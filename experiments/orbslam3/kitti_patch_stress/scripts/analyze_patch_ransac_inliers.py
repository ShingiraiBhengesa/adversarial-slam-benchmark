#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np


def patch_box(img_h, img_w, area_fraction, location):
    patch_area = img_h * img_w * area_fraction
    side = int(round(math.sqrt(patch_area)))
    patch_h = max(1, min(side, img_h))
    patch_w = max(1, min(side, img_w))
    margin_x = int(0.05 * img_w)
    margin_y = int(0.05 * img_h)

    if location == "center":
        x0 = (img_w - patch_w) // 2
        y0 = (img_h - patch_h) // 2
    elif location == "bottom_right":
        x0 = img_w - patch_w - margin_x
        y0 = img_h - patch_h - margin_y
    elif location == "bottom_left":
        x0 = margin_x
        y0 = img_h - patch_h - margin_y
    elif location == "top_right":
        x0 = img_w - patch_w - margin_x
        y0 = margin_y
    elif location == "top_left":
        x0 = margin_x
        y0 = margin_y
    else:
        raise ValueError(location)

    return x0, y0, patch_w, patch_h


def inside_patch(kp, box):
    x0, y0, w, h = box
    x, y = kp.pt
    return x0 <= x < x0 + w and y0 <= y < y0 + h


def summarize(vals):
    vals = np.asarray(vals, dtype=float)
    if len(vals) == 0:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": float(vals.mean()),
        "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
        "min": float(vals.min()),
        "max": float(vals.max()),
    }



def normalize_points_2d(pts):
    pts = np.asarray(pts, dtype=np.float64)
    centroid = pts.mean(axis=0)
    centered = pts - centroid
    mean_dist = np.mean(np.linalg.norm(centered, axis=1))
    scale = np.sqrt(2.0) / mean_dist if mean_dist > 1e-12 else 1.0

    T = np.array([
        [scale, 0.0, -scale * centroid[0]],
        [0.0, scale, -scale * centroid[1]],
        [0.0, 0.0, 1.0],
    ], dtype=np.float64)

    pts_h = np.column_stack([pts, np.ones(len(pts))])
    pts_n = (T @ pts_h.T).T
    return pts_n, T


def estimate_fundamental_8point(pts0, pts1):
    if len(pts0) < 8:
        return None

    p0, T0 = normalize_points_2d(pts0)
    p1, T1 = normalize_points_2d(pts1)

    x0, y0 = p0[:, 0], p0[:, 1]
    x1, y1 = p1[:, 0], p1[:, 1]

    A = np.column_stack([
        x1 * x0, x1 * y0, x1,
        y1 * x0, y1 * y0, y1,
        x0, y0, np.ones(len(p0)),
    ])

    try:
        _, _, vh = np.linalg.svd(A)
        F = vh[-1].reshape(3, 3)

        # enforce rank 2
        u, s, vh = np.linalg.svd(F)
        s[-1] = 0.0
        F_rank2 = u @ np.diag(s) @ vh

        F_denorm = T1.T @ F_rank2 @ T0
        norm = np.linalg.norm(F_denorm)
        return F_denorm / norm if norm > 1e-12 else F_denorm
    except np.linalg.LinAlgError:
        return None


def sampson_error_px(F, pts0, pts1):
    pts0_h = np.column_stack([pts0, np.ones(len(pts0))])
    pts1_h = np.column_stack([pts1, np.ones(len(pts1))])

    Fx0 = (F @ pts0_h.T).T
    Ftx1 = (F.T @ pts1_h.T).T
    x1tFx0 = np.sum(pts1_h * Fx0, axis=1)

    denom = Fx0[:, 0] ** 2 + Fx0[:, 1] ** 2 + Ftx1[:, 0] ** 2 + Ftx1[:, 1] ** 2
    denom = np.maximum(denom, 1e-12)

    return np.sqrt((x1tFx0 ** 2) / denom)


def ransac_fundamental_numpy(pts0, pts1, threshold_px, max_iters=300, seed=0):
    pts0 = np.asarray(pts0, dtype=np.float64)
    pts1 = np.asarray(pts1, dtype=np.float64)

    n = len(pts0)
    if n < 8:
        return None, np.zeros(n, dtype=bool)

    rng = np.random.default_rng(seed)
    best_mask = np.zeros(n, dtype=bool)
    best_count = 0

    for _ in range(max_iters):
        sample = rng.choice(n, size=8, replace=False)
        F = estimate_fundamental_8point(pts0[sample], pts1[sample])
        if F is None:
            continue

        err = sampson_error_px(F, pts0, pts1)
        mask = err <= threshold_px
        count = int(mask.sum())

        if count > best_count:
            best_count = count
            best_mask = mask

    if best_count >= 8:
        F_refined = estimate_fundamental_8point(pts0[best_mask], pts1[best_mask])
        return F_refined, best_mask

    return None, best_mask

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True, type=Path)
    ap.add_argument("--location", required=True,
                    choices=["center", "bottom_right", "bottom_left", "top_right", "top_left"])
    ap.add_argument("--area-fraction", type=float, default=0.05)
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--pair-step", type=int, default=1)
    ap.add_argument("--nfeatures", type=int, default=2000)
    ap.add_argument("--max-hamming", type=int, default=50)
    ap.add_argument("--ransac-threshold", type=float, default=1.0)
    ap.add_argument("--ransac-iters", type=int, default=100)
    ap.add_argument("--max-ransac-matches", type=int, default=300)
    ap.add_argument("--max-pairs", type=int, default=0)
    ap.add_argument("--output-json", required=True, type=Path)
    args = ap.parse_args()

    images = sorted((args.sequence / "image_0").glob("*.png"))
    if not images:
        raise FileNotFoundError(args.sequence / "image_0")

    orb = cv2.ORB_create(nfeatures=args.nfeatures)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    records = []
    patch_inlier_fracs = []
    patch_inlier_counts = []
    total_inlier_counts = []

    for idx in range(0, len(images) - args.pair_step, args.stride):
        if args.max_pairs > 0 and len(records) >= args.max_pairs:
            break
        img0 = cv2.imread(str(images[idx]), cv2.IMREAD_GRAYSCALE)
        img1 = cv2.imread(str(images[idx + args.pair_step]), cv2.IMREAD_GRAYSCALE)

        if img0 is None or img1 is None:
            continue

        h, w = img0.shape[:2]
        box = patch_box(h, w, args.area_fraction, args.location)

        kp0, desc0 = orb.detectAndCompute(img0, None)
        kp1, desc1 = orb.detectAndCompute(img1, None)
        kp0 = kp0 or []
        kp1 = kp1 or []

        if desc0 is None or desc1 is None:
            continue

        matches = [m for m in bf.match(desc0, desc1) if m.distance <= args.max_hamming]

        if len(matches) < 8:
            continue

        pts0 = np.ascontiguousarray([kp0[m.queryIdx].pt for m in matches], dtype=np.float32)
        pts1 = np.ascontiguousarray([kp1[m.trainIdx].pt for m in matches], dtype=np.float32)
        patch_match_flags = np.array([inside_patch(kp0[m.queryIdx], box) for m in matches], dtype=bool)

        rng = np.random.default_rng(12345 + idx)
        if len(matches) > args.max_ransac_matches:
            sample_idx = rng.choice(len(matches), size=args.max_ransac_matches, replace=False)
        else:
            sample_idx = np.arange(len(matches))

        F, _ = ransac_fundamental_numpy(
            pts0[sample_idx],
            pts1[sample_idx],
            threshold_px=float(args.ransac_threshold),
            max_iters=int(args.ransac_iters),
            seed=12345 + idx,
        )

        if F is None:
            continue

        err = sampson_error_px(F, pts0, pts1)
        mask = err <= float(args.ransac_threshold)
        total_inliers = int(mask.sum())
        patch_matches = int(patch_match_flags.sum())
        patch_inliers = int(np.logical_and(mask, patch_match_flags).sum())

        patch_inlier_frac_of_patch_matches = patch_inliers / patch_matches if patch_matches else 0.0
        patch_inlier_frac_of_all_inliers = patch_inliers / total_inliers if total_inliers else 0.0

        records.append({
            "frame_index": idx,
            "matches_total": len(matches),
            "inliers_total": total_inliers,
            "patch_matches": patch_matches,
            "patch_inliers": patch_inliers,
            "patch_inlier_frac_of_patch_matches": patch_inlier_frac_of_patch_matches,
            "patch_inlier_frac_of_all_inliers": patch_inlier_frac_of_all_inliers,
        })

        patch_inlier_fracs.append(patch_inlier_frac_of_all_inliers)
        patch_inlier_counts.append(patch_inliers)
        total_inlier_counts.append(total_inliers)

    result = {
        "sequence": str(args.sequence),
        "location": args.location,
        "area_fraction": args.area_fraction,
        "stride": args.stride,
        "pair_step": args.pair_step,
        "nfeatures": args.nfeatures,
        "max_hamming": args.max_hamming,
        "ransac_threshold": args.ransac_threshold,
        "num_pairs_analyzed": len(records),
        "total_inliers": summarize(total_inlier_counts),
        "patch_inliers": summarize(patch_inlier_counts),
        "patch_inlier_fraction_of_all_inliers": summarize(patch_inlier_fracs),
        "records": records,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

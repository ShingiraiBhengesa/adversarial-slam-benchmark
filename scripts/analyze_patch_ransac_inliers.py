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

        pts0 = np.asarray([kp0[m.queryIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
        pts1 = np.asarray([kp1[m.trainIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)

        F, mask = cv2.findFundamentalMat(
            pts0,
            pts1,
            cv2.FM_RANSAC,
            args.ransac_threshold,
            0.99,
            2000,
        )

        if mask is None:
            continue

        mask = mask.ravel().astype(bool)
        total_inliers = int(mask.sum())

        patch_match_flags = np.array([inside_patch(kp0[m.queryIdx], box) for m in matches], dtype=bool)
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

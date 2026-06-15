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

    x0 = max(0, min(x0, img_w - patch_w))
    y0 = max(0, min(y0, img_h - patch_h))
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


def detect_orb(orb, img_path):
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise RuntimeError(f"could not read {img_path}")
    kps, desc = orb.detectAndCompute(img, None)
    return img, kps or [], desc


def good_cross_matches(desc_a, desc_b, max_hamming):
    if desc_a is None or desc_b is None or len(desc_a) == 0 or len(desc_b) == 0:
        return []
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc_a, desc_b)
    return [m for m in matches if m.distance <= max_hamming]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True, type=Path)
    ap.add_argument("--area-fraction", required=True, type=float)
    ap.add_argument("--location", required=True,
                    choices=["center", "bottom_right", "bottom_left", "top_right", "top_left"])
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--pair-step", type=int, default=1)
    ap.add_argument("--nfeatures", type=int, default=2000)
    ap.add_argument("--max-hamming", type=int, default=50)
    ap.add_argument("--output-json", required=True, type=Path)
    args = ap.parse_args()

    left = sorted((args.sequence / "image_0").glob("*.png"))
    right = sorted((args.sequence / "image_1").glob("*.png"))

    if not left:
        raise FileNotFoundError(args.sequence / "image_0")
    if not right:
        raise FileNotFoundError(args.sequence / "image_1")

    orb = cv2.ORB_create(nfeatures=args.nfeatures)

    temporal_patch_match_fracs = []
    temporal_patch_displacements = []
    stereo_patch_match_fracs = []
    stereo_patch_disparities = []

    records = []

    for idx in range(0, min(len(left), len(right)) - args.pair_step, args.stride):
        img_l0, kp_l0, desc_l0 = detect_orb(orb, left[idx])
        _, kp_l1, desc_l1 = detect_orb(orb, left[idx + args.pair_step])
        _, kp_r0, desc_r0 = detect_orb(orb, right[idx])

        h, w = img_l0.shape[:2]
        box = patch_box(h, w, args.area_fraction, args.location)

        patch_indices = [i for i, kp in enumerate(kp_l0) if inside_patch(kp, box)]
        patch_index_set = set(patch_indices)

        temp_matches = good_cross_matches(desc_l0, desc_l1, args.max_hamming)
        temp_patch = [m for m in temp_matches if m.queryIdx in patch_index_set]

        stereo_matches = good_cross_matches(desc_l0, desc_r0, args.max_hamming)
        stereo_patch = [m for m in stereo_matches if m.queryIdx in patch_index_set]

        temp_disp = []
        for m in temp_patch:
            x0, y0 = kp_l0[m.queryIdx].pt
            x1, y1 = kp_l1[m.trainIdx].pt
            temp_disp.append(math.hypot(x1 - x0, y1 - y0))

        stereo_disp = []
        for m in stereo_patch:
            xl, yl = kp_l0[m.queryIdx].pt
            xr, yr = kp_r0[m.trainIdx].pt
            stereo_disp.append(xl - xr)

        temp_frac = len(temp_patch) / len(temp_matches) if temp_matches else 0.0
        stereo_frac = len(stereo_patch) / len(stereo_matches) if stereo_matches else 0.0

        temporal_patch_match_fracs.append(temp_frac)
        stereo_patch_match_fracs.append(stereo_frac)
        temporal_patch_displacements.extend(temp_disp)
        stereo_patch_disparities.extend(stereo_disp)

        records.append({
            "frame_index": idx,
            "temporal_matches_total": len(temp_matches),
            "temporal_patch_matches": len(temp_patch),
            "temporal_patch_match_fraction": temp_frac,
            "temporal_patch_displacement_median_px": float(np.median(temp_disp)) if temp_disp else None,
            "stereo_matches_total": len(stereo_matches),
            "stereo_patch_matches": len(stereo_patch),
            "stereo_patch_match_fraction": stereo_frac,
            "stereo_patch_disparity_median_px": float(np.median(stereo_disp)) if stereo_disp else None,
        })

    result = {
        "sequence": str(args.sequence),
        "location": args.location,
        "area_fraction": args.area_fraction,
        "stride": args.stride,
        "pair_step": args.pair_step,
        "nfeatures": args.nfeatures,
        "max_hamming": args.max_hamming,
        "num_frames_analyzed": len(records),
        "temporal_patch_match_fraction": summarize(temporal_patch_match_fracs),
        "temporal_patch_displacement_px": summarize(temporal_patch_displacements),
        "stereo_patch_match_fraction": summarize(stereo_patch_match_fracs),
        "stereo_patch_disparity_px": summarize(stereo_patch_disparities),
        "records": records,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

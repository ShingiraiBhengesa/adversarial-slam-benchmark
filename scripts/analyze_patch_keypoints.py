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
        raise ValueError(f"Unknown location: {location}")

    x0 = max(0, min(x0, img_w - patch_w))
    y0 = max(0, min(y0, img_h - patch_h))
    return x0, y0, patch_w, patch_h


def summarize(vals):
    vals = np.asarray(vals, dtype=float)
    return {
        "mean": float(vals.mean()) if len(vals) else 0.0,
        "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
        "min": float(vals.min()) if len(vals) else 0.0,
        "max": float(vals.max()) if len(vals) else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True, type=Path)
    ap.add_argument("--area-fraction", required=True, type=float)
    ap.add_argument("--location", required=True,
                    choices=["center", "bottom_right", "bottom_left", "top_right", "top_left"])
    ap.add_argument("--camera", default="image_0", choices=["image_0", "image_1"])
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--nfeatures", type=int, default=2000)
    ap.add_argument("--output-json", required=True, type=Path)
    args = ap.parse_args()

    img_dir = args.sequence / args.camera
    images = sorted(img_dir.glob("*.png"))
    if not images:
        raise FileNotFoundError(f"No PNGs found in {img_dir}")

    orb = cv2.ORB_create(nfeatures=args.nfeatures)

    records = []
    total_counts = []
    patch_counts = []
    outside_counts = []
    patch_fracs = []

    for idx, path in enumerate(images):
        if idx % args.stride != 0:
            continue

        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError(f"Could not read {path}")

        h, w = img.shape[:2]
        x0, y0, pw, ph = patch_box(h, w, args.area_fraction, args.location)

        kps = orb.detect(img, None)
        total = len(kps)

        inside = 0
        for kp in kps:
            x, y = kp.pt
            if x0 <= x < x0 + pw and y0 <= y < y0 + ph:
                inside += 1

        outside = total - inside
        frac = inside / total if total else 0.0

        records.append({
            "frame_index": idx,
            "image": path.name,
            "total_keypoints": total,
            "patch_keypoints": inside,
            "outside_keypoints": outside,
            "patch_keypoint_fraction": frac,
        })

        total_counts.append(total)
        patch_counts.append(inside)
        outside_counts.append(outside)
        patch_fracs.append(frac)

    result = {
        "sequence": str(args.sequence),
        "camera": args.camera,
        "area_fraction": args.area_fraction,
        "location": args.location,
        "stride": args.stride,
        "nfeatures": args.nfeatures,
        "num_frames_analyzed": len(records),
        "patch_box": {
            "x": x0,
            "y": y0,
            "w": pw,
            "h": ph,
        },
        "total_keypoints": summarize(total_counts),
        "patch_keypoints": summarize(patch_counts),
        "outside_keypoints": summarize(outside_counts),
        "patch_keypoint_fraction": summarize(patch_fracs),
        "records": records,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

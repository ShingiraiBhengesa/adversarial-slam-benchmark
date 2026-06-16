#!/usr/bin/env python3
import argparse
import json
import math
import statistics as stats
from pathlib import Path

import cv2


def patch_rect(width, height, area_fraction, location):
    patch_area = area_fraction * width * height
    side = int(round(math.sqrt(patch_area)))
    side = max(1, min(side, width, height))

    if location == "top_left":
        x0, y0 = 0, 0
    elif location == "top_right":
        x0, y0 = width - side, 0
    elif location == "bottom_left":
        x0, y0 = 0, height - side
    elif location == "bottom_right":
        x0, y0 = width - side, height - side
    elif location == "center":
        x0, y0 = (width - side) // 2, (height - side) // 2
    else:
        raise ValueError(f"Unsupported location: {location}")

    return x0, y0, x0 + side, y0 + side


def describe(vals):
    vals = list(vals)
    if not vals:
        return {"count": 0, "mean": None, "std": None, "min": None, "max": None}
    return {
        "count": len(vals),
        "mean": float(stats.mean(vals)),
        "std": float(stats.stdev(vals)) if len(vals) > 1 else 0.0,
        "min": float(min(vals)),
        "max": float(max(vals)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True, type=Path)
    ap.add_argument("--area-fraction", required=True, type=float)
    ap.add_argument("--location", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--nfeatures", type=int, default=2000)
    ap.add_argument("--output-json", required=True, type=Path)
    args = ap.parse_args()

    image_dir = args.sequence / "image_0"
    images = sorted(image_dir.glob("*.png"))
    if not images:
        raise SystemExit(f"No PNG images found in {image_dir}")

    first = cv2.imread(str(images[0]), cv2.IMREAD_GRAYSCALE)
    if first is None:
        raise SystemExit(f"Could not read {images[0]}")

    h, w = first.shape[:2]
    x0, y0, x1, y1 = patch_rect(w, h, args.area_fraction, args.location)

    orb = cv2.ORB_create(nfeatures=args.nfeatures)

    records = []
    for idx, img_path in enumerate(images):
        if idx % args.stride != 0:
            continue

        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        kps = orb.detect(img, None)
        total = len(kps)

        patch_kps = 0
        for kp in kps:
            x, y = kp.pt
            if x0 <= x < x1 and y0 <= y < y1:
                patch_kps += 1

        outside = total - patch_kps
        frac = patch_kps / total if total else 0.0

        records.append({
            "frame_index": idx,
            "image": img_path.name,
            "total_keypoints": total,
            "patch_keypoints": patch_kps,
            "outside_keypoints": outside,
            "patch_keypoint_fraction": frac,
        })

    out = {
        "label": args.label,
        "sequence": str(args.sequence),
        "image_dir": str(image_dir),
        "area_fraction": args.area_fraction,
        "location": args.location,
        "stride": args.stride,
        "nfeatures": args.nfeatures,
        "image_width": w,
        "image_height": h,
        "patch_rect_xyxy": [x0, y0, x1, y1],
        "num_sampled_frames": len(records),
        "total_keypoints": describe(r["total_keypoints"] for r in records),
        "patch_keypoints": describe(r["patch_keypoints"] for r in records),
        "outside_keypoints": describe(r["outside_keypoints"] for r in records),
        "patch_keypoint_fraction": describe(r["patch_keypoint_fraction"] for r in records),
        "records": records,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "label": args.label,
        "output": str(args.output_json),
        "patch_keypoints_mean": out["patch_keypoints"]["mean"],
        "patch_keypoint_fraction_mean": out["patch_keypoint_fraction"]["mean"],
        "sampled_frames": len(records),
    }, indent=2))


if __name__ == "__main__":
    main()

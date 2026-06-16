#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_gray(path: Path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img


def patch_rect(width, height, area_fraction, location):
    side = int(round((width * height * area_fraction) ** 0.5))
    side = max(1, min(side, width, height))
    pw = ph = side

    if location == "top_left":
        x0, y0 = 0, 0
    elif location == "top_right":
        x0, y0 = width - pw, 0
    elif location == "bottom_left":
        x0, y0 = 0, height - ph
    elif location == "bottom_right":
        x0, y0 = width - pw, height - ph
    elif location == "center":
        x0, y0 = (width - pw) // 2, (height - ph) // 2
    else:
        raise ValueError(f"Unsupported location: {location}")

    return x0, y0, pw, ph


def detect_keypoints(img):
    orb = cv2.ORB_create(nfeatures=2000)
    return orb.detect(img, None)


def split_keypoints(kps, rect):
    x0, y0, pw, ph = rect
    inside = []
    outside = []

    for kp in kps:
        x, y = kp.pt
        if x0 <= x < x0 + pw and y0 <= y < y0 + ph:
            inside.append(kp)
        else:
            outside.append(kp)

    return inside, outside


def plot_panel(ax, img, kps, rect, title):
    inside, outside = split_keypoints(kps, rect)
    x0, y0, pw, ph = rect

    ax.imshow(img, cmap="gray")

    if outside:
        xs = [kp.pt[0] for kp in outside]
        ys = [kp.pt[1] for kp in outside]
        ax.scatter(xs, ys, s=3, alpha=0.35, label="outside patch")

    if inside:
        xs = [kp.pt[0] for kp in inside]
        ys = [kp.pt[1] for kp in inside]
        ax.scatter(xs, ys, s=6, alpha=0.9, label="inside patch")

    box = plt.Rectangle((x0, y0), pw, ph, fill=False, linewidth=2)
    ax.add_patch(box)

    frac = len(inside) / len(kps) if kps else 0.0
    ax.set_title(f"{title}\npatch KP: {len(inside)}/{len(kps)} = {frac:.3f}")
    ax.axis("off")

    return {
        "title": title,
        "total_keypoints": len(kps),
        "patch_keypoints": len(inside),
        "outside_keypoints": len(outside),
        "patch_keypoint_fraction": frac,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-index", type=int, required=True)
    ap.add_argument("--area-fraction", type=float, required=True)
    ap.add_argument("--location", required=True)
    ap.add_argument("--clean-sequence", required=True, type=Path)
    ap.add_argument("--black-sequence", required=True, type=Path)
    ap.add_argument("--checkerboard-sequence", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    frame = f"{args.frame_index:06d}.png"

    items = [
        ("clean", args.clean_sequence / "image_0" / frame),
        ("black patch", args.black_sequence / "image_0" / frame),
        ("checkerboard patch", args.checkerboard_sequence / "image_0" / frame),
    ]

    imgs = [(label, load_gray(path), path) for label, path in items]
    h, w = imgs[0][1].shape[:2]
    rect = patch_rect(w, h, args.area_fraction, args.location)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    summary = {
        "frame_index": args.frame_index,
        "frame": frame,
        "area_fraction": args.area_fraction,
        "location": args.location,
        "patch_rect_xywh": rect,
        "conditions": [],
    }

    for ax, (label, img, path) in zip(axes, imgs):
        kps = detect_keypoints(img)
        result = plot_panel(ax, img, kps, rect, label)
        result["image_path"] = str(path)
        summary["conditions"].append(result)

    handles, labels = axes[-1].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=2)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.savefig(args.output, dpi=220)

    json_out = args.output.with_suffix(".json")
    json_out.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"saved {args.output}")
    print(f"saved {json_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

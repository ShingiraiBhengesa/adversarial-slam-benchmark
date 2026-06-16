#!/usr/bin/env python3
import argparse
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


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

    return x0, y0, x0 + patch_w, y0 + patch_h


def inside(pt, box):
    x, y = pt
    x0, y0, x1, y1 = box
    return x0 <= x < x1 and y0 <= y < y1


def draw_overlay(image_path, location, area_fraction, label, out_path, nfeatures=2000):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    gray = np.array(img.convert("L"))

    h, w = gray.shape
    box = patch_box(h, w, area_fraction, location)

    orb = cv2.ORB_create(nfeatures=nfeatures)
    kps = orb.detect(gray, None)

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 28)
    except Exception:
        font = ImageFont.load_default()

    # Patch box
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=4)

    patch_count = 0
    outside_count = 0

    for kp in kps:
        x, y = kp.pt
        if inside((x, y), box):
            patch_count += 1
            color = (255, 0, 0)
        else:
            outside_count += 1
            color = (0, 255, 0)

        r = 2
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

    text = f"{label} | total={len(kps)} patch={patch_count} outside={outside_count}"
    draw.rectangle([10, 10, min(w-10, 980), 52], fill=(0, 0, 0))
    draw.text((20, 17), text, fill=(255, 255, 255), font=font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True, type=Path)
    ap.add_argument("--location", required=True)
    ap.add_argument("--area-fraction", type=float, default=0.05)
    ap.add_argument("--frames", nargs="+", type=int, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()

    for frame in args.frames:
        image_path = args.sequence / "image_0" / f"{frame:06d}.png"
        out_path = args.output_dir / f"{args.label}_{frame:06d}_features.png"
        draw_overlay(image_path, args.location, args.area_fraction, f"{args.label} frame {frame}", out_path)
        print(out_path)


if __name__ == "__main__":
    main()

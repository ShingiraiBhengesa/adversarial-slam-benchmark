#!/usr/bin/env python3
import argparse
import math
from pathlib import Path

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


def blur5(img):
    kernel = np.array([1, 4, 6, 4, 1], dtype=np.float64) / 16.0
    tmp = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=1, arr=img)
    out = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=0, arr=tmp)
    return out


def harris_points(gray, nfeatures=2000, min_dist=4):
    gray = gray.astype(np.float64) / 255.0

    gy, gx = np.gradient(gray)
    ixx = blur5(gx * gx)
    iyy = blur5(gy * gy)
    ixy = blur5(gx * gy)

    k = 0.04
    det = ixx * iyy - ixy * ixy
    trace = ixx + iyy
    response = det - k * trace * trace

    # Ignore weak/negative responses and borders.
    border = 8
    response[:border, :] = -np.inf
    response[-border:, :] = -np.inf
    response[:, :border] = -np.inf
    response[:, -border:] = -np.inf

    flat = response.ravel()
    finite = np.isfinite(flat)
    if not finite.any():
        return []

    # Start from more candidates than needed, then greedy non-max suppression.
    candidate_count = min(len(flat), nfeatures * 20)
    idxs = np.argpartition(flat, -candidate_count)[-candidate_count:]
    idxs = idxs[np.argsort(flat[idxs])[::-1]]

    h, w = response.shape
    selected = []
    occupied = np.zeros((h, w), dtype=bool)

    for idx in idxs:
        y, x = divmod(int(idx), w)
        if not np.isfinite(response[y, x]) or response[y, x] <= 0:
            continue

        y0 = max(0, y - min_dist)
        y1 = min(h, y + min_dist + 1)
        x0 = max(0, x - min_dist)
        x1 = min(w, x + min_dist + 1)

        if occupied[y0:y1, x0:x1].any():
            continue

        selected.append((float(x), float(y)))
        occupied[y0:y1, x0:x1] = True

        if len(selected) >= nfeatures:
            break

    return selected


def draw_overlay(image_path, location, area_fraction, label, out_path, nfeatures=2000):
    img = Image.open(image_path).convert("RGB")
    gray = np.array(img.convert("L"), dtype=np.uint8)

    h, w = gray.shape
    box = patch_box(h, w, area_fraction, location)
    pts = harris_points(gray, nfeatures=nfeatures)

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 28)
    except Exception:
        font = ImageFont.load_default()

    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=4)

    patch_count = 0
    outside_count = 0

    for x, y in pts:
        if inside((x, y), box):
            patch_count += 1
            color = (255, 0, 0)
        else:
            outside_count += 1
            color = (0, 255, 0)

        r = 2
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    text = f"{label} | Harris total={len(pts)} patch={patch_count} outside={outside_count}"
    draw.rectangle([10, 10, min(w - 10, 1080), 52], fill=(0, 0, 0))
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
    ap.add_argument("--nfeatures", type=int, default=2000)
    args = ap.parse_args()

    for frame in args.frames:
        image_path = args.sequence / "image_0" / f"{frame:06d}.png"
        out_path = args.output_dir / f"{args.label}_{frame:06d}_features.png"
        draw_overlay(
            image_path=image_path,
            location=args.location,
            area_fraction=args.area_fraction,
            label=f"{args.label} frame {frame}",
            out_path=out_path,
            nfeatures=args.nfeatures,
        )
        print(out_path)


if __name__ == "__main__":
    main()

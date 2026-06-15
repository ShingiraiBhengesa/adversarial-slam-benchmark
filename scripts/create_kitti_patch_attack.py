#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np


def make_patch(h: int, w: int, mode: str) -> np.ndarray:
    if mode == "black":
        return np.zeros((h, w), dtype=np.uint8)

    if mode == "white":
        return np.full((h, w), 255, dtype=np.uint8)

    if mode == "checkerboard":
        tile = max(4, min(h, w) // 12)
        yy, xx = np.indices((h, w))
        patch = ((xx // tile + yy // tile) % 2) * 255
        return patch.astype(np.uint8)

    if mode == "random":
        rng = np.random.default_rng(0)
        return rng.integers(0, 256, size=(h, w), dtype=np.uint8)

    raise ValueError(f"Unknown patch mode: {mode}")


def patch_location(img_h: int, img_w: int, patch_h: int, patch_w: int, location: str):
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
    return x0, y0


def overlay_patch(img: np.ndarray, area_fraction: float, location: str, mode: str) -> np.ndarray:
    img_h, img_w = img.shape[:2]
    patch_area = img_h * img_w * area_fraction
    side = int(round(np.sqrt(patch_area)))
    patch_h = max(1, min(side, img_h))
    patch_w = max(1, min(side, img_w))

    x0, y0 = patch_location(img_h, img_w, patch_h, patch_w, location)
    patch = make_patch(patch_h, patch_w, mode)

    out = img.copy()
    out[y0:y0 + patch_h, x0:x0 + patch_w] = patch
    return out


def process_dir(src_img_dir: Path, dst_img_dir: Path, area_fraction: float, location: str, mode: str):
    dst_img_dir.mkdir(parents=True, exist_ok=True)
    images = sorted(src_img_dir.glob("*.png"))

    if not images:
        raise FileNotFoundError(f"No PNG images found in {src_img_dir}")

    for i, src in enumerate(images):
        img = cv2.imread(str(src), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError(f"Could not read image: {src}")

        patched = overlay_patch(img, area_fraction, location, mode)
        dst = dst_img_dir / src.name
        ok = cv2.imwrite(str(dst), patched)
        if not ok:
            raise RuntimeError(f"Could not write image: {dst}")

        if i % 500 == 0:
            print(f"processed {i}/{len(images)}: {src.name}")

    print(f"processed {len(images)} images into {dst_img_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-sequence", required=True, type=Path)
    ap.add_argument("--output-sequence", required=True, type=Path)
    ap.add_argument("--area-fraction", type=float, required=True)
    ap.add_argument("--location", default="bottom_right",
                    choices=["center", "bottom_right", "bottom_left", "top_right", "top_left"])
    ap.add_argument("--mode", default="checkerboard",
                    choices=["black", "white", "checkerboard", "random"])
    ap.add_argument("--both-cameras", action="store_true")
    args = ap.parse_args()

    if not (0.0 < args.area_fraction < 1.0):
        raise ValueError("--area-fraction must be between 0 and 1")

    src = args.source_sequence
    dst = args.output_sequence

    if dst.exists():
        raise FileExistsError(f"Output sequence already exists: {dst}")

    dst.mkdir(parents=True)

    for name in ["calib.txt", "times.txt"]:
        shutil.copy2(src / name, dst / name)

    process_dir(src / "image_0", dst / "image_0", args.area_fraction, args.location, args.mode)

    if args.both_cameras:
        process_dir(src / "image_1", dst / "image_1", args.area_fraction, args.location, args.mode)
    else:
        shutil.copytree(src / "image_1", dst / "image_1")

    metadata = {
        "source_sequence": str(src),
        "output_sequence": str(dst),
        "area_fraction": args.area_fraction,
        "location": args.location,
        "mode": args.mode,
        "both_cameras": args.both_cameras,
        "note": "Digital image-plane patch stress test; not a physically accurate stereo patch.",
    }

    import json
    (dst / "patch_attack_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()

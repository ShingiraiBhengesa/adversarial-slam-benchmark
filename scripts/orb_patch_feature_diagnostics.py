#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np


def read_image(path: Path):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img


def infer_patch_bbox(clean_img, attack_img, min_diff=10):
    diff = cv2.absdiff(clean_img, attack_img)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    mask = gray > min_diff

    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None

    x1, x2 = int(xs.min()), int(xs.max()) + 1
    y1, y2 = int(ys.min()), int(ys.max()) + 1
    return x1, y1, x2, y2


def count_inside_patch(keypoints, bbox):
    if bbox is None:
        return 0

    x1, y1, x2, y2 = bbox
    count = 0
    for kp in keypoints:
        x, y = kp.pt
        if x1 <= x < x2 and y1 <= y < y2:
            count += 1
    return count


def draw_overlay(img, keypoints, bbox, output_path: Path):
    out = cv2.drawKeypoints(
        img,
        keypoints,
        None,
        flags=cv2.DrawMatchesFlags_DRAW_RICH_KEYPOINTS,
    )

    if bbox is not None:
        x1, y1, x2, y2 = bbox
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 0, 255), 3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", required=True, help="Frame id, e.g. 000120")
    parser.add_argument("--clean", required=True, type=Path)
    parser.add_argument("--black10", required=True, type=Path)
    parser.add_argument("--checkerboard5", required=True, type=Path)
    parser.add_argument("--checkerboard10", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--nfeatures", type=int, default=2000)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    clean_img = read_image(args.clean)

    conditions = [
        ("clean_reference_top_left_10pct_region", args.clean),
        ("black_10pct_top_left", args.black10),
        ("checkerboard_5pct_top_left", args.checkerboard5),
        ("checkerboard_10pct_top_left", args.checkerboard10),
    ]

    # Use black 10% patch bbox as the reference region for the clean image.
    black_img = read_image(args.black10)
    clean_reference_bbox = infer_patch_bbox(clean_img, black_img)

    orb = cv2.ORB_create(nfeatures=args.nfeatures)

    rows = []

    for name, image_path in conditions:
        img = read_image(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        keypoints = orb.detect(gray, None)

        if name.startswith("clean"):
            bbox = clean_reference_bbox
        else:
            bbox = infer_patch_bbox(clean_img, img)

        patch_keypoints = count_inside_patch(keypoints, bbox)
        total_keypoints = len(keypoints)

        h, w = img.shape[:2]
        image_area = h * w

        if bbox is None:
            patch_area = 0
            patch_area_fraction = 0.0
        else:
            x1, y1, x2, y2 = bbox
            patch_area = (x2 - x1) * (y2 - y1)
            patch_area_fraction = patch_area / image_area

        patch_keypoint_fraction = (
            patch_keypoints / total_keypoints if total_keypoints else 0.0
        )

        patch_density = patch_keypoints / patch_area if patch_area else 0.0
        image_density = total_keypoints / image_area if image_area else 0.0
        density_ratio = patch_density / image_density if image_density else 0.0

        overlay_path = args.outdir / f"{args.frame}_{name}_orb_keypoints.png"
        draw_overlay(img, keypoints, bbox, overlay_path)

        rows.append(
            {
                "frame": args.frame,
                "condition": name,
                "image": str(image_path),
                "overlay": str(overlay_path),
                "total_keypoints": total_keypoints,
                "patch_keypoints": patch_keypoints,
                "patch_keypoint_fraction": patch_keypoint_fraction,
                "patch_area_fraction": patch_area_fraction,
                "patch_density_keypoints_per_pixel": patch_density,
                "image_density_keypoints_per_pixel": image_density,
                "patch_to_image_density_ratio": density_ratio,
                "patch_bbox_xyxy": bbox,
            }
        )

    csv_path = args.outdir / f"{args.frame}_orb_patch_feature_diagnostics.csv"
    json_path = args.outdir / f"{args.frame}_orb_patch_feature_diagnostics.json"
    md_path = args.outdir / f"{args.frame}_orb_patch_feature_diagnostics.md"

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2) + "\n")

    lines = []
    lines.append(f"# ORB Patch Feature Diagnostics: KITTI frame {args.frame}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This diagnostic checks whether the checkerboard patch behaves like a feature-injection perturbation rather than simple occlusion."
    )
    lines.append("")
    lines.append("The analysis uses OpenCV ORB as a proxy diagnostic. It is not a direct dump of ORB-SLAM3's internal frontend state.")
    lines.append("")
    lines.append("## Keypoint count summary")
    lines.append("")
    lines.append("| Condition | Total ORB keypoints | Patch-region keypoints | % of keypoints in patch | Patch area % | Patch/image density ratio |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for r in rows:
        lines.append(
            f"| {r['condition']} | "
            f"{r['total_keypoints']} | "
            f"{r['patch_keypoints']} | "
            f"{100*r['patch_keypoint_fraction']:.2f}% | "
            f"{100*r['patch_area_fraction']:.2f}% | "
            f"{r['patch_to_image_density_ratio']:.2f} |"
        )

    lines.append("")
    lines.append("## Overlay figures")
    lines.append("")

    for r in rows:
        rel = Path(r["overlay"]).name
        lines.append(f"### {r['condition']}")
        lines.append("")
        lines.append(f"![{r['condition']}]({rel})")
        lines.append("")

    lines.append("## Interpretation guide")
    lines.append("")
    lines.append(
        "If the checkerboard mechanism is feature injection, the checkerboard rows should show a much higher patch-region keypoint fraction and density ratio than the clean or black-patch controls."
    )
    lines.append("")
    lines.append(
        "The black patch is expected to remove visual content, so it should not attract many ORB keypoints inside the patch. If its trajectory remains near baseline while the checkerboard trajectory fails, this supports the claim that failure is caused by injected high-texture structure rather than occlusion alone."
    )
    lines.append("")

    md_path.write_text("\n".join(lines))

    print(json.dumps(
        {
            "csv": str(csv_path),
            "json": str(json_path),
            "markdown": str(md_path),
            "num_conditions": len(rows),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()

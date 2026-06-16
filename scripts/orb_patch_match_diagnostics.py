#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np


def patch_box(img, area_fraction):
    h, w = img.shape[:2]
    # Square patch whose area matches the requested fraction of the full image.
    side = int(round((area_fraction * h * w) ** 0.5))
    side = min(side, w, h)
    return (0, 0, side, side)


def inside_box(pt, box):
    x, y = pt
    x0, y0, x1, y1 = box
    return x0 <= x < x1 and y0 <= y < y1


def load_gray(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(path)
    return img


def draw_matches(img1, kp1, img2, kp2, matches, box, out_path, max_draw=120):
    drawn = cv2.drawMatches(
        img1, kp1,
        img2, kp2,
        matches[:max_draw],
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )

    x0, y0, x1, y1 = box
    w = img1.shape[1]

    # Draw patch boxes on left and right images.
    cv2.rectangle(drawn, (x0, y0), (x1, y1), (0, 255, 255), 2)
    cv2.rectangle(drawn, (x0 + w, y0), (x1 + w, y1), (0, 255, 255), 2)

    cv2.imwrite(str(out_path), drawn)


def analyze_pair(condition, img1_path, img2_path, area_fraction, outdir, nfeatures):
    img1 = load_gray(img1_path)
    img2 = load_gray(img2_path)

    orb = cv2.ORB_create(nfeatures=nfeatures)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        matches = []
    else:
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        knn = matcher.knnMatch(des1, des2, k=2)

        matches = []
        for pair in knn:
            if len(pair) < 2:
                continue
            m, n = pair
            if m.distance < 0.75 * n.distance:
                matches.append(m)

        matches = sorted(matches, key=lambda m: m.distance)

    box = patch_box(img1, area_fraction)
    x0, y0, x1, y1 = box
    patch_area_fraction_actual = ((x1 - x0) * (y1 - y0)) / (img1.shape[0] * img1.shape[1])

    both_patch = 0
    either_patch = 0
    query_patch = 0
    train_patch = 0

    for m in matches:
        p1 = kp1[m.queryIdx].pt
        p2 = kp2[m.trainIdx].pt

        in1 = inside_box(p1, box)
        in2 = inside_box(p2, box)

        query_patch += int(in1)
        train_patch += int(in2)
        either_patch += int(in1 or in2)
        both_patch += int(in1 and in2)

    total = len(matches)
    both_frac = both_patch / total if total else 0.0
    either_frac = either_patch / total if total else 0.0

    density_ratio_both = both_frac / patch_area_fraction_actual if patch_area_fraction_actual else 0.0
    density_ratio_either = either_frac / patch_area_fraction_actual if patch_area_fraction_actual else 0.0

    out_img = outdir / f"{condition}_orb_matches.png"
    draw_matches(img1, kp1, img2, kp2, matches, box, out_img)

    return {
        "condition": condition,
        "image_1": str(img1_path),
        "image_2": str(img2_path),
        "nfeatures": nfeatures,
        "keypoints_frame1": len(kp1),
        "keypoints_frame2": len(kp2),
        "total_ratio_matches": total,
        "query_patch_matches": query_patch,
        "train_patch_matches": train_patch,
        "either_patch_matches": either_patch,
        "both_patch_matches": both_patch,
        "either_patch_match_fraction": either_frac,
        "both_patch_match_fraction": both_frac,
        "patch_area_fraction": patch_area_fraction_actual,
        "either_patch_density_ratio": density_ratio_either,
        "both_patch_density_ratio": density_ratio_both,
        "match_overlay": str(out_img),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame-a", required=True)
    ap.add_argument("--frame-b", required=True)
    ap.add_argument("--clean-dir", required=True)
    ap.add_argument("--black10-dir", required=True)
    ap.add_argument("--checkerboard5-dir", required=True)
    ap.add_argument("--checkerboard10-dir", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--nfeatures", type=int, default=5000)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("clean_reference_top_left_10pct_region", args.clean_dir, 0.10),
        ("black_10pct_top_left", args.black10_dir, 0.10),
        ("checkerboard_5pct_top_left", args.checkerboard5_dir, 0.05),
        ("checkerboard_10pct_top_left", args.checkerboard10_dir, 0.10),
    ]

    rows = []
    for condition, root, area in specs:
        root = Path(root)
        rows.append(
            analyze_pair(
                condition,
                root / f"{args.frame_a}.png",
                root / f"{args.frame_b}.png",
                area,
                outdir,
                args.nfeatures,
            )
        )

    csv_path = outdir / f"{args.frame_a}_{args.frame_b}_orb_match_diagnostics.csv"
    json_path = outdir / f"{args.frame_a}_{args.frame_b}_orb_match_diagnostics.json"
    md_path = outdir / f"{args.frame_a}_{args.frame_b}_orb_match_diagnostics.md"

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2))

    lines = []
    lines.append(f"# ORB Match Diagnostics: KITTI frames {args.frame_a} → {args.frame_b}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This diagnostic checks whether the checkerboard patch not only creates many ORB keypoints, but also attracts frame-to-frame descriptor matches.")
    lines.append("")
    lines.append("This uses OpenCV ORB + Hamming BF matching with Lowe ratio filtering as a proxy diagnostic. It is not a direct dump of ORB-SLAM3 internal matching.")
    lines.append("")
    lines.append("## Match summary")
    lines.append("")
    lines.append("| Condition | Matches | Either endpoint in patch | Both endpoints in patch | Either-patch density ratio | Both-patch density ratio |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(
            f"| {r['condition']} | "
            f"{r['total_ratio_matches']} | "
            f"{100*r['either_patch_match_fraction']:.2f}% | "
            f"{100*r['both_patch_match_fraction']:.2f}% | "
            f"{r['either_patch_density_ratio']:.2f} | "
            f"{r['both_patch_density_ratio']:.2f} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("If the checkerboard is causing feature/match injection, the checkerboard conditions should show a much higher fraction of matches involving the patch region than clean or black-patch controls.")
    lines.append("")
    lines.append("The strongest evidence is high both-endpoint patch matching: this means features inside the patch region in one frame are repeatedly matched to patch-region features in the next frame.")
    lines.append("")
    lines.append("## Overlay figures")
    lines.append("")
    for r in rows:
        lines.append(f"### {r['condition']}")
        lines.append("")
        lines.append(f"![{r['condition']}]({Path(r['match_overlay']).name})")
        lines.append("")

    md_path.write_text("\n".join(lines))

    print(json.dumps({
        "csv": str(csv_path),
        "json": str(json_path),
        "markdown": str(md_path),
        "num_conditions": len(rows),
    }, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attack-run", required=True, type=Path)
    ap.add_argument(
        "--baseline-summary",
        default=Path("results/baselines/orbslam3/kitti00_stereo/repeat_summary.json"),
        type=Path,
    )
    args = ap.parse_args()

    baseline = json.loads(args.baseline_summary.read_text())
    ate = json.loads((args.attack_run / "ate_metrics.json").read_text())
    seg = json.loads((args.attack_run / "kitti_segment_metrics.json").read_text())

    comparisons = [
        ("ATE RMSE (m)", ate["ate_rmse_m"], "ate_rmse_m"),
        ("ATE RMSE / path (%)", ate["ate_rmse_percent_of_path"], "ate_rmse_percent_of_path"),
        ("Translation drift (%)", seg["translation_error_percent_mean"], "segment_translation_error_percent_mean"),
        ("Rotation drift (deg/100m)", seg["rotation_error_deg_per_100m_mean"], "segment_rotation_error_deg_per_100m_mean"),
    ]

    print("=== ATTACK VS CLEAN BASELINE ===")
    print(f"Attack run: {args.attack_run}")
    print(f"Attack poses: {ate['num_est_poses']} / evaluated: {ate['num_evaluated_poses']}")
    print()

    for label, value, key in comparisons:
        mean = baseline[key]["mean"]
        std = baseline[key]["std"]
        delta = value - mean
        rel = 100.0 * delta / mean if mean else float("nan")
        z = delta / std if std else float("nan")

        print(label)
        print(f"  clean mean ± std: {mean:.6f} ± {std:.6f}")
        print(f"  attack:           {value:.6f}")
        print(f"  delta:            {delta:.6f}")
        print(f"  relative delta:   {rel:.2f}%")
        print(f"  z-score:          {z:.2f}")
        print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
import statistics as stats
from pathlib import Path


METRIC_MAP = {
    "ate_rmse_m": ("ate_metrics.json", "ate_rmse_m"),
    "ate_rmse_percent_of_path": ("ate_metrics.json", "ate_rmse_percent_of_path"),
    "segment_translation_error_percent_mean": ("kitti_segment_metrics.json", "translation_error_percent_mean"),
    "segment_rotation_error_deg_per_100m_mean": ("kitti_segment_metrics.json", "rotation_error_deg_per_100m_mean"),
}


def mean_std(vals):
    return {
        "mean": stats.mean(vals),
        "std": stats.stdev(vals) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attack-root", required=True, type=Path)
    ap.add_argument("--output-json", type=Path)
    args = ap.parse_args()

    run_dirs = sorted(args.attack_root.glob("run_*"))
    valid = []

    for run_dir in run_dirs:
        ate_path = run_dir / "ate_metrics.json"
        seg_path = run_dir / "kitti_segment_metrics.json"
        if not ate_path.exists() or not seg_path.exists():
            continue

        ate = json.loads(ate_path.read_text())
        seg = json.loads(seg_path.read_text())

        valid.append({
            "run_dir": str(run_dir),
            "num_est_poses": ate["num_est_poses"],
            "num_evaluated_poses": ate["num_evaluated_poses"],
            "ate_rmse_m": ate["ate_rmse_m"],
            "ate_rmse_percent_of_path": ate["ate_rmse_percent_of_path"],
            "segment_translation_error_percent_mean": seg["translation_error_percent_mean"],
            "segment_rotation_error_deg_per_100m_mean": seg["rotation_error_deg_per_100m_mean"],
            "num_segments_total": seg["num_segments_total"],
        })

    if not valid:
        raise SystemExit(f"No valid attack runs found under {args.attack_root}")

    summary = {
        "attack_root": str(args.attack_root),
        "num_valid_runs": len(valid),
        "runs": valid,
    }

    for key in [
        "ate_rmse_m",
        "ate_rmse_percent_of_path",
        "segment_translation_error_percent_mean",
        "segment_rotation_error_deg_per_100m_mean",
    ]:
        summary[key] = mean_std([float(r[key]) for r in valid])

    out = args.output_json or args.attack_root / "attack_repeat_summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

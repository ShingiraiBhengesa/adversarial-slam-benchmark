#!/usr/bin/env python3
import argparse
import json
import statistics as stats
from pathlib import Path


METRIC_KEYS = [
    "ate_rmse_m",
    "ate_rmse_percent_of_path",
    "segment_translation_error_percent_mean",
    "segment_rotation_error_deg_per_100m_mean",
]


def mean_std(values):
    return {
        "mean": stats.mean(values),
        "std": stats.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--runs-root",
        type=Path,
        default=Path("results/baselines/orbslam3/kitti00_stereo"),
    )
    ap.add_argument(
        "--pattern",
        default="run_repeat_*/run_summary.json",
    )
    ap.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/baselines/orbslam3/kitti00_stereo/repeat_summary.json"),
    )
    args = ap.parse_args()

    paths = sorted(args.runs_root.glob(args.pattern))
    if not paths:
        raise SystemExit(f"No run summaries found under {args.runs_root} with pattern {args.pattern}")

    rows = [json.loads(p.read_text()) for p in paths]

    metrics = {
        "num_runs": len(rows),
        "runs": [r["run_dir"] for r in rows],
    }

    for key in METRIC_KEYS:
        vals = [float(r[key]) for r in rows]
        metrics[key] = mean_std(vals)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(metrics, indent=2) + "\n")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

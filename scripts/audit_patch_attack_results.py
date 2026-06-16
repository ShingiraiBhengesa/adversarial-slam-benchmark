#!/usr/bin/env python3
import json
from pathlib import Path

required = [
    "docs/attacks/main_results_narrative.md",
    "docs/figures/kitti00_trajectory_clean_black_checkerboard.png",
    "docs/figures/kitti02_trajectory_clean_black_checkerboard.png",

    "results/baselines/orbslam3/kitti00_stereo/repeat_summary.json",
    "results/baselines/orbslam3/kitti02_stereo/repeat_summary.json",

    "results/diagnostics/logs/kitti00_stereo_log_summary.json",
    "results/diagnostics/logs/kitti02_stereo_log_summary.json",

    "results/official_kitti_devkit_eval/kitti00_clean/official_summary.json",
    "results/official_kitti_devkit_eval/kitti00_black10_top_left/official_summary.json",
    "results/official_kitti_devkit_eval/kitti00_checkerboard05_top_left/official_summary.json",
    "results/official_kitti_devkit_eval/kitti02_clean/official_summary.json",
    "results/official_kitti_devkit_eval/kitti02_black10_top_left/official_summary.json",
    "results/official_kitti_devkit_eval/kitti02_checkerboard05_top_left_padded/official_summary.json",
    "results/official_kitti_devkit_eval/kitti02_checkerboard10_top_left_padded/official_summary.json",
]

missing = [p for p in required if not Path(p).exists()]

print("=== REQUIRED ARTIFACT CHECK ===")
if missing:
    print("MISSING:")
    for p in missing:
        print(f"  - {p}")
else:
    print("All required artifacts exist.")

def run_count(d):
    if "num_valid_runs" in d:
        return d["num_valid_runs"]
    if "num_runs" in d:
        return d["num_runs"]
    if "runs" in d:
        return len(d["runs"])
    return "unknown"


def metric_mean_std(d, key):
    if key not in d:
        return "missing"
    val = d[key]
    if isinstance(val, dict) and "mean" in val and "std" in val:
        return f"{val['mean']:.3f} ± {val['std']:.3f}"
    return str(val)


print("\n=== BASELINE RUN COUNTS ===")
for label, path in [
    ("KITTI 00 clean", "results/baselines/orbslam3/kitti00_stereo/repeat_summary.json"),
    ("KITTI 02 clean", "results/baselines/orbslam3/kitti02_stereo/repeat_summary.json"),
]:
    d = json.loads(Path(path).read_text())
    print(
        f"{label}: runs={run_count(d)}, "
        f"ATE={metric_mean_std(d, 'ate_rmse_m')}, "
        f"trans={metric_mean_std(d, 'segment_translation_error_percent_mean')}"
    )

print("\n=== OFFICIAL KITTI DEVKIT CROSS-CHECK ===")
files = sorted(Path("results/official_kitti_devkit_eval").glob("*/official_summary.json"))

for p in files:
    d = json.loads(p.read_text())
    m = d.get("target_sequence_metrics")
    if not m:
        print(f"{d['result_sha']}: MISSING METRICS")
    else:
        print(
            f"{d['result_sha']}: "
            f"trans={m['translation_error_percent_mean']:.3f}%, "
            f"rot={m['rotation_error_deg_per_100m_mean']:.3f} deg/100m, "
            f"segments={m['num_segments']}"
        )

print("\n=== FIGURE LINKS IN NARRATIVE ===")
text = Path("docs/attacks/main_results_narrative.md").read_text()
for fig in [
    "../figures/kitti00_trajectory_clean_black_checkerboard.png",
    "../figures/kitti02_trajectory_clean_black_checkerboard.png",
]:
    print(f"{fig}: {'FOUND' if fig in text else 'MISSING'}")

if missing:
    raise SystemExit(1)

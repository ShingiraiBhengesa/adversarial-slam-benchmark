#!/usr/bin/env python3
import json
from pathlib import Path


REQUIRED = [
    # Canonical docs
    "README.md",
    "docs/attacks/README.md",
    "docs/attacks/main_results_narrative.md",
    "docs/attacks/orb_feature_match_mechanism_summary.md",
    "experiments/orbslam3/kitti_patch_stress/README.md",

    # Figures
    "docs/figures/kitti00_trajectory_clean_black_checkerboard.png",
    "docs/figures/kitti02_trajectory_clean_black_checkerboard.png",

    # Curated summaries
    "artifacts/orbslam3_kitti_patch/summaries/kitti00_clean_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti02_clean_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti00_black_10pct_top_left_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti00_checkerboard_05pct_top_left_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti00_checkerboard_10pct_top_left_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti02_black_10pct_top_left_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti02_checkerboard_05pct_top_left_repeat_summary.json",
    "artifacts/orbslam3_kitti_patch/summaries/kitti02_checkerboard_10pct_top_left_repeat_summary.json",

    # Official devkit cross-checks
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti00_clean_official_summary.json",
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti00_black10_top_left_official_summary.json",
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti00_checkerboard05_top_left_official_summary.json",
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti02_clean_official_summary.json",
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti02_black10_top_left_official_summary.json",
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti02_checkerboard05_top_left_padded_official_summary.json",
    "artifacts/orbslam3_kitti_patch/official_devkit/kitti02_checkerboard10_top_left_padded_official_summary.json",

    # Mechanism artifacts
    "artifacts/orbslam3_kitti_patch/mechanism/orb_match_diagnostic_summary_fixed.md",
    "artifacts/orbslam3_kitti_patch/mechanism/orb_match_diagnostic_summary_fixed.json",
]


def load_json(path):
    return json.loads(Path(path).read_text())


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

    return "missing"


def main():
    print("=== REQUIRED ARTIFACT CHECK ===")
    missing = [p for p in REQUIRED if not Path(p).exists()]

    if missing:
        print("MISSING:")
        for p in missing:
            print(f"  - {p}")
        raise SystemExit(1)

    print("All required artifacts exist.")

    print("\n=== BASELINE RUN COUNTS ===")
    for label, path in [
        ("KITTI 00 clean", "artifacts/orbslam3_kitti_patch/summaries/kitti00_clean_repeat_summary.json"),
        ("KITTI 02 clean", "artifacts/orbslam3_kitti_patch/summaries/kitti02_clean_repeat_summary.json"),
    ]:
        d = load_json(path)
        print(
            f"{label}: runs={run_count(d)}, "
            f"ATE={metric_mean_std(d, 'ate_rmse_m')}, "
            f"trans={metric_mean_std(d, 'segment_translation_error_percent_mean')}"
        )

    print("\n=== OFFICIAL KITTI DEVKIT CROSS-CHECK ===")
    official_root = Path("artifacts/orbslam3_kitti_patch/official_devkit")

    for p in sorted(official_root.glob("*_official_summary.json")):
        d = load_json(p)
        m = d.get("target_sequence_metrics")

        if not m:
            print(f"{p.name}: missing target_sequence_metrics")
            continue

        print(
            f"{p.name}: "
            f"trans={m['translation_error_percent_mean']:.3f}%, "
            f"rot={m['rotation_error_deg_per_100m_mean']:.3f} deg/100m, "
            f"segments={m['num_segments']}"
        )

    print("\n=== MECHANISM ARTIFACT CHECK ===")
    mech = load_json("artifacts/orbslam3_kitti_patch/mechanism/orb_match_diagnostic_summary_fixed.json")
    print(f"fixed ORB match rows: {len(mech)}")

    print("\nAudit passed.")


if __name__ == "__main__":
    main()

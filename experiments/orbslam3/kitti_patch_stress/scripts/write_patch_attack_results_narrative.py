#!/usr/bin/env python3
import json
import statistics as stats
from pathlib import Path


def load(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def fmt(mean, std, digits=3):
    return f"{mean:.{digits}f} ± {std:.{digits}f}"


def run_dir_from_record(run):
    if isinstance(run, dict):
        return Path(run["run_dir"])
    return Path(run)


def count_fail_track(run_dir):
    log_path = run_dir / "orbslam3_stdout.log"
    if not log_path.exists():
        return None
    return log_path.read_text(errors="ignore").count("Fail to track local map")


def fail_track_mean(summary):
    counts = []
    for run in summary["runs"]:
        c = count_fail_track(run_dir_from_record(run))
        if c is not None:
            counts.append(c)
    if not counts:
        return "n/a"
    return f"{stats.mean(counts):.2f}"


def run_count(summary):
    return summary.get("num_valid_runs", summary.get("num_runs", len(summary.get("runs", []))))


def metric_row(seq, condition, summary_path):
    s = load(summary_path)
    return (
        f"| {seq} | {condition} | {run_count(s)} | "
        f"{fmt(s['ate_rmse_m']['mean'], s['ate_rmse_m']['std'])} | "
        f"{fmt(s['segment_translation_error_percent_mean']['mean'], s['segment_translation_error_percent_mean']['std'])} | "
        f"{fmt(s['segment_rotation_error_deg_per_100m_mean']['mean'], s['segment_rotation_error_deg_per_100m_mean']['std'])} | "
        f"{fail_track_mean(s)} |"
    )


rows = []

rows.append(metric_row(
    "KITTI 00",
    "clean",
    "results/baselines/orbslam3/kitti00_stereo/repeat_summary.json",
))

for tag, label in [
    ("seq00_black_10pct_top_left_leftonly", "black 10% top-left"),
    ("seq00_checkerboard_025pct_top_left_leftonly", "checkerboard 2.5% top-left"),
    ("seq00_checkerboard_05pct_top_left_leftonly", "checkerboard 5% top-left"),
    ("seq00_checkerboard_10pct_top_left_leftonly", "checkerboard 10% top-left"),
]:
    rows.append(metric_row(
        "KITTI 00",
        label,
        f"results/attacks/orbslam3/{tag}/attack_repeat_summary.json",
    ))

rows.append(metric_row(
    "KITTI 02",
    "clean",
    "results/generalization/orbslam3/kitti02/clean/repeat_summary.json",
))

for tag, label in [
    ("seq02_black_10pct_top_left_leftonly", "black 10% top-left"),
    ("seq02_checkerboard_025pct_top_left_leftonly", "checkerboard 2.5% top-left"),
    ("seq02_checkerboard_05pct_top_left_leftonly", "checkerboard 5% top-left"),
    ("seq02_checkerboard_10pct_top_left_leftonly", "checkerboard 10% top-left"),
]:
    rows.append(metric_row(
        "KITTI 02",
        label,
        f"results/generalization/orbslam3/kitti02/{tag}/repeat_summary.json",
    ))


out = Path("experiments/orbslam3/kitti_patch_stress/docs/main_results.md")
out.parent.mkdir(parents=True, exist_ok=True)

text = f"""# Main Results Narrative: ORB-SLAM3 Patch Stress Test

## Core question

This experiment asks whether ORB-SLAM3 stereo fails mainly because an image patch occludes part of the scene, or because a high-texture patch corrupts feature extraction and matching.

The current evidence supports the second explanation.

## Experimental setup

- SLAM system: ORB-SLAM3 stereo
- Datasets: KITTI Odometry sequences 00 and 02
- Patch location for cross-sequence comparison: top-left
- Modified camera: left camera only
- Right camera: unchanged
- Control patch: black patch
- Attack patch: checkerboard patch
- Metrics:
  - ATE RMSE
  - KITTI-style segment translation drift
  - KITTI-style segment rotation drift
  - ORB-SLAM3 log symptoms, especially `Fail to track local map`

## Main quantitative result

| Sequence | Condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Rotation drift mean ± std (deg/100m) | Fail-track mean |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Visual result

### KITTI 00

![KITTI 00 trajectory comparison](../figures/kitti00_trajectory_clean_black_checkerboard.png)

### KITTI 02

![KITTI 02 trajectory comparison](../figures/kitti02_trajectory_clean_black_checkerboard.png)

## Interpretation

The black patch control stays close to the clean baseline on both KITTI 00 and KITTI 02. This weakens the explanation that the attack works simply by hiding part of the image.

The checkerboard patch behaves differently. At 5% and 10% patch area, the trajectory error becomes much larger, segment drift increases sharply, and ORB-SLAM3 begins showing internal instability through tracking failures and map events.

This supports a feature-corruption interpretation: the high-texture patch injects visually stable but geometrically misleading local structure. ORB-SLAM3 can continue producing a trajectory, but that trajectory can become severely wrong.

## Threshold behavior

The 2.5% checkerboard condition should not be overclaimed. On KITTI 00, it is only mildly worse than clean. On KITTI 02, it is unstable across repeats, with one severe run and two milder runs. This suggests an early-warning or sequence-sensitive regime, not a deterministic failure threshold.

The strongest current claim is that the failure becomes robust at 5% and 10% patch area in the tested top-left configuration.

## Paper-safe claim

Across KITTI 00 and KITTI 02, same-location black occlusion controls have little effect on ORB-SLAM3 stereo, while high-texture checkerboard patches can cause severe trajectory drift, tracking instability, and map inconsistency. This suggests the vulnerability is driven less by lost image area and more by corrupted feature/match structure.

## What not to claim yet

Do not claim this is a physical adversarial patch. These are digital image-plane stress tests.

Do not claim monotonic degradation with patch size. The results show a qualitative transition, not a clean monotonic curve.

Do not claim official KITTI benchmark performance unless the segment evaluator is cross-checked against the official KITTI odometry evaluator.

Do not claim universal failure at 2.5%. That condition is unstable and sequence-dependent.

## Next evidence needed

The next most useful addition is a small feature/match diagnostic figure: clean vs black vs checkerboard for the same frame, showing that the checkerboard attracts a disproportionate number of ORB features while the black patch does not.
"""

out.write_text(text)
print(f"wrote {out}")

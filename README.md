# Adversarial SLAM Benchmark

## Quick start

New readers should begin with `START_HERE.md`.


This repository contains reproducible experiments for studying how visual SLAM systems respond to controlled image-plane perturbations.

The current validated experiment block is ORB-SLAM3 stereo on KITTI Odometry sequences 00 and 02 under digital patch stress tests.

## Current validated experiment

### ORB-SLAM3 KITTI patch stress test

- System: ORB-SLAM3
- Mode: stereo
- Dataset: KITTI Odometry
- Sequences: 00 and 02
- Patch types:
  - black occlusion control
  - checkerboard feature-injection patch
- Patch location: top-left
- Modified camera: left camera only
- Evaluation:
  - internal ATE evaluation
  - KITTI-style segment drift
  - official KITTI odometry devkit cross-check
  - ORB keypoint and match proxy diagnostics

Experiment index:

- `experiments/orbslam3/kitti_patch_stress/README.md`

Canonical result documents:

- `docs/attacks/main_results_narrative.md`
- `docs/attacks/orb_feature_match_mechanism_summary.md`

Curated mechanism artifacts:

- `artifacts/orbslam3_kitti_patch/mechanism/`

Selected figures:

- `docs/figures/`

## Main finding

Low-texture black occlusion patches remain near the clean ORB-SLAM3 baseline, while high-texture checkerboard patches cause severe trajectory drift.

Official KITTI devkit examples:

| Condition | Translation drift (%) | Rotation drift (deg/100m) |
|---|---:|---:|
| KITTI 00 clean | 0.677 | 0.252 |
| KITTI 00 black 10% top-left | 0.668 | 0.252 |
| KITTI 00 checkerboard 5% top-left | 40.750 | 21.115 |
| KITTI 02 clean | 0.731 | 0.227 |
| KITTI 02 black 10% top-left | 0.707 | 0.227 |
| KITTI 02 checkerboard 5% top-left | 50.511 | 23.733 |
| KITTI 02 checkerboard 10% top-left | 71.953 | 28.463 |

The safest interpretation is that checkerboard patches induce a threshold-like transition into a high-variance catastrophic drift regime. The result should not be framed as a perfectly monotonic dose-response curve.

## Repository structure

- `artifacts/orbslam3_kitti_patch/`
  - Curated small summaries and mechanism artifacts.
- `docs/attacks/`
  - Canonical result and mechanism narratives.
- `docs/figures/`
  - Selected paper-quality figures.
- `experiments/orbslam3/kitti_patch_stress/`
  - Experiment-level index, runbooks, and manifests.
- `scripts/`
  - Patch generation, evaluation, auditing, and diagnostics scripts.
- `systems/ORB_SLAM3/`
  - External ORB-SLAM3 checkout/build.

## Data and output policy

Large datasets, raw trajectories, raw logs, and full experiment outputs are not committed.

Ignored local paths include:

- `data/`
- `results/`
- `logs/`
- `local_mechanism/`
- `local_plans/`

Only curated summaries, selected figures, scripts, and documentation are committed.

## Reproducing the ORB-SLAM3 result block

The high-level workflow is:

1. Prepare KITTI Odometry data locally.
2. Build ORB-SLAM3 under `systems/ORB_SLAM3/`.
3. Generate patched KITTI image sequences with `scripts/create_kitti_patch_attack.py`.
4. Run ORB-SLAM3 conditions with `scripts/run_orbslam3_kitti_condition.sh`.
5. Aggregate repeated runs with `scripts/aggregate_orbslam3_attack_repeats.py`.
6. Cross-check selected conditions with `scripts/run_kitti_official_devkit_eval.py`.
7. Run mechanism diagnostics with:
   - `scripts/orb_patch_feature_diagnostics.py`
   - `scripts/orb_patch_match_diagnostics.py`
8. Audit expected artifacts with `scripts/audit_patch_attack_results.py`.

## Important caveats

These are digital image-plane patch stress tests. They are not physically validated printed-patch attacks.

The ORB keypoint and match diagnostics use OpenCV ORB as a proxy. They are not direct ORB-SLAM3 frontend instrumentation.

Some current attack sweeps use three repeats, while clean baselines use five repeats. This should be disclosed in paper writing.

## Planned next experiment

The next research step is second-system validation.

Recommended pilot:

| System | Dataset | Conditions | Repeats |
|---|---|---|---:|
| VINS-Fusion stereo | KITTI 00 | clean | 3 |
| VINS-Fusion stereo | KITTI 00 | black 10% top-left | 3 |
| VINS-Fusion stereo | KITTI 00 | checkerboard 5% top-left | 3 |

The goal is to test whether the checkerboard-vs-black separation transfers beyond ORB-SLAM3 before running a full severity sweep.

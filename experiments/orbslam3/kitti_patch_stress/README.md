# ORB-SLAM3 KITTI Patch Stress Test

## Purpose

This experiment tests how ORB-SLAM3 stereo odometry behaves when KITTI images are changed with simple digital patches.

The main comparison is:

- black patch: removes image content
- checkerboard patch: adds repeated high-texture pattern

The goal is to test whether ORB-SLAM3 is only affected by missing image content, or whether added repeated texture can cause much larger trajectory error.

## Current status

This is the first completed system experiment in the benchmark.

## System

- SLAM system: ORB-SLAM3
- Mode: stereo
- Dataset: KITTI Odometry
- Sequences: 00 and 02
- Camera changed: left camera only
- Patch location: top-left
- Patch types: black and checkerboard

## Main documents

- Main results: `docs/main_results.md`
- Mechanism summary: `docs/mechanism.md`
- Official KITTI devkit results: `docs/official_kitti_devkit_results.md`
- Severity/onset notes: `docs/severity_onset.md`
- Trajectory visualization notes: `docs/trajectory_visualization.md`
- Full run instructions: `RUNBOOK.md`

## Main scripts

ORB-SLAM3-specific scripts are in:

- `scripts/`

Shared benchmark scripts are in:

- `../../../shared/patching/`
- `../../../shared/evaluation/`
- `../../../shared/diagnostics/`
- `../../../shared/plotting/`
- `../../../shared/cluster/`
- `../../../shared/data/`

Important scripts:

- Patch generation: `../../../shared/patching/create_kitti_patch_attack.py`
- ORB-SLAM3 KITTI condition runner: `scripts/run_orbslam3_kitti_condition.sh`
- ATE evaluator: `../../../shared/evaluation/evaluate_kitti_ate.py`
- KITTI segment evaluator: `../../../shared/evaluation/evaluate_kitti_segments.py`
- Official KITTI devkit wrapper: `../../../shared/evaluation/run_kitti_official_devkit_eval.py`
- Result audit: `scripts/audit_patch_attack_results.py`
- ORB keypoint diagnostic: `../../../shared/diagnostics/orb_patch_feature_diagnostics.py`
- ORB match diagnostic: `../../../shared/diagnostics/orb_patch_match_diagnostics.py`

## Important caveats

These are digital patch tests on saved images. They are not printed physical patch experiments.

The ORB keypoint and match diagnostics use OpenCV ORB as a proxy. They are not direct logs from ORB-SLAM3 internals.

Some attack sweeps use three repeats, while the clean baselines use five repeats. This should be stated clearly in paper writing.

## Next extension

The next system experiment should start with a small pilot:

- clean
- black 10%
- checkerboard 5%

Do not run a full sweep on the next SLAM system until the pilot shows useful signal.

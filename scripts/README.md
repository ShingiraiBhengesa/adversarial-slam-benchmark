# Scripts

This folder contains experiment scripts.

## Main scripts for the ORB-SLAM3 KITTI patch result

Use these first:

- `create_kitti_patch_attack.py`
  - creates black or checkerboard patched KITTI image folders

- `run_orbslam3_kitti_condition.sh`
  - runs ORB-SLAM3 on one KITTI condition

- `aggregate_orbslam3_attack_repeats.py`
  - combines repeated runs into one summary JSON

- `summarize_orbslam3_logs.py`
  - counts tracking failures, new maps, loop detections, and related log events

- `evaluate_kitti_ate.py`
  - computes ATE against KITTI poses

- `evaluate_kitti_segments.py`
  - computes KITTI-style segment drift

- `run_kitti_official_devkit_eval.py`
  - runs the official KITTI odometry devkit check

- `orb_patch_feature_diagnostics.py`
  - counts ORB keypoints inside and outside the patch

- `orb_patch_match_diagnostics.py`
  - checks whether patch-region features attract frame-to-frame ORB matches

- `audit_patch_attack_results.py`
  - checks that the important committed result files exist

## Older helper scripts

Some scripts were used during setup, debugging, or earlier analysis. They are kept because they may still be useful, but the list above is the clean path for the current result.

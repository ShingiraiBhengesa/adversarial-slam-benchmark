# Attack Result Documents

This directory contains result narratives and supporting notes for the current ORB-SLAM3 KITTI patch stress-test block.

## Read first

1. `main_results_narrative.md`

   Canonical summary of the ORB-SLAM3 KITTI patch results. Includes baseline audit, internal repeated-run results, official KITTI devkit cross-check, onset analysis, trajectory visualization notes, mechanism summary, and limitations.

2. `orb_feature_match_mechanism_summary.md`

   Mechanism-specific summary. Explains the ORB keypoint and ORB descriptor match proxy diagnostics supporting the feature-injection interpretation.

## Supporting documents

- `severity_onset_kitti00_checkerboard_top_left.md`

  Onset analysis for checkerboard severity on KITTI 00.

- `trajectory_visualization_summary.md`

  Notes on trajectory comparison figures.

- `official_kitti_devkit_results.md`, if present

  Official KITTI devkit result notes.

## Current validated claim

On KITTI stereo odometry, black occlusion patches remain near the ORB-SLAM3 clean baseline, while high-texture checkerboard patches induce severe trajectory drift.

ORB-style proxy diagnostics show that checkerboard patches concentrate a disproportionate share of keypoints and descriptor matches inside the patch region, supporting a feature-injection mechanism rather than a simple occlusion explanation.

## Caveats

These results are digital image-plane patch stress tests, not physically validated patches.

ORB keypoint and match diagnostics are proxy diagnostics using OpenCV ORB. They are not direct ORB-SLAM3 frontend instrumentation.

The checkerboard severity sweep should be described as threshold-like and high-variance, not as a clean monotonic dose-response curve.

## Canonical current documents

- `main_results_narrative.md`
- `orb_feature_match_mechanism_summary.md`

Older notes in this directory may reflect intermediate experiments or earlier planning.

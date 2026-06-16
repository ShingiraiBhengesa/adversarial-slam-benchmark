# ORB-SLAM3 Log Failure Diagnostics: KITTI 00 Patch Attacks

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Log source: `orbslam3_stdout.log`
- Counted events:
  - `Fail to track local map`
  - `Creation of new map`
  - `*Loop detected`
  - trajectory line count

## Attempt-level log summary

This table includes all detected run directories, including failed or incomplete attempts.

| Condition | Runs | Fail-track mean | New-map mean | Loop mean | Traj lines mean |
|---|---:|---:|---:|---:|---:|
| kitti00_stereo | 7 | 1.57 | 2.00 | 4.29 | 4541.0 |
| seq00_black_5pct_bottom_right_leftonly | 3 | 0.00 | 2.00 | 4.00 | 4541.0 |
| seq00_checkerboard_5pct_bottom_right_leftonly | 4 | 33.50 | 3.00 | 11.50 | 3405.0 |
| seq00_checkerboard_5pct_center_leftonly | 3 | 0.00 | 2.00 | 4.00 | 4541.0 |
| seq00_checkerboard_5pct_top_left_leftonly | 3 | 22.67 | 3.33 | 11.33 | 4540.3 |
| seq00_checkerboard_5pct_top_right_leftonly | 4 | 22.50 | 3.50 | 14.25 | 3405.2 |

## Interpretation

The log diagnostics support the metric results.

Clean runs, black occlusion, and the center checkerboard patch show normal behavior: full-length trajectories, no local-map tracking failures, and the expected number of new maps and loop detections.

Corner checkerboard patches show clear ORB-SLAM3 instability. Bottom-right, top-left, and top-right placements produce repeated local-map tracking failures, extra map creation, more loop detections, and in some attempts incomplete or missing trajectories.

This strengthens the mechanism story: the damaging condition is not mere occlusion and not merely high ORB keypoint density. The damaging condition is spatially localized high-frequency feature injection that destabilizes tracking and mapping.

## Caveat

This is an attempt-level log summary. Failed or incomplete run directories are included. For metric reporting, use valid trajectory runs only. For reliability reporting, keep this attempt-level table.

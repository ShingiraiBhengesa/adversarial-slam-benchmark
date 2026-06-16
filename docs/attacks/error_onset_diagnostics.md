# KITTI 00 Error Onset Diagnostics: 5% Patch Attacks

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Error metric: framewise translation error after first-pose SE(3) alignment
- Onset rule: first frame where error stays above threshold for 20 consecutive frames
- Thresholds: 5 m, 10 m, 25 m, 50 m, 100 m
- FPS assumption: 10 Hz

## Onset summary

| Condition | Valid trajectories | First 10m frame mean | First 25m frame mean | First 50m frame mean | First 100m frame mean |
|---|---:|---:|---:|---:|---:|
| clean baseline | 8 | 976.6 | 2532.0 | none | none |
| black 5% bottom-right left-only | 3 | 1837.0 | none | none | none |
| checkerboard 5% bottom-right left-only | 3 | 185.3 | 231.3 | 280.3 | 340.0 |
| checkerboard 5% center left-only | 3 | 884.7 | none | none | none |
| checkerboard 5% top-left left-only | 3 | 133.0 | 156.3 | 194.0 | 244.3 |
| checkerboard 5% top-right left-only | 3 | 151.3 | 220.7 | 265.0 | 335.3 |

## Interpretation

The structured checkerboard patch causes early catastrophic divergence when placed in several peripheral regions. Top-left is the fastest-failing location in this diagnostic: it reaches 100 m error at about frame 244 on average, or about 24.4 seconds. Bottom-right and top-right also cross 100 m early, around frames 340 and 335 respectively.

The black patch behaves like a weak occlusion control. It crosses 10 m late, but never reaches 25 m, 50 m, or 100 m in the tested runs. This supports the argument that the failure is not caused by lost image area alone. The structured/high-frequency patch is doing something more damaging to the visual front end.

The center checkerboard result is important because it weakens a simplistic “more patch keypoints means more damage” explanation. Even though the center patch attracted many keypoints in the earlier keypoint-density diagnostic, it did not cause catastrophic drift here. This suggests that location, temporal consistency, stereo inconsistency, and downstream map/loop behavior matter more than raw patch keypoint count alone.

## Caveats

The clean baseline row uses all available clean trajectories under the baseline root, not only the curated five-run clean repeat set. For paper-quality reporting, either regenerate this table using only the clean repeat runs or explicitly label it as an all-available-run diagnostic.

The segment and onset metrics are repository KITTI-style diagnostics unless cross-checked against the official KITTI odometry evaluator.

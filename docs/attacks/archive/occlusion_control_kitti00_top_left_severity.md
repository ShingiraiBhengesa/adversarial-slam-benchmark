# KITTI 00 Occlusion Control: Top-Left Patch Severity

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch location: top-left
- Modified camera: left camera only
- Compared patch types:
  - Checkerboard patch: high-texture feature-injection stress test
  - Black patch: occlusion control
- Patch areas: 1%, 2.5%, 5%, 7.5%, 10%
- Repeats: 3 per condition
- Metrics:
  - ATE RMSE
  - KITTI-style translation drift
  - Mean ORB-SLAM3 tracking failure log count

## Checkerboard vs black-patch control

| Patch area | Checkerboard ATE RMSE | Black ATE RMSE | Checkerboard translation drift | Black translation drift | Checkerboard fail-track mean | Black fail-track mean |
|---:|---:|---:|---:|---:|---:|---:|
| 1% | 7.878 ± 0.245 m | 7.403 ± 0.102 m | 0.676 ± 0.001% | 0.666 ± 0.003% | 0.00 | 0.00 |
| 2.5% | 11.260 ± 1.145 m | 7.603 ± 0.379 m | 1.967 ± 0.134% | 0.666 ± 0.013% | 0.00 | 0.00 |
| 5% | 318.600 ± 159.587 m | 7.986 ± 0.220 m | 35.341 ± 5.308% | 0.666 ± 0.015% | 4.00 | 0.00 |
| 7.5% | 259.620 ± 32.964 m | 7.548 ± 0.081 m | 56.692 ± 5.385% | 0.664 ± 0.003% | 22.67 | 0.00 |
| 10% | 286.264 ± 22.153 m | 7.865 ± 0.148 m | 54.897 ± 6.054% | 0.661 ± 0.007% | 41.67 | 0.00 |

## Interpretation

The black-patch control strongly suggests that the checkerboard failure is not caused by simple occlusion. Across 1% to 10% patch area, black patches remain near the clean baseline, with no observed mean tracking failures and stable KITTI-style translation drift near 0.66%.

In contrast, checkerboard patches show a sharp transition between 2.5% and 5%. At 1% and 2.5%, the effect is mild to moderate. At 5% and above, the trajectory becomes severely corrupted, with ATE RMSE increasing by orders of magnitude and ORB-SLAM3 beginning to report tracking instability.

The strongest defensible claim is:

> A high-texture synthetic patch can induce severe ORB-SLAM3 stereo trajectory corruption at patch sizes where a same-location black occlusion control remains near baseline.

## Caveats

These are digital image-plane stress tests, not physically validated adversarial patches. The result should be described as feature-injection or high-texture patch sensitivity, not yet as a physically realizable adversarial patch. Segment drift is KITTI-style unless cross-checked against the official KITTI odometry evaluator.

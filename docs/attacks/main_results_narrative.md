# Main KITTI Patch Attack Results

## Summary

These experiments evaluate whether image-plane patches affect ORB-SLAM3 stereo tracking on KITTI odometry sequences. The key comparison is between a solid black patch, which acts as an occlusion control, and a high-frequency checkerboard patch, which injects artificial visual texture.

The main result is that solid black patches behave close to the clean baseline, while checkerboard patches cause large trajectory corruption. This supports the interpretation that the failure is not merely due to removed pixels, but due to feature-rich texture disturbing visual tracking and matching.

## Experimental setup

- Dataset: KITTI odometry sequences 00 and 02
- SLAM system: ORB-SLAM3 stereo
- Patch location: top-left unless otherwise noted
- Modified camera: left camera only
- Patch types:
  - Black patch: occlusion control
  - Checkerboard patch: high-frequency texture injection
- Metrics:
  - ATE RMSE in meters
  - KITTI-style segment translation drift in percent
  - KITTI-style segment rotation drift in degrees per 100 meters
  - ORB-SLAM3 internal tracking-failure log count

## KITTI 00 severity result

| Patch area | Checkerboard ATE RMSE | Black ATE RMSE | Checkerboard trans drift | Black trans drift | Checkerboard fail-track | Black fail-track |
|---:|---:|---:|---:|---:|---:|---:|
| 1% | 7.878 ± 0.245 | 7.403 ± 0.102 | 0.676 ± 0.001 | 0.666 ± 0.003 | 0.00 | 0.00 |
| 2.5% | 11.260 ± 1.145 | 7.603 ± 0.379 | 1.967 ± 0.134 | 0.666 ± 0.013 | 0.00 | 0.00 |
| 5% | 318.600 ± 159.587 | 7.986 ± 0.220 | 35.341 ± 5.308 | 0.666 ± 0.015 | 4.00 | 0.00 |
| 7.5% | 259.620 ± 32.964 | 7.548 ± 0.081 | 56.692 ± 5.385 | 0.664 ± 0.003 | 22.67 | 0.00 |
| 10% | 286.264 ± 22.153 | 7.865 ± 0.148 | 54.897 ± 6.054 | 0.661 ± 0.007 | 41.67 | 0.00 |

The KITTI 00 results show a sharp transition between 2.5% and 5% checkerboard area. Below this transition, drift increases but the system remains close to baseline. At 5% and above, the checkerboard patch produces catastrophic trajectory corruption, while black patches of comparable or larger size remain close to the clean/near-baseline regime.

## KITTI 02 generalization result

| KITTI 02 condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Rotation drift mean ± std (deg/100m) | Fail-track mean |
|---|---:|---:|---:|---:|---:|
| clean baseline | 5 | 7.838 ± 0.896 | 0.754 ± 0.008 | 0.247 ± 0.010 | 0.00 |
| black 10% top-left | 3 | 8.408 ± 0.420 | 0.722 ± 0.024 | 0.237 ± 0.013 | 0.00 |
| checkerboard 2.5% top-left | 3 | 68.614 ± 79.033 | 6.607 ± 9.743 | 1.578 ± 2.167 | 10.00 |
| checkerboard 5% top-left | 3 | 597.977 ± 123.298 | 47.107 ± 8.627 | 19.413 ± 3.760 | 19.67 |
| checkerboard 10% top-left | 3 | 576.657 ± 69.407 | 66.443 ± 6.642 | 32.650 ± 4.358 | 30.67 |

The KITTI 02 results show the same pattern on a second sequence. The black 10% control remains close to the clean baseline, while checkerboard patches produce large drift and tracking instability. The 2.5% checkerboard condition is unstable across runs, suggesting it lies near the transition boundary for this sequence. The 5% and 10% checkerboard conditions are consistently destructive.

## Official KITTI devkit cross-check

| Condition | Translation drift (%) | Rotation drift (deg/100m) | Segments |
|---|---:|---:|---:|
| KITTI 00 clean | 0.677 | 0.252 | 3283 |
| KITTI 00 black 10% top-left | 0.668 | 0.252 | 3283 |
| KITTI 00 checkerboard 5% top-left | 40.750 | 21.115 | 3283 |
| KITTI 02 clean | 0.731 | 0.227 | 3453 |
| KITTI 02 black 10% top-left | 0.707 | 0.227 | 3453 |
| KITTI 02 checkerboard 5% top-left padded | 50.511 | 23.733 | 3453 |
| KITTI 02 checkerboard 10% top-left padded | 71.953 | 28.463 | 3453 |

The official KITTI devkit cross-check agrees with the internal KITTI-style evaluator. Solid black patches remain near baseline, while checkerboard patches increase translation and rotation drift by orders of magnitude. For KITTI 02 checkerboard 5% and 10%, the prediction files were one pose shorter than the ground truth, so one final pose was padded to satisfy the legacy devkit's strict pose-count requirement. These padded devkit numbers should be treated as a compatibility cross-check, not as the primary repeat-mean statistic.

## Trajectory visualizations

### KITTI 00

![KITTI 00 trajectory comparison](../figures/kitti00_trajectory_clean_black_checkerboard.png)

### KITTI 02

![KITTI 02 trajectory comparison](../figures/kitti02_trajectory_clean_black_checkerboard.png)

The trajectory plots provide qualitative confirmation of the quantitative result. Clean and black-patch trajectories stay close to ground truth, while checkerboard trajectories visibly diverge.

## Main claim

A high-frequency image-plane texture patch can cause severe ORB-SLAM3 trajectory corruption even when a solid occlusion patch of comparable size does not. The evidence supports a texture-injection failure mechanism rather than simple information removal.

## Caveats

These are digital image-plane patch stress tests, not physical-world attacks. The patch is overlaid directly on the image stream and does not model lighting, perspective, multi-view consistency, physical placement, or partial visibility. Therefore, the strongest defensible claim is about digital replay robustness, not real-world physical patch vulnerability.

The KITTI 02 clean baseline uses 5 repeats, while the KITTI 02 attack conditions currently use 3 repeats. This is acceptable for the current draft, but the difference in repeat count should be disclosed. For a final paper table, either rerun the attack conditions with 5 repeats or clearly report the number of valid runs per condition.

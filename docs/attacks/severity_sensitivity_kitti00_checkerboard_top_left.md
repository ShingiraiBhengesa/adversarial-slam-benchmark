# KITTI 00 Severity Sensitivity: Top-Left Checkerboard Patch

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch location: top-left
- Modified camera: left camera only (`image_0`)
- Right camera: unchanged
- Repeats per condition: 3
- Metrics: repository ATE, KITTI-style segment drift, and ORB-SLAM3 log-event diagnostics

## Metric results

| Patch area | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Rotation drift mean ± std (deg/100m) |
|---:|---:|---:|---:|---:|
| 1% | 3 | 7.878 ± 0.245 | 0.676 ± 0.001 | 0.255 ± 0.003 |
| 2.5% | 3 | 11.260 ± 1.145 | 1.967 ± 0.134 | 0.891 ± 0.051 |
| 5% | 3 | 318.600 ± 159.587 | 35.341 ± 5.308 | 16.974 ± 3.716 |
| 7.5% | 3 | 259.620 ± 32.964 | 56.692 ± 5.385 | 31.742 ± 1.405 |
| 10% | 3 | 286.264 ± 22.153 | 54.897 ± 6.054 | 33.345 ± 3.046 |

## ORB-SLAM3 internal log diagnostics

| Patch area | Runs | Fail-track mean | New-map mean | Loop mean | Trajectory lines mean |
|---:|---:|---:|---:|---:|---:|
| 1% | 3 | 0.00 | 2.00 | 4.00 | 4541.0 |
| 2.5% | 3 | 0.00 | 2.00 | 4.00 | 4541.0 |
| 5% | 3 | 4.00 | 2.00 | 8.33 | 4541.0 |
| 7.5% | 3 | 22.67 | 3.33 | 19.00 | 4540.3 |
| 10% | 3 | 41.67 | 4.00 | 16.33 | 4540.0 |

## Interpretation

The severity sweep suggests a sharp failure threshold between 2.5% and 5% patch area. At 1% and 2.5%, ORB-SLAM3 behaves close to the clean baseline. At 5%, ATE and KITTI-style drift increase sharply, but the system still often completes with a full trajectory and only modest tracking-failure logs. This indicates a silent corruption regime: the estimated trajectory can become badly wrong before ORB-SLAM3 reports strong internal failure symptoms.

At 7.5% and 10%, the attack becomes more visibly disruptive. Tracking failures, extra map creation, stored maps, and loop events increase substantially. These larger patches therefore represent an overt failure regime, while 5% is the more scientifically interesting transition point.

## Caveats

These are digital image-plane patch stress tests, not physically validated patches. The segment drift values are KITTI-style repository metrics unless cross-checked against the official KITTI odometry evaluator. ATE is sensitive to ORB-SLAM3 stochasticity, loop closure, and map-reset behavior, so the strongest claim should be based on the threshold pattern across ATE, segment drift, and log diagnostics together rather than on one metric alone.

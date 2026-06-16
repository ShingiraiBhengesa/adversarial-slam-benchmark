# KITTI 00 Feature-Injection Control: Checkerboard vs Black Patch

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch location: top-left
- Modified camera: left camera only
- Compared patch types: checkerboard versus black occlusion
- Patch areas: 1%, 2.5%, 5%, 7.5%, 10%
- Diagnostic: OpenCV ORB keypoint detection with 2000 features, sampled every 10 frames

## Feature-density diagnostic

| Patch area | Clean patch keypoint frac | Checkerboard patch keypoint frac | Black patch keypoint frac |
|---:|---:|---:|---:|
| 1% | 0.0009 | 0.0128 | 0.0013 |
| 2.5% | 0.0063 | 0.0758 | 0.0028 |
| 5% | 0.0210 | 0.2006 | 0.0045 |
| 7.5% | 0.0389 | 0.2642 | 0.0057 |
| 10% | 0.0607 | 0.3275 | 0.0072 |

## Trajectory impact

| Patch area | Checkerboard ATE RMSE | Black ATE RMSE | Checkerboard translation drift | Black translation drift | Checkerboard fail-track mean | Black fail-track mean |
|---:|---:|---:|---:|---:|---:|---:|
| 1% | 7.878 ± 0.245 m | 7.403 ± 0.102 m | 0.676 ± 0.001% | 0.666 ± 0.003% | 0.00 | 0.00 |
| 2.5% | 11.260 ± 1.145 m | 7.603 ± 0.379 m | 1.967 ± 0.134% | 0.666 ± 0.013% | 0.00 | 0.00 |
| 5% | 318.600 ± 159.587 m | 7.986 ± 0.220 m | 35.341 ± 5.308% | 0.666 ± 0.015% | 4.00 | 0.00 |
| 7.5% | 259.620 ± 32.964 m | 7.548 ± 0.081 m | 56.692 ± 5.385% | 0.664 ± 0.003% | 22.67 | 0.00 |
| 10% | 286.264 ± 22.153 m | 7.865 ± 0.148 m | 54.897 ± 6.054% | 0.661 ± 0.007% | 41.67 | 0.00 |

## Interpretation

The black-patch control isolates ordinary occlusion from high-texture feature injection. If the failure were mainly caused by removing pixels, then the black patch should degrade ORB-SLAM3 similarly as patch size increases. Instead, the black patch remains near baseline even at larger patch areas, while the checkerboard patch produces severe trajectory corruption from the 5% region onward.

This supports the mechanism claim that the checkerboard patch disrupts ORB-SLAM3 by creating a dense, misleading feature region rather than simply hiding part of the image.

The strongest defensible paper wording is:

> High-texture image-plane patches can induce severe ORB-SLAM3 stereo trajectory corruption at patch sizes where same-location black occlusion controls remain near baseline, suggesting that feature injection rather than occlusion is the dominant failure mechanism.

## Caveats

This remains a digital image-plane stress test, not a physically validated adversarial patch. The diagnostic ORB detector approximates the feature-budget mechanism but is not a direct trace of ORB-SLAM3 internal feature selection.

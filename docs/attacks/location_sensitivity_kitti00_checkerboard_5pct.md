# KITTI 00 Location Sensitivity: 5% Checkerboard Patch

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch area: 5% of image area
- Modified camera: left camera only (`image_0`)
- Right camera: unchanged
- Metric type: repository KITTI-style segment drift and ATE

## Results

| Location | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Rotation drift mean ± std (deg/100m) |
|---|---:|---:|---:|---:|
| bottom-right | 3 | 230.487 ± 51.309 | 52.051 ± 4.335 | 30.966 ± 2.474 |
| top-left | 3 | 264.201 ± 41.894 | 41.146 ± 2.378 | 23.326 ± 4.982 |
| center | 3 | 6.895 ± 0.270 | 0.743 ± 0.018 | 0.299 ± 0.009 |
| bottom-left | 3 | 173.310 ± 57.921 | 42.186 ± 14.676 | 23.031 ± 7.321 |
| top-right | 2 | 191.180 ± 29.103 | 50.611 ± 2.672 | 23.356 ± 1.602 |

## Interpretation

The checkerboard patch effect is strongly location-sensitive. Corner placements cause severe degradation, while the center placement behaves close to the clean baseline. This suggests the failure is not simply caused by the presence of high-frequency texture anywhere in the image. The patch likely interacts with ORB-SLAM3's spatial feature selection, matching, and mapping behavior.

The center result is especially important because it prevents overclaiming. A stronger claim is: small textured patches can severely degrade ORB-SLAM3 stereo, but the effect depends on image location.

## Caveats

- The top-right condition currently has only 2 valid runs and should be rerun to reach 3.
- These are digital image-plane patches, not physical printed patches.
- Segment drift values are KITTI-style repository metrics, not official KITTI odometry server results.

## Pose-error time-series diagnostic

| Condition | RMSE (m) | Max error (m) | Max frame | First >25m | First >50m | First >100m |
|---|---:|---:|---:|---:|---:|---:|
| clean | 7.11 | 11.67 | 3954 | — | — | — |
| center | 6.63 | 11.80 | 3963 | — | — | — |
| bottom-right | 213.99 | 479.25 | 2986 | 247 | 282 | 347 |

## Interpretation

The bottom-right checkerboard patch causes early trajectory divergence, crossing 25m error by frame 247 and 100m by frame 347. The maximum error occurs much later, but the onset is early. Therefore, the correct diagnostic window is approximately frames 240–350, not only the maximum-error region near frame 2986.

The center patch remains close to clean behavior across the full sequence, despite having more patch-region keypoints, more patch-region temporal matches, and more patch-region RANSAC inliers. This strengthens the conclusion that the mechanism is not explained by raw feature count or generic temporal epipolar consistency alone.

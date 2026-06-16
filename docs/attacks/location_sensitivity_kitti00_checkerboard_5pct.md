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

## Failure-onset visual inspection window

A contact sheet was generated locally for frames 200, 240, 247, 282, 347, and 400 using the clean sequence and the bottom-right checkerboard attack sequence. These frames bracket the early divergence window where the bottom-right attack crosses 25m, 50m, and 100m pose error.

Local artifact:

`results/diagnostics/failure_onset_frames/bottom_right_onset_contact_sheet.png`

## Visual inspection of bottom-right failure onset

The bottom-right contact sheet shows that during the early divergence window, especially frames 240–400, the checkerboard patch overlaps visually important right-side scene structure such as parked cars, building edges, sidewalk boundaries, shadows, and façade lines. This suggests the observed failure is not simply caused by adding many features anywhere in the image.

The stronger interpretation is that the checkerboard patch becomes harmful when placed over spatial regions that contribute important tracking and mapping constraints. This supports a placement-sensitive mechanism rather than a pure keypoint-count or pure temporal-RANSAC explanation.

## Center-vs-corner visual comparison

The center contact sheet shows that the center checkerboard patch also overlaps visually meaningful scene content, including the road corridor, parked cars, building boundaries, and shadows. However, the center condition remains close to clean baseline performance.

This weakens the simpler hypothesis that failure occurs merely because the patch covers important scene structure. The evidence instead points toward a more spatially specific mechanism: high-texture injected features become most harmful when they create a strong asymmetric feature cluster near the image periphery or corners. This may affect ORB-SLAM3 through feature distribution, map-point creation, keyframe/local-map behavior, or pose-optimization leverage rather than through raw keypoint count alone.

The center patch appears to be geometrically absorbed by the tracker, while peripheral patches produce early trajectory divergence.

# KITTI 00 Patch Match Diagnostics: 5% Checkerboard Left-Only

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch area: 5%
- Modified camera: left camera only
- Diagnostic matcher: OpenCV ORB + BFMatcher cross-check
- Diagnostic stride: every 10 frames
- Pair step: 1 frame
- Max Hamming distance: 50

## Match diagnostic results

| Location | Temporal patch match frac | Temporal patch disp px | Stereo patch match frac | Stereo patch disparity px |
|---|---:|---:|---:|---:|
| bottom_right | 0.5337 | 5.62 | 0.0025 | 401.77 |
| top_left | 0.5112 | 6.48 | 0.0028 | -375.48 |
| center | 0.7215 | 4.00 | 0.0095 | -9.96 |
| bottom_left | 0.5428 | 6.01 | 0.0030 | -398.09 |
| top_right | 0.4859 | 6.86 | 0.0021 | 353.49 |

## Interpretation

The center patch has the highest temporal patch match fraction, but it does not significantly degrade ORB-SLAM3. This means temporal patch matching alone does not explain the observed failure.

The strongest differentiator is the stereo diagnostic. Corner placements produce extreme patch-region stereo disparities, while the center patch produces a much smaller near-zero disparity. This suggests that catastrophic corner failures are more consistent with geometry-disrupting patch matches than with raw feature density alone.

## Careful claim

The diagnostics support the hypothesis that high-frequency patch features become harmful when they interact with stereo/geometry in unstable ways. Feature density is not sufficient as an explanation because the center patch has the highest patch-keypoint and temporal-match concentration but remains near baseline.

## Caveat

This diagnostic does not prove which matches ORB-SLAM3 internally accepts. It uses an external OpenCV ORB + BFMatcher cross-check pipeline, not ORB-SLAM3's internal stereo matching, map-point creation, and outlier rejection logic.

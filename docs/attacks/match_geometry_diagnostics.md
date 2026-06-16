# KITTI 00 Match Geometry Diagnostics: 5% Checkerboard Patch

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch area: 5%
- Modified camera: left camera only
- Diagnostic matcher: OpenCV ORB + Hamming BFMatcher with cross-check
- Diagnostic stride: every 10 frames
- Note: this is an external diagnostic, not ORB-SLAM3's internal matcher.

## Match diagnostic results

| Location | Temporal patch match frac | Temporal patch disp px | Stereo patch match frac | Stereo patch disparity px |
|---|---:|---:|---:|---:|
| bottom_right | 0.5337 | 5.62 | 0.0025 | 401.77 |
| top_left | 0.5112 | 6.48 | 0.0028 | -375.48 |
| center | 0.7215 | 4.00 | 0.0095 | -9.96 |
| bottom_left | 0.5428 | 6.01 | 0.0030 | -398.09 |
| top_right | 0.4859 | 6.86 | 0.0021 | 353.49 |

## Interpretation

The center checkerboard patch produces many patch-region ORB features and the highest patch match fractions, but it does not significantly degrade ORB-SLAM3. Therefore, keypoint count and match count alone do not explain the attack.

The stronger signal is stereo geometry. Corner patches produce very large patch-associated stereo disparities, roughly ±350 to ±400 pixels, while the center patch produces a much smaller disparity magnitude. This supports the hypothesis that catastrophic degradation is driven by geometrically disruptive false matches, not merely by feature injection density.

## Current mechanism hypothesis

High-frequency checkerboard patches inject many ORB features. Catastrophic failure occurs when those features create spatially concentrated, geometrically inconsistent stereo or temporal evidence that contaminates tracking and mapping. The center patch appears less damaging because its patch-associated matches are less geometrically disruptive.

## Caveat

These diagnostics use an external ORB/BFMatcher pipeline. They should be treated as supporting evidence. A stronger future diagnostic would instrument ORB-SLAM3 directly to count patch-region matches, inliers, outliers, and map points.

## Absolute match-count location diagnostic

| Location | Temporal total | Temporal patch | Stereo total | Stereo patch |
|---|---:|---:|---:|---:|
| bottom_right | 1179.32 | 624.62 | 499.75 | 1.16 |
| top_left | 1132.15 | 574.04 | 499.39 | 1.34 |
| center | 1191.61 | 857.56 | 308.24 | 2.62 |
| bottom_left | 1170.83 | 630.83 | 490.96 | 1.40 |
| top_right | 1126.35 | 543.60 | 515.41 | 1.01 |

## Refined interpretation

The center checkerboard patch produces the highest number of patch-region temporal matches, yet the center condition remains close to clean baseline performance. Therefore, temporal patch match count alone does not explain failure.

The corner conditions produce fewer patch-region temporal matches than the center condition but cause severe degradation. This suggests that the attack depends on where injected features enter the image geometry, not only how many injected features are detected or matched.

Stereo patch match counts are low for all locations, so stereo diagnostics should be treated as supporting evidence rather than the primary mechanism.

The current best hypothesis is spatially sensitive feature-track pollution: injected textured features become harmful when they affect high-leverage image regions for tracking and mapping. Center-region feature pollution is abundant but appears less damaging or more easily rejected by the downstream SLAM pipeline.

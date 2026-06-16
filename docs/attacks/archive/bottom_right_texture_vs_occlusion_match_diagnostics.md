# Bottom-Right Texture vs Occlusion Match Diagnostics

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch location: bottom-right
- Patch area: 5%
- Modified camera: left camera only
- Diagnostic matcher: OpenCV ORB + Hamming BFMatcher with cross-check
- Diagnostic stride: every 10 frames
- Note: this is an external diagnostic, not ORB-SLAM3's internal matcher.

## Results

| Condition | Temporal patch match frac | Temporal disp px | Stereo patch match frac | Stereo disparity px |
|---|---:|---:|---:|---:|
| black 5% bottom-right left-only | 0.0004 | 48.03 | 0.0002 | 277.89 |
| random 5% bottom-right left-only | 0.3974 | 0.29 | 0.0023 | 389.52 |
| checkerboard 5% bottom-right left-only | 0.5337 | 5.62 | 0.0025 | 401.77 |

## Interpretation

The black patch behaves like simple occlusion: it creates almost no patch-region temporal or stereo matches, and the corresponding SLAM result remains close to the clean baseline.

The random and checkerboard patches behave differently. They create many patch-region temporal matches and produce patch-associated stereo matches with very large disparities. These conditions also produce severe ORB-SLAM3 degradation.

This supports the hypothesis that the attack effect comes from artificial textured feature injection rather than simple feature removal.

## Caveat

The stereo match fraction is small for all conditions. Therefore, the large disparity values should be interpreted together with match volume and downstream SLAM degradation, not as a standalone explanation. A stronger future diagnostic would instrument ORB-SLAM3 directly to count patch-region inliers, outliers, and map points.

## Absolute match-count diagnostic

| Condition | Temporal matches total | Temporal patch matches | Stereo matches total | Stereo patch matches |
|---|---:|---:|---:|---:|
| black 5% bottom-right left-only | 1026.39 | 0.43 | 818.57 | 0.14 |
| random 5% bottom-right left-only | 1212.74 | 488.39 | 630.88 | 1.25 |
| checkerboard 5% bottom-right left-only | 1179.32 | 624.62 | 499.75 | 1.16 |

## Refined interpretation

The absolute counts show that the black patch contributes almost no patch-region temporal matches, while the random and checkerboard patches contribute hundreds of temporal patch matches per sampled frame pair. This is a stronger diagnostic than patch keypoint count alone.

The stereo patch match counts are very small, around one patch-region stereo match per sampled frame. Therefore, the stereo disparity diagnostic should be treated as supporting evidence, not the primary mechanism.

The current best explanation is temporal feature-track pollution: textured patches inject persistent artificial ORB features that are repeatedly matched across time, contaminating tracking and mapping. Simple occlusion does not create this effect.

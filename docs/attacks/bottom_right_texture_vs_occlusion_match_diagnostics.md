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

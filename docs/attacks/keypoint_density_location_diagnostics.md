# KITTI 00 Keypoint Density Diagnostics: 5% Checkerboard Patch

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch area: 5%
- Modified camera: left camera only
- ORB feature cap: 2000 features
- Diagnostic stride: every 10 frames

## Keypoint density results

| Location | Clean patch KP mean | Attack patch KP mean | Clean patch KP frac | Attack patch KP frac |
|---|---:|---:|---:|---:|
| bottom_right | 39.40 | 886.56 | 0.0197 | 0.4432 |
| top_left | 83.15 | 876.73 | 0.0416 | 0.4383 |
| center | 261.46 | 1222.34 | 0.1308 | 0.6111 |
| bottom_left | 36.70 | 911.02 | 0.0184 | 0.4555 |
| top_right | 85.92 | 835.03 | 0.0430 | 0.4175 |

## Interpretation

The center patch produces the highest number and fraction of patch-region ORB keypoints, yet the center patch does not significantly degrade ORB-SLAM3. Therefore, patch-region ORB keypoint count alone does not explain the attack effect.

The severe failures seen in corner placements are more likely caused by how injected patch features interact with spatial feature distribution, temporal matching, stereo correspondence, or map initialization. The mechanism is therefore geometric/spatial, not merely feature-density based.

## Updated claim

A small high-frequency patch can dominate ORB feature extraction, but catastrophic SLAM degradation depends strongly on image location. Feature injection density is necessary to measure, but insufficient as a standalone explanation.

## Next diagnostic

Analyze temporal and stereo matches involving patch-region keypoints. The key question is whether damaging corner patches produce more accepted false matches than the center patch.

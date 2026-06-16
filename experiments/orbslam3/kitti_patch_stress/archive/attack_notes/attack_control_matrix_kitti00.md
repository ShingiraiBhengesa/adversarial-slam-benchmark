# KITTI 00 Patch Control Matrix: ORB-SLAM3 Stereo

## Purpose

This control matrix separates simple occlusion from harmful artificial texture and stereo inconsistency. All conditions use KITTI Odometry sequence 00 and ORB-SLAM3 stereo.

Clean reference is the 5-run clean baseline:

- ATE RMSE: 7.206066747824011 ± 0.47158506731930333 m
- KITTI-style translation drift: 0.6786799488134423 ± 0.0015298720393951606%
- KITTI-style rotation drift: 0.2524391721734871 ± 0.003485820137255906 deg / 100 m

## Results

| Condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Rotation drift mean ± std (deg/100m) |
|---|---:|---:|---:|---:|
| checkerboard 5%, bottom-right, left-only | 3 | 230.487 ± 51.309 | 52.051 ± 4.335 | 30.966 ± 2.474 |
| black 5%, bottom-right, left-only | 3 | 6.949 ± 0.430 | 0.692 ± 0.013 | 0.253 ± 0.014 |
| random 5%, bottom-right, left-only | 3 | 262.707 ± 52.072 | 66.018 ± 3.365 | 34.791 ± 3.437 |
| checkerboard 10%, bottom-right, left-only | 3 | 243.537 ± 72.445 | 59.052 ± 10.246 | 34.814 ± 6.820 |
| checkerboard 5%, bottom-right, both cameras | 3 | 226.682 ± 70.831 | 48.422 ± 12.351 | 25.765 ± 8.523 |

## Interpretation

The black 5% left-only patch behaves close to the clean baseline, so the failure is not explained by simple occlusion. In contrast, the random and checkerboard textured patches cause severe degradation, indicating that artificial high-frequency texture is the main harmful factor.

The both-camera checkerboard condition is also severely degraded, which means the attack is not only caused by left-right stereo inconsistency. Stereo inconsistency may amplify the effect, but the stronger finding is that artificial textured patches can destabilize ORB-SLAM3 stereo even when both camera streams are modified.

The 10% checkerboard condition is not cleanly worse than the 5% checkerboard condition. This suggests the failure saturates: once the textured patch is strong enough to corrupt tracking and mapping, increasing patch area does not necessarily produce monotonic metric growth.

## Current claim

A small high-frequency digital image-plane patch can severely degrade ORB-SLAM3 stereo on KITTI 00, while an equal-area black occlusion patch does not. This supports the hypothesis that feature-injection texture is more damaging than simple feature removal.

## Caveats

- These are digital image-plane perturbations, not physically validated printed patches.
- Segment drift values are KITTI-style repository metrics, not official KITTI odometry server results.
- Each condition currently has 3 repeats. More repeats would improve confidence, especially for the high-variance both-camera and 10% checkerboard conditions.

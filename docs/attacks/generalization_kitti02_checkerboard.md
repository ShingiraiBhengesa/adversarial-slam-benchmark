# KITTI 02 Generalization: Top-Left Checkerboard Patch

## Setup

- Dataset: KITTI Odometry sequence 02
- SLAM system: ORB-SLAM3 stereo
- Patch location: top-left
- Modified camera: left camera only (`image_0`)
- Right camera: unchanged
- Patch type: checkerboard, with black occlusion control
- Repeats: 3 per condition
- Metrics: ATE RMSE and repository KITTI-style segment drift

## Results

| KITTI 02 condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Rotation drift mean ± std (deg/100m) | Fail-track mean |
|---|---:|---:|---:|---:|---:|
| clean | 3 | 7.511 ± 0.305 | 0.737 ± 0.006 | 0.236 ± 0.008 | 0.00 |
| black 10% top-left | 3 | 8.408 ± 0.420 | 0.722 ± 0.024 | 0.237 ± 0.013 | 0.00 |
| checkerboard 2.5% top-left | 3 | 68.614 ± 79.033 | 6.607 ± 9.743 | 1.578 ± 2.167 | 10.00 |
| checkerboard 5% top-left | 3 | 597.977 ± 123.298 | 47.107 ± 8.627 | 19.413 ± 3.760 | 19.67 |
| checkerboard 10% top-left | 3 | 576.657 ± 69.407 | 66.443 ± 6.642 | 32.650 ± 4.358 | 30.67 |

## Interpretation

KITTI 02 supports the same high-level pattern observed on KITTI 00: simple black occlusion does not substantially degrade ORB-SLAM3 stereo, while high-texture checkerboard patches can produce severe trajectory corruption and tracking instability.

The 10% black patch remains near the clean baseline, which strengthens the argument that the failure is not explained by area occlusion alone. The checkerboard patch changes the feature/matching structure of the image and produces much larger trajectory error.

The 2.5% checkerboard condition is unstable across repeats. One run fails badly while the other two remain closer to baseline. This should be reported as an early-warning region, not as a deterministic failure threshold.

The 5% and 10% checkerboard conditions are the strongest generalization evidence: both produce very large ATE and KITTI-style drift on KITTI 02.

## Paper-safe claim

Across KITTI 00 and KITTI 02, high-texture image-plane patches degrade ORB-SLAM3 stereo far more than same-location black occlusion controls. The effect is severity-dependent and becomes consistently large around 5% patch area in the tested top-left configuration.

## Caveats

These are digital image-plane patch stress tests, not physically validated patches. Segment drift is KITTI-style unless cross-checked against the official KITTI odometry evaluator. ORB-SLAM3 can show run-to-run stochasticity, so all conclusions should be framed using repeated runs rather than single trajectories.

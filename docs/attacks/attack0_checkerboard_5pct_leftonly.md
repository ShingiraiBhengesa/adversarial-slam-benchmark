# Attack 0: KITTI 00 Left-Camera Checkerboard Patch Stress Test

## Attack configuration

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Attack type: digital image-plane patch stress test
- Patch mode: checkerboard
- Patch area: 5% of image area
- Patch location: bottom-right
- Cameras modified: left camera only (`image_0`)
- Right camera: unchanged
- Attack sequence: `data/kitti_attacks/seq00_checkerboard_5pct_bottom_right_leftonly`
- Attack run: `results/attacks/orbslam3/seq00_checkerboard_5pct_bottom_right_leftonly/run_20260615_052346`

## Clean baseline

Clean baseline is the 5-run ORB-SLAM3 KITTI 00 stereo repeat summary.

- ATE RMSE: 7.206066747824011 ± 0.47158506731930333 m
- ATE RMSE / path length: 0.19349368777715376 ± 0.012662765551513012%
- KITTI-style mean translation drift: 0.6786799488134423 ± 0.0015298720393951606%
- KITTI-style mean rotation drift: 0.2524391721734871 ± 0.003485820137255906 deg / 100 m

## Attack metrics

- Estimated poses: 4540
- Evaluated poses: 4540
- Ground-truth path length: 3723.0509169005895 m
- ATE RMSE: 213.98760040368558 m
- ATE RMSE / path length: 5.747640985308591%
- ATE mean: 173.76448727280837 m
- ATE median: 158.9699143911274 m
- ATE max: 479.2511803395279 m
- KITTI-style mean translation drift: 48.81354492758062%
- KITTI-style mean rotation drift: 28.122815180551278 deg / 100 m
- Total evaluated segments: 3282

## Observed tracking behavior

The ORB-SLAM3 log showed repeated tracking failures and map disruption:

- Repeated `Fail to track local map!`
- New map created around keyframe 1266
- Map merge later occurred
- Final trajectory was saved successfully

## Interpretation

This attack caused severe trajectory degradation relative to the clean baseline. The result should be described as a digital image-plane stereo stress test, not yet as a physically realizable adversarial patch. Because the patch is applied to the left image only while the right image remains clean, the likely mechanism is stereo correspondence disruption plus high-frequency feature injection.

## Caveat

The segment drift values are KITTI-style metrics computed by the repository evaluator, not official KITTI odometry server results.

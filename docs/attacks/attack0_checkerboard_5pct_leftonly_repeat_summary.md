# Attack 0 Repeat Summary: KITTI 00 Left-Camera Checkerboard Patch

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
- Valid attack runs: 3

## Clean baseline

Clean baseline is the 5-run ORB-SLAM3 KITTI 00 stereo repeat summary.

- ATE RMSE: 7.206066747824011 ± 0.47158506731930333 m
- ATE RMSE / path length: 0.19349368777715376 ± 0.012662765551513012%
- KITTI-style mean translation drift: 0.6786799488134423 ± 0.0015298720393951606%
- KITTI-style mean rotation drift: 0.2524391721734871 ± 0.003485820137255906 deg / 100 m

## Attack repeat results

- ATE RMSE: 230.48654569192797 ± 51.3085090566688 m
- ATE RMSE / path length: 6.190797569961955 ± 1.3781307374485952%
- KITTI-style mean translation drift: 52.05055059101963 ± 4.335415926784396%
- KITTI-style mean rotation drift: 30.965649124519384 ± 2.47413220630344 deg / 100 m

## Interpretation

The 5% left-camera-only checkerboard patch caused severe degradation relative to clean ORB-SLAM3 stereo performance. Across three valid runs, the attack increased ATE RMSE by roughly 32x and KITTI-style translation drift by roughly 77x.

The observed failure should be described carefully: this is a digital image-plane stereo stress test, not yet a physically realizable adversarial patch. Because only the left camera was modified, the likely mechanism is a combination of stereo correspondence disruption and high-frequency feature injection.

## Caveat

Segment drift values are KITTI-style metrics computed by the repository evaluator, not official KITTI odometry benchmark server results.

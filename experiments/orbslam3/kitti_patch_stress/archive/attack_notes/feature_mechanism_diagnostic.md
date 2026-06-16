# Feature Mechanism Diagnostic

## Purpose

This diagnostic supports the mechanism claim behind the ORB-SLAM3 patch stress test.

The key question is whether failure is caused by ordinary occlusion or by high-texture feature corruption.

## Figure

![KITTI 00 top-left 5% keypoint diagnostic](../figures/kitti00_top_left_5pct_keypoint_diagnostic_frame0120.png)

## Interpretation

The black patch is an occlusion control. If the black patch produces near-baseline behavior while the checkerboard patch attracts many ORB keypoints and causes severe trajectory drift, then the stronger explanation is not simple loss of image area.

The checkerboard patch creates a dense, artificial feature region. In a feature-based SLAM system, this can corrupt local matching and geometric estimation even when the system continues to output a trajectory.

## Caveat

This diagnostic uses OpenCV ORB keypoints as an explanatory proxy. It is not a direct dump of ORB-SLAM3's internal feature pipeline, so it should be framed as supporting evidence rather than definitive internal instrumentation.

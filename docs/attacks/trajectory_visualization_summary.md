# Trajectory Visualization Summary

## Purpose

These figures provide qualitative visual evidence for the quantitative KITTI 00 and KITTI 02 patch results.

The plotted trajectory for each condition is the repeat whose ATE RMSE is closest to that condition's repeat mean. This avoids cherry-picking the best or worst run.

## Figures

### KITTI 00

![KITTI 00 trajectory comparison](../figures/kitti00_trajectory_clean_black_checkerboard.png)

### KITTI 02

![KITTI 02 trajectory comparison](../figures/kitti02_trajectory_clean_black_checkerboard.png)

## Interpretation

The clean and black-patch control trajectories remain close to the ground truth. The checkerboard trajectories visibly deviate, confirming that the main effect is not simple image occlusion but high-texture feature/match corruption.

## Caveat

These are digital image-plane patch stress tests. They should not be described as physically validated patch attacks.

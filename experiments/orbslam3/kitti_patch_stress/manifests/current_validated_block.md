# Current Validated ORB-SLAM3 KITTI Patch Block

## Validated system

- ORB-SLAM3 stereo

## Validated dataset

- KITTI Odometry sequence 00
- KITTI Odometry sequence 02

## Validated perturbation families

- black top-left patch
- checkerboard top-left patch

## Main evaluated conditions

- clean baseline
- black 10% top-left
- checkerboard 5% top-left
- checkerboard 10% top-left

## Additional KITTI 00 severity sweep

- checkerboard 1%
- checkerboard 2.5%
- checkerboard 5%
- checkerboard 7.5%
- checkerboard 10%

## Evaluation layers

- ATE RMSE
- KITTI-style segment translation drift
- KITTI-style segment rotation drift
- official KITTI odometry devkit
- ORB keypoint proxy diagnostic
- ORB match proxy diagnostic

## Current main claim

Black occlusion remains near baseline. Checkerboard texture injection causes severe drift.

## Main caveat

The checkerboard failure regime is threshold-like and high-variance, not a clean monotonic dose-response curve.

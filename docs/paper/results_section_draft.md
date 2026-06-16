# Draft Results Section: ORB-SLAM3 Patch Stress Test

## RQ1: Does a high-texture image patch degrade ORB-SLAM3 more than simple occlusion?

Yes. Across KITTI 00 and KITTI 02, black occlusion controls remain close to the clean baseline, while checkerboard patches cause large trajectory drift and visible geometric collapse.

On KITTI 00, the clean baseline achieves an ATE RMSE of 7.206 ± 0.472 m and a KITTI-style translation drift of 0.679 ± 0.002%. A 10% black patch remains near this range, with 7.865 ± 0.148 m ATE RMSE and 0.661 ± 0.007% translation drift. In contrast, the 5% checkerboard patch increases ATE RMSE to 318.600 ± 159.587 m and translation drift to 35.341 ± 5.308%. The 10% checkerboard patch remains highly disruptive, with 286.264 ± 22.153 m ATE RMSE and 54.897 ± 6.054% translation drift.

The same pattern appears on KITTI 02. The clean baseline achieves 7.511 ± 0.305 m ATE RMSE and 0.737 ± 0.006% translation drift. The 10% black patch remains near baseline, with 8.408 ± 0.420 m ATE RMSE and 0.722 ± 0.024% translation drift. However, the 5% checkerboard patch increases ATE RMSE to 597.977 ± 123.298 m and translation drift to 47.107 ± 8.627%. The 10% checkerboard patch produces 576.657 ± 69.407 m ATE RMSE and 66.443 ± 6.642% translation drift.

These results suggest that the failure is not caused simply by removing image content. Instead, the checkerboard patch acts as a high-texture feature attractor that corrupts the feature and matching structure used by ORB-SLAM3.

## RQ2: What is the likely failure mechanism?

The keypoint diagnostic supports a feature-corruption explanation. In a representative KITTI 00 frame, the 5% top-left region contains 18/2000 ORB keypoints in the clean image and 8/2000 ORB keypoints under a black patch. Under the checkerboard patch, the same 5% region contains 405/2001 keypoints.

Thus, a 5% checkerboard patch attracts about 20.2% of all detected ORB keypoints, roughly four times its proportional image area. This is consistent with a mechanism where the patch injects artificial local texture rather than merely occluding real scene content.

## RQ3: Does the effect generalize across sequences?

The attack generalizes from KITTI 00 to KITTI 02, but not identically. Both sequences show near-baseline behavior under black occlusion and severe degradation under 5% and 10% checkerboard patches. However, the 2.5% condition is unstable: it is mild on KITTI 00 but can produce severe runs on KITTI 02.

This supports a threshold-style interpretation rather than a strictly monotonic patch-size curve. The safest claim is that high-texture patches induce a transition from near-baseline tracking to severe geometric corruption, and that the exact transition point depends on sequence content and geometry.

## Qualitative trajectory evidence

The trajectory plots reinforce the quantitative results. In both KITTI 00 and KITTI 02, clean and black-patch trajectories remain close to the ground truth. Checkerboard trajectories deviate sharply, producing incorrect loops and distorted paths. This visual behavior is consistent with geometric corruption rather than simple gradual drift.

## Limitations

These experiments use digital image-plane patches and should not be described as physically validated attacks. The KITTI-style segment drift evaluator should also be cross-checked against the official KITTI odometry evaluator before making official benchmark claims. Finally, the feature diagnostic uses OpenCV ORB as a proxy for explaining ORB-SLAM3 behavior; it supports the mechanism but does not directly instrument ORB-SLAM3 internals.

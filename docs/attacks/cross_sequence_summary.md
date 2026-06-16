# Cross-Sequence Summary: KITTI 00 and KITTI 02

## Main takeaway

The current evidence supports a stronger claim than a single-sequence stress test: ORB-SLAM3 stereo is robust to simple black occlusion controls but vulnerable to high-texture checkerboard patches that inject many stable visual features.

## Sequence-level evidence

| Sequence | Condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Fail-track mean |
|---|---|---:|---:|---:|---:|
| KITTI 00 | clean | 5 | 7.206 ± 0.472 | 0.679 ± 0.002 | 0.00 |
| KITTI 00 | black 10% top-left | 3 | 7.865 ± 0.148 | 0.661 ± 0.007 | 0.00 |
| KITTI 00 | checkerboard 2.5% top-left | 3 | 11.260 ± 1.145 | 1.967 ± 0.134 | 0.00 |
| KITTI 00 | checkerboard 5% top-left | 3 | 318.600 ± 159.587 | 35.341 ± 5.308 | 4.00 |
| KITTI 00 | checkerboard 10% top-left | 3 | 286.264 ± 22.153 | 54.897 ± 6.054 | 41.67 |
| KITTI 02 | clean | 3 | 7.511 ± 0.305 | 0.737 ± 0.006 | 0.00 |
| KITTI 02 | black 10% top-left | 3 | 8.408 ± 0.420 | 0.722 ± 0.024 | 0.00 |
| KITTI 02 | checkerboard 2.5% top-left | 3 | 68.614 ± 79.033 | 6.607 ± 9.743 | 10.00 |
| KITTI 02 | checkerboard 5% top-left | 3 | 597.977 ± 123.298 | 47.107 ± 8.627 | 19.67 |
| KITTI 02 | checkerboard 10% top-left | 3 | 576.657 ± 69.407 | 66.443 ± 6.642 | 30.67 |

## Interpretation

The cross-sequence pattern is consistent: black occlusion remains near baseline, while checkerboard patches cause large trajectory corruption.

The strongest defensible result is not that error increases monotonically with patch size. It does not. The stronger result is that textured patches introduce a qualitative failure mode that black occlusion does not.

The 2.5% region should be described as unstable or sequence-sensitive. The 5% and 10% checkerboard conditions are the robust failure region in the current experiments.

## Recommended paper wording

A same-area black patch control has little effect on ORB-SLAM3 stereo, while high-texture checkerboard patches can cause large trajectory drift, tracking failures, and map instability. This supports the hypothesis that the vulnerability is driven less by visual occlusion and more by feature/match corruption.

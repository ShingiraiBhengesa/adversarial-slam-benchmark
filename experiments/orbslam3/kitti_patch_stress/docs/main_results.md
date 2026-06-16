# Main Results: KITTI Patch Stress Tests Against ORB-SLAM3

## Summary

These experiments evaluate whether small digital image-plane patches can degrade ORB-SLAM3 stereo odometry on KITTI. The key comparison is between a low-texture black occlusion patch and a high-texture checkerboard patch.

The black patch acts as an occlusion control. It removes local image content but does not inject strong visual structure. The checkerboard patch acts as a feature-injection perturbation. It introduces dense, repeatable local texture that can attract ORB keypoints and frame-to-frame descriptor matches.

Across KITTI 00 and KITTI 02, the black 10% top-left patch remains close to the clean baseline. In contrast, checkerboard patches cause large trajectory drift, early error onset, increased tracking instability, and visible trajectory deviation. The result supports the claim that the failure is not explained by simple occlusion alone. The damaging mechanism is high-texture feature and match corruption.

## Experimental scope

- Dataset: KITTI Odometry sequences 00 and 02
- System: ORB-SLAM3 stereo
- Patch type: black occlusion control and checkerboard feature-injection patch
- Patch location: top-left
- Modified camera: left camera only
- Evaluation:
  - Internal ATE and KITTI-style segment drift evaluator
  - Official KITTI odometry devkit cross-check
  - ORB keypoint proxy diagnostic
  - ORB descriptor match proxy diagnostic

These are digital image-plane patch stress tests. They should not be described as physically validated patch attacks.

## Audited baseline results

| Condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) |
|---|---:|---:|---:|
| KITTI 00 clean | 5 | 7.206 ± 0.472 | 0.679 ± 0.002 |
| KITTI 02 clean | 5 | 7.838 ± 0.896 | 0.754 ± 0.008 |

The clean baselines are stable across repeated runs and show low KITTI-style translation drift.

## Main internal repeated-run results

| Sequence | Condition | Runs | ATE RMSE mean ± std (m) | Translation drift mean ± std (%) | Interpretation |
|---|---|---:|---:|---:|---|
| KITTI 00 | black 10% top-left | 3 | 7.865 ± 0.148 | 0.661 ± 0.007 | Near baseline |
| KITTI 00 | checkerboard 2.5% top-left | 3 | 11.260 ± 1.145 | 1.967 ± 0.134 | Mild degradation |
| KITTI 00 | checkerboard 5% top-left | 3 | 318.600 ± 159.587 | 35.341 ± 5.308 | Catastrophic, high variance |
| KITTI 00 | checkerboard 7.5% top-left | 3 | 259.620 ± 32.964 | 56.692 ± 5.385 | Catastrophic |
| KITTI 00 | checkerboard 10% top-left | 3 | 286.264 ± 22.153 | 54.897 ± 6.054 | Catastrophic |
| KITTI 02 | black 10% top-left | 3 | 8.408 ± 0.420 | 0.722 ± 0.024 | Near baseline |
| KITTI 02 | checkerboard 2.5% top-left | 3 | 68.614 ± 79.033 | 6.607 ± 9.743 | Unstable degradation |
| KITTI 02 | checkerboard 5% top-left | 3 | 597.977 ± 123.298 | 47.107 ± 8.627 | Catastrophic |
| KITTI 02 | checkerboard 10% top-left | 3 | 576.657 ± 69.407 | 66.443 ± 6.642 | Catastrophic |

The repeated-run results show a threshold-like transition. Small checkerboard patches can cause mild drift, but around the 5% region the system enters a high-variance catastrophic regime. The non-monotonic ATE values are important: they suggest stochastic failure, relocalization, recovery, and new-map effects rather than a clean dose-response curve.

The safest wording is therefore not “error increases monotonically with patch size.” The safer and more accurate wording is:

> Checkerboard patches induce a threshold-like transition from near-baseline tracking to a high-variance catastrophic failure regime.

## Official KITTI devkit cross-check

| Condition | Translation drift (%) | Rotation drift (deg/100m) | Segments |
|---|---:|---:|---:|
| KITTI 00 clean | 0.677 | 0.252 | 3283 |
| KITTI 00 black 10% top-left | 0.668 | 0.252 | 3283 |
| KITTI 00 checkerboard 5% top-left | 40.750 | 21.115 | 3283 |
| KITTI 02 clean | 0.731 | 0.227 | 3453 |
| KITTI 02 black 10% top-left | 0.707 | 0.227 | 3453 |
| KITTI 02 checkerboard 5% top-left | 50.511 | 23.733 | 3453 |
| KITTI 02 checkerboard 10% top-left | 71.953 | 28.463 | 3453 |

The official KITTI devkit confirms the central trend. Clean and black-patch controls remain below 1% translation drift. Checkerboard patches produce severe drift, reaching 40.750% on KITTI 00 at 5% patch area and 50.511% on KITTI 02 at 5% patch area.

This cross-check strengthens the result because it shows that the trend is not an artifact of the internal evaluator.

## Error onset on KITTI 00

| Patch area | Valid trajectories | First 5m frame mean | First 10m frame mean | First 25m frame mean | First 50m frame mean | First 100m frame mean |
|---:|---:|---:|---:|---:|---:|---:|
| 1% | 3 | 311.7 | 735.0 | none | none | none |
| 2.5% | 3 | 310.7 | 685.7 | 2802.7 | none | none |
| 5% | 3 | 111.7 | 126.0 | 144.7 | 166.7 | 233.0 |
| 7.5% | 3 | 103.7 | 109.3 | 125.3 | 143.0 | 278.3 |
| 10% | 3 | 46.0 | 86.3 | 179.7 | 209.3 | 311.3 |

The onset analysis separates mild degradation from catastrophic failure. At 1% and 2.5%, errors cross small thresholds but do not consistently reach large-error thresholds. At 5% and above, large errors appear early in the sequence. This supports the threshold-style interpretation.

## Trajectory visualization

The trajectory figures provide qualitative support for the quantitative results.

- [KITTI 00 trajectory comparison](../figures/trajectories/kitti00_trajectory_clean_black_checkerboard.png)
- [KITTI 02 trajectory comparison](../figures/trajectories/kitti02_trajectory_clean_black_checkerboard.png)

The clean and black-patch trajectories remain close to ground truth. The checkerboard trajectories visibly deviate, matching the large drift values.

## Mechanism diagnostic

A separate ORB feature and match proxy diagnostic supports the interpretation that the checkerboard patch acts as a feature-injection perturbation rather than simple occlusion.

See: [ORB feature and match mechanism summary](mechanism.md)

### ORB keypoint concentration

Across seven KITTI 00 frames, the checkerboard patch captured a disproportionate share of ORB keypoints.

| Condition | Frames | Total keypoints mean | Patch keypoints mean | % in patch mean ± std | Patch area % mean | Density ratio mean ± std |
|---|---:|---:|---:|---:|---:|---:|
| clean reference top-left 10% region | 7 | 2000.0 | 102.9 | 5.14 ± 3.86 | 10.00 | 0.51 ± 0.39 |
| black 10% top-left | 7 | 2000.0 | 6.4 | 0.32 ± 0.24 | 10.00 | 0.03 ± 0.02 |
| checkerboard 5% top-left | 7 | 2000.4 | 869.0 | 43.44 ± 0.98 | 5.02 | 8.66 ± 0.20 |
| checkerboard 10% top-left | 7 | 2000.4 | 1000.3 | 50.00 ± 0.74 | 10.00 | 5.00 ± 0.07 |

### ORB match concentration

Across seven adjacent KITTI 00 frame pairs, the checkerboard patch also captured a disproportionate share of accepted ORB descriptor matches.

| Condition | Pairs | Matches mean | Either patch match % mean ± std | Both patch match % mean ± std | Patch area % | Either density ratio mean ± std | Both density ratio mean ± std |
|---|---:|---:|---:|---:|---:|---:|---:|
| clean reference top-left 10% region | 7 | 2238.0 | 3.27 ± 3.42 | 2.42 ± 3.10 | 10.00 | 0.33 ± 0.34 | 0.24 ± 0.31 |
| black 10% top-left | 7 | 2145.3 | 0.16 ± 0.26 | 0.10 ± 0.25 | 10.00 | 0.02 ± 0.03 | 0.01 ± 0.03 |
| checkerboard 5% top-left | 7 | 2458.0 | 14.31 ± 2.10 | 13.59 ± 2.37 | 5.02 | 2.85 ± 0.42 | 2.71 ± 0.47 |
| checkerboard 10% top-left | 7 | 2576.1 | 27.98 ± 3.78 | 26.99 ± 3.96 | 10.00 | 2.80 ± 0.38 | 2.70 ± 0.40 |

The black patch suppresses local keypoints and contributes almost no accepted patch-region matches. The checkerboard behaves differently. Even at 5% image area, it captures roughly 43% of detected ORB keypoints and about 13.6% of both-endpoint descriptor matches. At 10% image area, it captures about 50% of detected ORB keypoints and about 27% of both-endpoint descriptor matches.

This supports the mechanism claim: the checkerboard does not primarily harm ORB-SLAM3 by hiding scene content. It harms the visual frontend by injecting dense, repeatable local structure that can dominate feature extraction and perturb matching.

## Main interpretation

The results support three claims.

First, simple occlusion is not enough to explain the failure. A black 10% patch remains near the clean baseline on both KITTI 00 and KITTI 02.

Second, checkerboard patches cause severe trajectory degradation. The effect appears on two KITTI sequences and is confirmed by both the internal evaluator and the official KITTI devkit.

Third, the mechanism evidence supports feature injection. The checkerboard patch attracts a disproportionate fraction of ORB keypoints and accepted descriptor matches, while the black patch does not.

## Limitations and caveats

The attack results use fewer repeats than the clean baselines in some conditions. Clean baselines use five repeats, while several attack conditions use three repeats. This should be reported clearly.

The 5% checkerboard condition is especially important but also high-variance. On KITTI 00, the ATE standard deviation is large relative to the mean. This should not be hidden. It indicates a stochastic catastrophic regime rather than a clean deterministic failure.

The current experiments use KITTI stereo sequences, not the originally considered TUM RGB-D sequence. This is a defensible change because KITTI provides stereo odometry data and an official evaluation devkit, but the change should be stated explicitly.

The fail-track counts are internal log-derived event counts per run, not frame percentages. They should be defined before being used in a paper table.

The ORB feature and match diagnostics are proxy diagnostics using OpenCV ORB and descriptor matching. They are not direct ORB-SLAM3 frontend instrumentation.

These are digital image-plane patches, not physically validated printed or camera-captured patches.

## Paper-safe headline

A safe paper-level summary is:

> On KITTI stereo odometry, black occlusion patches remain near the ORB-SLAM3 clean baseline, while high-texture checkerboard patches induce a threshold-like transition into a high-variance catastrophic drift regime. Official KITTI devkit evaluation confirms the drift increase, and ORB-style proxy diagnostics show that checkerboard patches concentrate a disproportionate share of keypoints and descriptor matches inside the patch region. This supports a feature-injection mechanism rather than a simple occlusion explanation.

## Next experimental step

The next experiment should test external validity. The strongest next move is a small second-system pilot, such as VINS-Fusion stereo on KITTI 00, using only clean, black 10%, and checkerboard 5% conditions. This tests whether the effect transfers beyond ORB-SLAM3 without opening a full new severity sweep.

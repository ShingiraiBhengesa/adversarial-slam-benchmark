# KITTI 00 Top-Left Checkerboard Severity Results

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch location: top-left
- Modified camera: left camera only
- Repeats: 3 per severity
- Metrics: ATE RMSE, KITTI-style segment drift, error onset, and ORB-SLAM3 log symptoms

## Combined severity table

| Patch area | ATE RMSE mean ± std (m) | Trans. drift mean ± std (%) | Rot. drift mean ± std (deg/100m) | First 100m error frame | Fail-track mean | New-map mean |
|---:|---:|---:|---:|---:|---:|---:|
| 1% | 7.878 ± 0.245 | 0.676 ± 0.001 | 0.255 ± 0.003 | none | 0.00 | 2.00 |
| 2.5% | 11.260 ± 1.145 | 1.967 ± 0.134 | 0.891 ± 0.051 | none | 0.00 | 2.00 |
| 5% | 318.600 ± 159.587 | 35.341 ± 5.308 | 16.974 ± 3.716 | 233.0 | 4.00 | 2.00 |
| 7.5% | 259.620 ± 32.964 | 56.692 ± 5.385 | 31.742 ± 1.405 | 278.3 | 22.67 | 3.33 |
| 10% | 286.264 ± 22.153 | 54.897 ± 6.054 | 33.345 ± 3.046 | 311.3 | 41.67 | 4.00 |

## Main finding

The top-left checkerboard patch shows threshold-like behavior rather than a smooth monotonic relationship with patch size. At 1% and 2.5%, ORB-SLAM3 remains close to baseline-level behavior, with no early 50m or 100m error onset and no tracking-failure log symptoms. At 5%, the system transitions into early large-error corruption: 50m and 100m error onset appear within the first few hundred frames. At 7.5% and 10%, the attack produces stronger overt instability, including frequent tracking failures and additional map creation.

## Paper-safe wording

A fixed high-texture patch can induce a sharp robustness transition in ORB-SLAM3 stereo. Below a small-area threshold, the system mostly absorbs the perturbation as ordinary drift. Around the 5% area regime, the patch begins to cause early trajectory corruption, and at larger areas the failure becomes more visible in ORB-SLAM3 internal logs through tracking loss and map resets.

## Caveat

These results are from digital image-plane patch injection, not a physically validated printed patch. The results should be presented as a controlled stress test, not as proof of physical-world attack transfer.

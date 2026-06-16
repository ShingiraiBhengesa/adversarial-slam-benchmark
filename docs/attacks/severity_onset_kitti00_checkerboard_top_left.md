# KITTI 00 Severity Onset: Top-Left Checkerboard Patch

## Setup

- Dataset: KITTI Odometry sequence 00
- SLAM system: ORB-SLAM3 stereo
- Patch type: checkerboard
- Patch location: top-left
- Modified camera: left camera only
- Onset definition: first frame where error remains above threshold for 20 consecutive frames
- Thresholds: 5, 10, 25, 50, 100 meters

## Error onset by severity

| Patch area | Valid trajectories | First 5m frame mean | First 10m frame mean | First 25m frame mean | First 50m frame mean | First 100m frame mean |
|---:|---:|---:|---:|---:|---:|---:|
| 1% | 3 | 311.7 | 735.0 | none | none | none |
| 2.5% | 3 | 310.7 | 685.7 | 2802.7 | none | none |
| 5% | 3 | 111.7 | 126.0 | 144.7 | 166.7 | 233.0 |
| 7.5% | 3 | 103.7 | 109.3 | 125.3 | 143.0 | 278.3 |
| 10% | 3 | 46.0 | 86.3 | 179.7 | 209.3 | 311.3 |

## Interpretation

The onset analysis separates mild degradation from true failure. Small patches may increase drift without producing early large-error onset. The key transition is expected around the 5% region: this is where the attack starts producing large trajectory error before ORB-SLAM3 necessarily reports strong internal failure symptoms.

For the paper, this supports a threshold-style claim rather than a simple monotonic-size claim. The most defensible wording is that textured patches show a severity-dependent transition from near-baseline tracking to silent corruption and then overt tracking failure.

## Caveats

These are digital image-plane patch stress tests, not physically validated patches. Onset values depend on the chosen threshold, consecutive-frame window, trajectory alignment, and ORB-SLAM3 stochasticity.

# Official KITTI Odometry Devkit Results

## Purpose

This document records the official KITTI odometry devkit metrics for the clean baseline, black-patch occlusion control, and checkerboard textured patch attacks.

These results are used as a compatibility check against the standard KITTI odometry segment-error protocol. The main repeated-run statistics are reported separately; this table reports the official devkit evaluation for the prepared trajectory file for each condition.

## Evaluation setup

- SLAM system: ORB-SLAM3 stereo
- Dataset sequences: KITTI Odometry 00 and 02
- Patch location: top-left
- Modified camera: left camera only
- Control patch: black image-plane patch
- Attack patch: checkerboard image-plane patch
- Metrics: KITTI odometry segment translation error and rotation error
- Translation error unit: percent
- Rotation error unit: degrees per 100 meters

For KITTI 02 checkerboard 5% and 10%, the estimated trajectory had 4660 poses while the ground truth had 4661 poses. For devkit compatibility, the final estimated pose was repeated once, padding 1 frame out of 4661 frames. This affects less than 0.03% of the sequence and is documented here for transparency.

## Official devkit metrics

| Sequence | Condition | Translation drift (%) | Rotation drift (deg/100m) | Segments |
|---|---|---:|---:|---:|
| KITTI 00 | Clean | 0.677 | 0.252 | 3283 |
| KITTI 00 | Black 10% top-left | 0.668 | 0.252 | 3283 |
| KITTI 00 | Checkerboard 5% top-left | 40.750 | 21.115 | 3283 |
| KITTI 02 | Clean | 0.731 | 0.227 | 3453 |
| KITTI 02 | Black 10% top-left | 0.707 | 0.227 | 3453 |
| KITTI 02 | Checkerboard 5% top-left | 50.511 | 23.733 | 3453 |
| KITTI 02 | Checkerboard 10% top-left | 71.953 | 28.463 | 3453 |

## Interpretation

The official KITTI devkit metrics confirm the central result: black image-plane occlusion does not materially degrade ORB-SLAM3 stereo odometry, while the checkerboard textured patch causes severe trajectory corruption.

On KITTI 00, the clean baseline and black 10% control remain near 0.67% translation drift, while the checkerboard 5% condition increases translation drift to 40.75%. On KITTI 02, the clean and black 10% conditions remain near 0.7% translation drift, while checkerboard 5% rises to 50.51% and checkerboard 10% rises to 71.95%.

This supports the claim that the failure mode is not simple loss of image area. The damaging condition is the introduction of a high-texture, repeatable feature pattern that corrupts feature matching and odometry estimation.

## Caveats

These are digital image-plane patch stress tests, not physically validated printed-patch attacks. The official devkit results should be described as standard odometry metric validation, while the repeated-run summaries should be used for statistical claims.

The devkit attempted to generate plots using gnuplot/pdfcrop, which were unavailable on the system. These plotting errors do not invalidate the numeric segment-error metrics recorded above.

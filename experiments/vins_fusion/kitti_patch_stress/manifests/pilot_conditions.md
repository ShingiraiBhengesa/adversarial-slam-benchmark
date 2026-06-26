# VINS-Fusion KITTI Pilot Conditions

## Pilot table

| ID | Sequence | Condition | Patch | Repeats | Purpose |
|---|---|---|---|---:|---|
| vins_kitti00_clean | 00 | clean | none | 3 | baseline |
| vins_kitti00_black10_top_left | 00 | black 10% top-left | black | 3 | occlusion control |
| vins_kitti00_checkerboard05_top_left | 00 | checkerboard 5% top-left | checkerboard | 3 | feature-injection transfer test |

## Decision rule

If checkerboard 5% produces much larger drift than clean and black 10%, expand to more repeats or more sequences.

If all three conditions behave similarly, pause before doing a full sweep.

## Why this pilot is small

The goal is to test transfer beyond ORB-SLAM3 without spending time on a full severity sweep too early.

A full sweep only makes sense if the pilot shows a clear separation between black occlusion and checkerboard texture injection.

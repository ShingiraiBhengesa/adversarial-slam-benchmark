# VINS-Fusion KITTI Patch Stress Test Runbook

This runbook documents the VINS-Fusion KITTI patch pilot.

## Goal

Test whether the checkerboard patch effect seen in ORB-SLAM3 also appears in VINS-Fusion.

This is a pilot, not a full sweep.

## Pilot conditions

| ID | KITTI sequence | Condition | Repeats | Purpose |
|---|---|---|---:|---|
| vins_kitti00_clean | 00 | clean | 3 | baseline |
| vins_kitti00_black10_top_left | 00 | black 10% top-left | 3 | occlusion control |
| vins_kitti00_checkerboard05_top_left | 00 | checkerboard 5% top-left | 3 | feature-injection test |

## Expected local folders

VINS-Fusion source/build should live locally under:

- systems/VINS-Fusion/

KITTI data should live locally under:

- data/kitti/dataset/

Raw outputs should be written under:

- results/vins_fusion/

These folders are local and should not be committed.

## Shared benchmark scripts

Patch generation should reuse:

- shared/patching/create_kitti_patch_attack.py

Trajectory evaluation should reuse:

- shared/evaluation/evaluate_kitti_ate.py
- shared/evaluation/evaluate_kitti_segments.py

Official KITTI devkit checks should reuse:

- shared/evaluation/run_kitti_official_devkit_eval.py

## First implementation task

Create one VINS-Fusion run wrapper in:

- experiments/vins_fusion/kitti_patch_stress/scripts/

The wrapper should run one KITTI condition and write a trajectory file that can be evaluated by the shared KITTI evaluators.

## Do not do yet

Do not run a full severity sweep.

Do not add KITTI 02 yet.

Do not add more patch sizes until the KITTI 00 pilot shows useful signal.

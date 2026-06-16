# Start Here

This repo currently has one completed experiment.

## Completed experiment

ORB-SLAM3 on KITTI with image patches.

We tested two kinds of patches:

- black patch
- checkerboard patch

The main result:

- black patch: stays close to the clean run
- checkerboard patch: causes large trajectory drift

## Read these first

1. `experiments/orbslam3/kitti_patch_stress/README.md`
2. `experiments/orbslam3/kitti_patch_stress/docs/main_results.md`
3. `experiments/orbslam3/kitti_patch_stress/docs/mechanism.md`
4. `experiments/orbslam3/kitti_patch_stress/RUNBOOK.md`

## Main folders

- `experiments/`
  - system-specific experiments

- `shared/`
  - reusable benchmark scripts

- `tools/`
  - external evaluation tools

- `paper/`
  - paper writing

## Check everything

Run:

    python experiments/orbslam3/kitti_patch_stress/scripts/audit_patch_attack_results.py

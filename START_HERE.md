# Start Here

This repo currently has one completed experiment:

## ORB-SLAM3 on KITTI with image patches

We tested whether different image patches affect ORB-SLAM3 stereo odometry.

The main result is simple:

- Black patch: stays close to the clean run.
- Checkerboard patch: causes large trajectory drift.

## Read these first

1. `README.md`
2. `experiments/orbslam3/kitti_patch_stress/README.md`
3. `experiments/orbslam3/kitti_patch_stress/docs/main_results.md`
4. `experiments/orbslam3/kitti_patch_stress/docs/mechanism.md`
5. `experiments/orbslam3/kitti_patch_stress/RUNBOOK.md`

## Where results are stored

Small result summaries are here:

- `experiments/orbslam3/kitti_patch_stress/results_summary/summaries/`
- `experiments/orbslam3/kitti_patch_stress/results_summary/official_devkit/`
- `experiments/orbslam3/kitti_patch_stress/results_summary/mechanism/`

Selected figures are here:

- `experiments/orbslam3/kitti_patch_stress/figures/`

## What is not in the repo

Large local files are not committed:

- KITTI dataset
- attacked image folders
- raw ORB-SLAM3 run folders
- raw trajectories
- SLURM logs

## Quick check

Run:

    python experiments/orbslam3/kitti_patch_stress/experiments/orbslam3/kitti_patch_stress/scripts/audit_patch_attack_results.py

If it passes, the important result files are present.

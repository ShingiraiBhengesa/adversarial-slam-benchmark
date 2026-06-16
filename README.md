# Adversarial SLAM Benchmark

This repo tests how SLAM systems behave when their input images are changed in controlled ways.

## Completed experiment

The completed experiment is:

- ORB-SLAM3
- KITTI Odometry
- stereo
- black patch vs checkerboard patch

Main result:

- black patch stays close to the clean run
- checkerboard patch causes large trajectory drift

Start here:

- `START_HERE.md`
- `experiments/orbslam3/kitti_patch_stress/README.md`

## Repo layout

- `experiments/`
  - one folder per system experiment
  - each experiment keeps its own docs, figures, result summaries, and system-specific scripts

- `shared/`
  - reusable benchmark code used across systems

- `tools/`
  - external evaluation tools

- `paper/`
  - paper drafts, result text, and figure captions

- `data/`
  - local datasets
  - ignored by Git

- `results/`
  - full local run outputs
  - ignored by Git

- `logs/`
  - cluster/job logs
  - ignored by Git

## Completed experiment folder

- `experiments/orbslam3/kitti_patch_stress/`

## Check

Run:

    python experiments/orbslam3/kitti_patch_stress/scripts/audit_patch_attack_results.py

The current experiments are digital image-plane patch stress tests, not printed physical patch experiments.

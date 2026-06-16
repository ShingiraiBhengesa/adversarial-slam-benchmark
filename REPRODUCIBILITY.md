# Reproducibility Guide

This repository separates large local experiment outputs from curated committed artifacts.

## Current validated experiment block

The current validated block is:

- System: ORB-SLAM3
- Mode: stereo
- Dataset: KITTI Odometry
- Sequences: 00 and 02
- Perturbations: digital image-plane black and checkerboard patches
- Main claim: black occlusion remains near baseline, while checkerboard texture injection causes severe drift

## What is committed

The repository commits:

- source scripts
- experiment indices and runbooks
- selected documentation
- selected figures
- small curated JSON/CSV/MD artifacts

## What is not committed

The repository does not commit:

- KITTI data
- generated attacked image sequences
- full ORB-SLAM3 trajectories
- raw repeated-run folders
- SLURM logs
- local exploratory mechanism outputs
- external build products

These remain local under ignored folders such as:

- `data/`
- `results/`
- `logs/`
- `local_mechanism/`
- `systems/ORB_SLAM3/`

## Canonical ORB-SLAM3 documents

Read these first:

- `README.md`
- `experiments/orbslam3/kitti_patch_stress/README.md`
- `experiments/orbslam3/kitti_patch_stress/RUNBOOK.md`
- `experiments/orbslam3/kitti_patch_stress/docs/main_results.md`
- `experiments/orbslam3/kitti_patch_stress/docs/mechanism.md`

## Audit

Run:

    python experiments/orbslam3/kitti_patch_stress/experiments/orbslam3/kitti_patch_stress/scripts/audit_patch_attack_results.py

The audit checks that the curated ORB-SLAM3 result artifacts, figures, summaries, and docs expected by the repository are present.

## Caveat

The current patch experiments are digital image-plane stress tests. They should not be described as physically validated patch attacks.

# ORB-SLAM3 KITTI Patch Stress-Test Runbook

## Purpose

This runbook records the reproducible workflow for the ORB-SLAM3 KITTI patch stress-test block.

The goal is to compare:

- clean KITTI stereo odometry
- black occlusion patch
- checkerboard feature-injection patch

The main question is whether degradation is caused by simple occlusion or by injected high-texture structure that perturbs feature extraction and matching.

## Dataset

Expected local KITTI layout:

- `data/kitti/dataset/sequences/00/`
- `data/kitti/dataset/sequences/02/`
- `data/kitti/dataset/poses/00.txt`
- `data/kitti/dataset/poses/02.txt`

The KITTI dataset itself is not committed.

## System

Expected local ORB-SLAM3 checkout/build:

- `systems/ORB_SLAM3/`

This external system directory is not treated as benchmark source code.

## Step 1: Generate attacked KITTI sequences

Example black 10% patch:

    python experiments/orbslam3/kitti_patch_stress/shared/patching/create_kitti_patch_attack.py \
      --source-sequence data/kitti/dataset/sequences/00 \
      --output-sequence data/kitti_attacks/seq00_black_10pct_top_left_leftonly \
      --area-fraction 0.10 \
      --location top_left \
      --mode black

Example checkerboard 5% patch:

    python experiments/orbslam3/kitti_patch_stress/shared/patching/create_kitti_patch_attack.py \
      --source-sequence data/kitti/dataset/sequences/00 \
      --output-sequence data/kitti_attacks/seq00_checkerboard_05pct_top_left_leftonly \
      --area-fraction 0.05 \
      --location top_left \
      --mode checkerboard

The attacked image sequences are generated local data and are not committed.

## Step 2: Run ORB-SLAM3 condition repeats

Example single condition runner:

    bash experiments/orbslam3/kitti_patch_stress/experiments/orbslam3/kitti_patch_stress/scripts/run_orbslam3_kitti_condition.sh \
      00 \
      seq00_checkerboard_05pct_top_left_leftonly \
      data/kitti_attacks/seq00_checkerboard_05pct_top_left_leftonly \
      1

For SLURM arrays, submit repeated jobs with different repeat IDs and write outputs under `results/`.

Raw run folders are not committed.

## Step 3: Aggregate repeated runs

Example:

    python experiments/orbslam3/kitti_patch_stress/experiments/orbslam3/kitti_patch_stress/scripts/aggregate_orbslam3_attack_repeats.py \
      --attack-root results/attacks/orbslam3/seq00_checkerboard_05pct_top_left_leftonly \
      --output-json results/attacks/orbslam3/seq00_checkerboard_05pct_top_left_leftonly/attack_repeat_summary.json

## Step 4: Summarize ORB-SLAM3 logs

Example:

    python experiments/orbslam3/kitti_patch_stress/experiments/orbslam3/kitti_patch_stress/scripts/summarize_orbslam3_logs.py \
      --root results/attacks/orbslam3/seq00_checkerboard_05pct_top_left_leftonly \
      --output-json results/diagnostics/logs_severity/seq00_checkerboard_05pct_top_left_leftonly_log_summary.json

## Step 5: Official KITTI devkit cross-check

Selected conditions are cross-checked with the official KITTI odometry devkit wrapper:

    python experiments/orbslam3/kitti_patch_stress/shared/evaluation/run_kitti_official_devkit_eval.py \
      --seq 00 \
      --condition checkerboard05_top_left \
      --prediction results/official_kitti_eval_inputs/kitti00_checkerboard05_top_left/predictions/00.txt \
      --groundtruth results/official_kitti_eval_inputs/kitti00_checkerboard05_top_left/groundtruth/00.txt

The official devkit summaries are copied into:

- `experiments/orbslam3/kitti_patch_stress/results_summary/official_devkit/`

## Step 6: Mechanism diagnostics

Run ORB keypoint diagnostics:

    python experiments/orbslam3/kitti_patch_stress/shared/diagnostics/orb_patch_feature_diagnostics.py \
      --frame 000120 \
      --clean data/kitti/dataset/sequences/00/image_0/000120.png \
      --black10 data/kitti_attacks/seq00_black_10pct_top_left_leftonly/image_0/000120.png \
      --checkerboard5 data/kitti_attacks/seq00_checkerboard_05pct_top_left_leftonly/image_0/000120.png \
      --checkerboard10 data/kitti_attacks/seq00_checkerboard_10pct_top_left_leftonly/image_0/000120.png \
      --outdir local_mechanism/orb_features/kitti00_frame000120 \
      --nfeatures 2000

Run ORB match diagnostics:

    python experiments/orbslam3/kitti_patch_stress/shared/diagnostics/orb_patch_match_diagnostics.py \
      --frame-a 000120 \
      --frame-b 000121 \
      --clean-dir data/kitti/dataset/sequences/00/image_0 \
      --black10-dir data/kitti_attacks/seq00_black_10pct_top_left_leftonly/image_0 \
      --checkerboard5-dir data/kitti_attacks/seq00_checkerboard_05pct_top_left_leftonly/image_0 \
      --checkerboard10-dir data/kitti_attacks/seq00_checkerboard_10pct_top_left_leftonly/image_0 \
      --outdir local_mechanism/orb_matches/kitti00_000120_000121 \
      --nfeatures 5000

Raw mechanism outputs remain local. Curated summaries and selected figures are copied into:

- `experiments/orbslam3/kitti_patch_stress/results_summary/mechanism/`
- `experiments/orbslam3/kitti_patch_stress/figures/mechanism/`

## Step 7: Audit committed artifacts

Run:

    python experiments/orbslam3/kitti_patch_stress/experiments/orbslam3/kitti_patch_stress/scripts/audit_patch_attack_results.py

The audit should pass before new systems are added.

## Current interpretation

The safe interpretation is:

Checkerboard patches induce a threshold-like transition into a high-variance catastrophic drift regime, while black occlusion patches remain near baseline.

Do not claim a clean monotonic dose-response curve.

Do not claim physical-world validation.

Do not claim the OpenCV ORB diagnostic is a direct dump of ORB-SLAM3 internal frontend state.

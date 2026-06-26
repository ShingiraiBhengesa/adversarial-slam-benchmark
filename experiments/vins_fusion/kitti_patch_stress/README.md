# VINS-Fusion KITTI Patch Stress Test

## Purpose

This experiment tests whether the ORB-SLAM3 checkerboard patch result transfers to another visual odometry / SLAM system.

The pilot compares VINS-Fusion stereo odometry on KITTI under three conditions:

- clean KITTI images
- black 10% top-left patch
- checkerboard 5% top-left patch

The goal is not to run a full sweep yet. The goal is to test whether the same black-vs-checkerboard separation appears outside ORB-SLAM3.

## System

- SLAM / odometry system: VINS-Fusion
- Mode: stereo
- Dataset: KITTI Odometry
- Initial sequence: 00
- Patch location: top-left
- Modified camera: left camera only
- Pilot conditions:
  - clean
  - black 10% top-left
  - checkerboard 5% top-left

## Why this system is next

VINS-Fusion is a good second-system test because it is still a classical geometry-based system, but it is not ORB-SLAM3. If checkerboard patches also hurt VINS-Fusion while black patches remain near baseline, the result becomes stronger than an ORB-SLAM3-only finding.

## Folder layout

- `docs/`
  - writeups and result notes

- `figures/`
  - selected figures only

- `results_summary/`
  - curated JSON, CSV, and markdown summaries

- `scripts/`
  - VINS-Fusion-specific run scripts

- `manifests/`
  - pilot condition lists and run records

- `archive/`
  - old notes and intermediate drafts

Shared benchmark code lives in:

- `../../../shared/patching/`
- `../../../shared/evaluation/`
- `../../../shared/diagnostics/`
- `../../../shared/plotting/`

## Important rule

Do not run a full severity sweep first.

Start with the small pilot:

| Condition | Sequence | Repeats |
|---|---|---:|
| clean | KITTI 00 | 3 |
| black 10% top-left | KITTI 00 | 3 |
| checkerboard 5% top-left | KITTI 00 | 3 |

Only expand if the pilot shows useful signal.

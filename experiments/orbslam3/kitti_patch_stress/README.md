# ORB-SLAM3 KITTI Patch Stress Test

## Purpose

This experiment block evaluates whether controlled digital image-plane patches degrade ORB-SLAM3 stereo odometry on KITTI.

The central comparison is:

- black patch: low-texture occlusion control
- checkerboard patch: high-texture feature-injection perturbation

## Current status

This is the first validated system-level experiment in the benchmark.

## System

- SLAM system: ORB-SLAM3
- Mode: stereo
- Dataset: KITTI Odometry
- Sequences: 00 and 02
- Camera modified: left camera only
- Patch location: top-left
- Patch types: black, checkerboard

## Canonical documents

- Main results: `../../../docs/attacks/main_results_narrative.md`
- Mechanism summary: `../../../docs/attacks/orb_feature_match_mechanism_summary.md`
- Attack docs index: `../../../docs/attacks/README.md`

## Canonical scripts

- Patch generation: `../../../scripts/create_kitti_patch_attack.py`
- ORB-SLAM3 KITTI condition runner: `../../../scripts/run_orbslam3_kitti_condition.sh`
- ATE evaluator: `../../../scripts/evaluate_kitti_ate.py`
- KITTI segment evaluator: `../../../scripts/evaluate_kitti_segments.py`
- Official KITTI devkit wrapper: `../../../scripts/run_kitti_official_devkit_eval.py`
- Result audit: `../../../scripts/audit_patch_attack_results.py`
- ORB keypoint diagnostic: `../../../scripts/orb_patch_feature_diagnostics.py`
- ORB match diagnostic: `../../../scripts/orb_patch_match_diagnostics.py`

## Important caveats

These are digital image-plane patch stress tests. They should not be described as physically validated adversarial patches.

The ORB keypoint and match diagnostics use OpenCV ORB as a proxy. They are not a direct dump of ORB-SLAM3 internal frontend state.

## Next extension

After this ORB-SLAM3 block is organized and audited, the next system-level experiment should test transfer to a second SLAM system using a minimal pilot:

- clean
- black 10%
- checkerboard 5%

Do not begin a full severity sweep on the next system until the pilot shows useful signal.

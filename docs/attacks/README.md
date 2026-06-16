# Patch Attack Experiments

This directory documents the KITTI digital patch stress tests against ORB-SLAM3 stereo odometry.

## Main result

A low-texture black patch behaves like an occlusion control and remains close to the clean baseline. A high-texture checkerboard patch causes large trajectory drift and tracking/map instability. This supports the claim that the failure mechanism is not simple occlusion but feature and match corruption.

## Key documents

- `main_results_narrative.md`: paper-style summary of the main KITTI 00 and KITTI 02 results.
- `severity_onset_kitti00_checkerboard_top_left.md`: onset analysis across checkerboard patch sizes.
- `patch_match_diagnostics.md`: temporal and stereo match diagnostics for patch locations.
- `trajectory_visualization_summary.md`: qualitative trajectory plot summary.

## Main figures

- `../figures/kitti00_trajectory_clean_black_checkerboard.png`
- `../figures/kitti02_trajectory_clean_black_checkerboard.png`

## Important caveat

These experiments use digital image-plane patches inserted into KITTI images. They should be described as controlled digital stress tests, not physically validated adversarial patches.

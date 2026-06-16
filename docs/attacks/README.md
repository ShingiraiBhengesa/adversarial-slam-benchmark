# ORB-SLAM3 KITTI Patch Results

Read these files in this order.

## 1. Main result

- `main_results_narrative.md`

This explains the main ORB-SLAM3 result:

- clean and black-patch runs stay close to baseline
- checkerboard patches cause large drift
- KITTI devkit checks agree with the internal evaluation

## 2. Why the checkerboard hurts

- `orb_feature_match_mechanism_summary.md`

This explains the ORB keypoint and match checks.

The short version:

- black patches remove visual content
- checkerboard patches add many strong features
- those features attract many ORB keypoints and matches
- this supports the feature-injection explanation

## 3. Extra result checks

- `official_kitti_devkit_results.md`
- `severity_onset_kitti00_checkerboard_top_left.md`
- `trajectory_visualization_summary.md`

## 4. Older notes

Older detailed notes are in:

- `archive/`

They are kept for record-keeping, but they are not the best place to start.

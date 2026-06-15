# ORB-SLAM3 KITTI 00 Baseline

## Dataset

- Dataset: KITTI Odometry sequence 00
- Images: grayscale stereo
- Frames: 4541
- Ground truth: `data/kitti/dataset/poses/00.txt`

## ORB-SLAM3 stereo run

- System: ORB-SLAM3 stereo
- Run directory: `results/baselines/orbslam3/kitti00_stereo/run_20260615_040140`
- Output trajectory: `CameraTrajectory.txt`
- Evaluated poses: 4541 / 4541
- Tracking:
  - Median tracking time: 0.0339122 s
  - Mean tracking time: 0.0433912 s
- Status: completed successfully; trajectory saved.

## ATE evaluation

- Evaluation script: `scripts/evaluate_kitti_ate.py`
- Alignment: first-pose SE(3)
- ATE RMSE: 7.392536673666279 m
- ATE mean: 6.670887441208109 m
- ATE median: 6.393424498288834 m
- ATE min: 0.0 m
- ATE max: 12.3034192989908 m
- ATE std: 3.1857274237186126 m

## Notes

This is a first baseline metric, not the final benchmark metric. For paper-quality reporting, add path-length-normalized drift and KITTI-style segment errors.

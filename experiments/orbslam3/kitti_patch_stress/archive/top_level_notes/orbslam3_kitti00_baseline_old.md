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

- Evaluation script: `shared/evaluation/evaluate_kitti_ate.py`
- Alignment: first_pose_SE3
- Ground-truth path length: 3724.186990597451 m
- ATE RMSE: 7.392536673666279 m
- ATE RMSE / path length: 0.19850068464151785%
- ATE mean: 6.670887441208109 m
- ATE median: 6.393424498288834 m
- ATE min: 0.0 m
- ATE max: 12.3034192989908 m
- ATE std: 3.1857274237186126 m

## KITTI-style segment drift evaluation

- Evaluation script: `shared/evaluation/evaluate_kitti_segments.py`
- Step size: 10 frames
- Segment lengths: 100, 200, 300, 400, 500, 600, 700, 800 m
- Total evaluated segments: 3283
- Mean translation drift: 0.6841217835324649%
- Mean rotation drift: 0.24809458838244688 deg / 100 m

### Segment drift by length

| Segment length (m) | Segments | Translation drift mean (%) | Rotation drift mean (deg / 100m) |
|---:|---:|---:|---:|
| 100 | 445 | 0.987814784136025 | 0.6016933840204027 |
| 200 | 431 | 0.8590768815095163 | 0.3414405097478553 |
| 300 | 424 | 0.761081898090764 | 0.24501187090915086 |
| 400 | 416 | 0.6996377250663942 | 0.20347593788745927 |
| 500 | 408 | 0.6419971711518848 | 0.16675679140054184 |
| 600 | 399 | 0.5602735943147875 | 0.14535504443232472 |
| 700 | 385 | 0.48137054613414626 | 0.12093399132310226 |
| 800 | 375 | 0.4041930981990148 | 0.10254953163517916 |

## Notes

This is a first baseline metric set. For paper-quality reporting, label the segment results as KITTI-style unless cross-checked against the official KITTI odometry evaluator.

## Five-run baseline repeat summary

- Repeats: 5
- ATE RMSE: 7.206066747824011 ± 0.47158506731930333 m
- ATE RMSE / path length: 0.19349368777715376 ± 0.012662765551513012%
- KITTI-style mean translation drift: 0.6786799488134423 ± 0.0015298720393951606%
- KITTI-style mean rotation drift: 0.2524391721734871 ± 0.003485820137255906 deg / 100 m

### Repeat run directories

- `/home/sbhengesa/research/adversarial-slam-benchmark/results/baselines/orbslam3/kitti00_stereo/run_repeat_1_20260615_045541`
- `/home/sbhengesa/research/adversarial-slam-benchmark/results/baselines/orbslam3/kitti00_stereo/run_repeat_2_20260615_045541`
- `/home/sbhengesa/research/adversarial-slam-benchmark/results/baselines/orbslam3/kitti00_stereo/run_repeat_3_20260615_045541`
- `/home/sbhengesa/research/adversarial-slam-benchmark/results/baselines/orbslam3/kitti00_stereo/run_repeat_4_20260615_045541`
- `/home/sbhengesa/research/adversarial-slam-benchmark/results/baselines/orbslam3/kitti00_stereo/run_repeat_5_20260615_045541`

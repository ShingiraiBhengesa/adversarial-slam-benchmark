# Environment Record

Every system, dataset, dependency, and reused attack repository must be version-pinned.

## Machine

- Machine name: SLU Libra cluster login01
- Local / cluster: cluster
- OS: Red Hat Enterprise Linux 9.7 (Plow)
- CPU: TBD from compute node
- GPU: not visible on login node; TBD from GPU job
- RAM: TBD from compute node
- CUDA: 12.8.93 via module cuda12.8/toolkit/12.8.1
- NVIDIA driver: TBD from GPU node
- Python: 3.12.11
- Conda: 25.7.0
- Compiler: GCC 14.2.0 via cluster module
- CMake: 4.1.2 via module cmake/4.1.2

## Python packages

- evo: 1.36.5
- numpy: 2.2.6
- pandas: 2.3.3
- matplotlib: 3.10.9
- opencv-python: 4.13.0
- torch: not installed yet
- torchvision: not installed yet

## SLAM systems

### ORB-SLAM3

- Repository: https://github.com/UZ-SLAMLab/ORB_SLAM3.git
- Commit hash: 4452a3c4ab75b1cde34e5505a36ec3f9edcdc4c4
- Build date: not built yet
- Notes: cloned under systems/ORB_SLAM3; external repo is gitignored

### DROID-SLAM

- Repository:
- Commit hash:
- Build date:
- CUDA/PyTorch notes:

## Datasets

### TUM RGB-D

- fr1/desk:
- fr1/room:
- Download date:
- Source URL:
- Notes:

## Evaluation

- evo version:
- ATE command:
- RPE command:
- Alignment mode:

## Attack scripts

- Occlusion script version:
- Texture script version:
- Severity definition:

## Conda build dependencies for ORB-SLAM3

- Environment name: slam-bench
- Python: 3.10.20
- CMake: 4.3.3 from conda-forge
- Make: 4.4.1 from conda-forge
- Ninja: 1.13.2 from conda-forge
- pkg-config: 0.29.2 from conda-forge
- Eigen: 3.4.0 from conda-forge
- OpenCV: 4.13.0 from conda-forge
- Pangolin: pangolin-opengl 0.9.5 from conda-forge
- Boost: 1.82.0 from conda-forge

Note: Cluster OpenCV module opencv/4.10.0-gcc-13.1.0-jxdnl was checked but not used because it was built with key ORB-SLAM3-required OpenCV modules disabled, including calib3d, features2d, imgproc, highgui, and imgcodecs.

cmake_minimum_required(VERSION 3.10)
project(kitti_odometry_devkit_eval CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(eval_odometry_local
  evaluate_odometry.cpp
  matrix.cpp
)

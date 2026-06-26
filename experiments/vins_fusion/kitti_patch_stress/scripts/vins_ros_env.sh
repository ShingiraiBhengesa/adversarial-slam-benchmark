#!/usr/bin/env bash
# Source this file before building or running VINS-Fusion on the cluster.
#
# Usage:
#   source experiments/vins_fusion/kitti_patch_stress/scripts/vins_ros_env.sh

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "ERROR: This script must be sourced, not executed."
  echo "Use:"
  echo "  source experiments/vins_fusion/kitti_patch_stress/scripts/vins_ros_env.sh"
  exit 1
fi

source /cm/shared/apps/anaconda/miniforge3/etc/profile.d/conda.sh

export CONDA_ENVS_PATH=/home/sbhengesa/.conda/envs
export CONDA_PKGS_DIRS=/home/sbhengesa/.conda/pkgs

conda activate /home/sbhengesa/.conda/envs/vins-ros-test

export ROS_DISTRO=noetic
export ROS_MASTER_URI=http://localhost:11311
export ROS_HOSTNAME=localhost

echo "VINS-Fusion ROS environment activated."
echo "CONDA_PREFIX=$CONDA_PREFIX"
echo "ROS_DISTRO=$ROS_DISTRO"
echo "ROS_MASTER_URI=$ROS_MASTER_URI"
echo "ROS_HOSTNAME=$ROS_HOSTNAME"

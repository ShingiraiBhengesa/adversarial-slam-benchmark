#!/usr/bin/env bash
# Source this after activating the slam-bench conda environment:
#   conda activate slam-bench
#   source experiments/orbslam3/kitti_patch_stress/scripts/orbslam3_env.sh

if [ -z "${CONDA_PREFIX:-}" ]; then
  echo "ERROR: CONDA_PREFIX is not set. Run: conda activate slam-bench"
  return 1 2>/dev/null || exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ORB_SLAM3_ROOT="$REPO_ROOT/systems/ORB_SLAM3"
export ORB_SLAM3_VOCAB="$ORB_SLAM3_ROOT/Vocabulary/ORBvoc.txt"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$ORB_SLAM3_ROOT/lib:$ORB_SLAM3_ROOT/Thirdparty/DBoW2/lib:$ORB_SLAM3_ROOT/Thirdparty/g2o/lib:${LD_LIBRARY_PATH:-}"

echo "ORB_SLAM3_ROOT=$ORB_SLAM3_ROOT"
echo "ORB_SLAM3_VOCAB=$ORB_SLAM3_VOCAB"

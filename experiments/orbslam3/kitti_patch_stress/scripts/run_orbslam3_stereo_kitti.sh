#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   conda activate slam-bench
#   source experiments/orbslam3/kitti_patch_stress/scripts/orbslam3_env.sh
#   bash experiments/orbslam3/kitti_patch_stress/scripts/run_orbslam3_stereo_kitti.sh <KITTI_SEQUENCE_DIR> <KITTI_SETTINGS_YAML>
#
# Example:
#   bash experiments/orbslam3/kitti_patch_stress/scripts/run_orbslam3_stereo_kitti.sh data/kitti/dataset/sequences/00 systems/ORB_SLAM3/Examples/Stereo/KITTI00-02.yaml

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <KITTI_SEQUENCE_DIR> <KITTI_SETTINGS_YAML>"
  exit 1
fi

KITTI_SEQUENCE_DIR="$1"
SETTINGS_YAML="$2"

if [ -z "${ORB_SLAM3_ROOT:-}" ]; then
  echo "ERROR: ORB_SLAM3_ROOT is not set. Run: source experiments/orbslam3/kitti_patch_stress/scripts/orbslam3_env.sh"
  exit 1
fi

if [ ! -f "$ORB_SLAM3_VOCAB" ]; then
  echo "ERROR: ORB vocabulary not found: $ORB_SLAM3_VOCAB"
  exit 1
fi

if [ ! -d "$KITTI_SEQUENCE_DIR/image_0" ]; then
  echo "ERROR: missing image_0 directory: $KITTI_SEQUENCE_DIR/image_0"
  exit 1
fi

if [ ! -d "$KITTI_SEQUENCE_DIR/image_1" ]; then
  echo "ERROR: missing image_1 directory: $KITTI_SEQUENCE_DIR/image_1"
  exit 1
fi

if [ ! -f "$KITTI_SEQUENCE_DIR/times.txt" ]; then
  echo "ERROR: missing times.txt: $KITTI_SEQUENCE_DIR/times.txt"
  exit 1
fi

if [ ! -f "$SETTINGS_YAML" ]; then
  echo "ERROR: settings YAML not found: $SETTINGS_YAML"
  exit 1
fi

echo "ORB_SLAM3_ROOT=$ORB_SLAM3_ROOT"
echo "ORB_SLAM3_VOCAB=$ORB_SLAM3_VOCAB"
echo "KITTI_SEQUENCE_DIR=$KITTI_SEQUENCE_DIR"
echo "SETTINGS_YAML=$SETTINGS_YAML"

"$ORB_SLAM3_ROOT/Examples/Stereo/stereo_kitti" \
  "$ORB_SLAM3_VOCAB" \
  "$SETTINGS_YAML" \
  "$KITTI_SEQUENCE_DIR"

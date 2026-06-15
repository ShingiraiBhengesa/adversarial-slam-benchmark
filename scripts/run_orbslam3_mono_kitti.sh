#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   conda activate slam-bench
#   source scripts/orbslam3_env.sh
#   bash scripts/run_orbslam3_mono_kitti.sh <KITTI_SEQUENCE_DIR> <KITTI_SETTINGS_YAML>
#
# Example:
#   bash scripts/run_orbslam3_mono_kitti.sh data/kitti/sequences/00 systems/ORB_SLAM3/Examples/Monocular/KITTI00-02.yaml

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <KITTI_SEQUENCE_DIR> <KITTI_SETTINGS_YAML>"
  exit 1
fi

KITTI_SEQUENCE_DIR="$1"
SETTINGS_YAML="$2"

if [ -z "${ORB_SLAM3_ROOT:-}" ]; then
  echo "ERROR: ORB_SLAM3_ROOT is not set. Run: source scripts/orbslam3_env.sh"
  exit 1
fi

if [ ! -f "$ORB_SLAM3_VOCAB" ]; then
  echo "ERROR: ORB vocabulary not found: $ORB_SLAM3_VOCAB"
  exit 1
fi

if [ ! -d "$KITTI_SEQUENCE_DIR" ]; then
  echo "ERROR: KITTI sequence directory not found: $KITTI_SEQUENCE_DIR"
  exit 1
fi

if [ ! -f "$SETTINGS_YAML" ]; then
  echo "ERROR: settings file not found: $SETTINGS_YAML"
  exit 1
fi

echo "ORB_SLAM3_ROOT=$ORB_SLAM3_ROOT"
echo "ORB_SLAM3_VOCAB=$ORB_SLAM3_VOCAB"
echo "KITTI_SEQUENCE_DIR=$KITTI_SEQUENCE_DIR"
echo "SETTINGS_YAML=$SETTINGS_YAML"

"$ORB_SLAM3_ROOT/Examples/Monocular/mono_kitti" \
  "$ORB_SLAM3_VOCAB" \
  "$SETTINGS_YAML" \
  "$KITTI_SEQUENCE_DIR"

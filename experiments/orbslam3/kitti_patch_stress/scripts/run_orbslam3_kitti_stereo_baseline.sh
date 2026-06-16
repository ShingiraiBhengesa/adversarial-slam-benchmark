#!/usr/bin/env bash
set -euo pipefail

SEQ="${1:-02}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ORB_SLAM3_ROOT="$REPO_ROOT/systems/ORB_SLAM3"
ORB_SLAM3_VOCAB="$ORB_SLAM3_ROOT/Vocabulary/ORBvoc.txt"
KITTI_SEQUENCE_DIR="$REPO_ROOT/data/kitti/dataset/sequences/$SEQ"
KITTI_GT="$REPO_ROOT/data/kitti/dataset/poses/${SEQ}.txt"

case "$SEQ" in
  00|01|02)
    SETTINGS_YAML="$ORB_SLAM3_ROOT/Examples/Stereo/KITTI00-02.yaml"
    ;;
  03)
    SETTINGS_YAML="$ORB_SLAM3_ROOT/Examples/Stereo/KITTI03.yaml"
    ;;
  *)
    SETTINGS_YAML="$ORB_SLAM3_ROOT/Examples/Stereo/KITTI04-12.yaml"
    ;;
esac

STAMP="$(date +%Y%m%d_%H%M%S)"

if [[ -n "${SLURM_ARRAY_TASK_ID:-}" ]]; then
  RUN_NAME="run_repeat_${SLURM_ARRAY_TASK_ID}_${STAMP}"
elif [[ -n "${REPEAT_ID:-}" ]]; then
  RUN_NAME="run_repeat_${REPEAT_ID}_${STAMP}"
else
  RUN_NAME="run_${STAMP}"
fi

RUN_DIR="$REPO_ROOT/results/baselines/orbslam3/kitti${SEQ}_stereo/$RUN_NAME"
mkdir -p "$RUN_DIR"

echo "=== ORB-SLAM3 KITTI $SEQ STEREO BASELINE ==="
echo "REPO_ROOT=$REPO_ROOT"
echo "RUN_DIR=$RUN_DIR"
echo "KITTI_SEQUENCE_DIR=$KITTI_SEQUENCE_DIR"
echo "KITTI_GT=$KITTI_GT"
echo "SETTINGS_YAML=$SETTINGS_YAML"
echo "DATE=$(date)"
echo "HOSTNAME=$(hostname)"
echo ""

echo "=== PRECHECKS ==="
test -x "$ORB_SLAM3_ROOT/Examples/Stereo/stereo_kitti"
test -f "$ORB_SLAM3_VOCAB"
test -d "$KITTI_SEQUENCE_DIR/image_0"
test -d "$KITTI_SEQUENCE_DIR/image_1"
test -f "$KITTI_GT"
test -f "$SETTINGS_YAML"

pushd "$RUN_DIR" >/dev/null

echo "=== RUN ORB-SLAM3 ==="
"$ORB_SLAM3_ROOT/Examples/Stereo/stereo_kitti" \
  "$ORB_SLAM3_VOCAB" \
  "$SETTINGS_YAML" \
  "$KITTI_SEQUENCE_DIR" \
  > orbslam3_stdout.log \
  2> orbslam3_stderr.log

echo ""
echo "=== TRAJECTORY CHECK ==="
wc -l CameraTrajectory.txt
ls -lh CameraTrajectory.txt

popd >/dev/null

echo ""
echo "=== EVALUATE ATE ==="
python "$REPO_ROOT/experiments/orbslam3/kitti_patch_stress/scripts/evaluate_kitti_ate.py" \
  --estimate "$RUN_DIR/CameraTrajectory.txt" \
  --groundtruth "$KITTI_GT" \
  --output-json "$RUN_DIR/ate_metrics.json"

echo ""
echo "=== EVALUATE KITTI-STYLE SEGMENT DRIFT ==="
python "$REPO_ROOT/experiments/orbslam3/kitti_patch_stress/scripts/evaluate_kitti_segments.py" \
  --estimate "$RUN_DIR/CameraTrajectory.txt" \
  --groundtruth "$KITTI_GT" \
  --output-json "$RUN_DIR/kitti_segment_metrics.json"

echo ""
echo "=== WRITE SUMMARY ==="
export RUN_DIR
python - <<'PY'
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR"])
ate = json.loads((run_dir / "ate_metrics.json").read_text())
seg = json.loads((run_dir / "kitti_segment_metrics.json").read_text())

summary = {
    "run_dir": str(run_dir),
    "trajectory": str(run_dir / "CameraTrajectory.txt"),
    "frames_evaluated": ate["num_evaluated_poses"],
    "gt_path_length_m": ate["gt_path_length_m"],
    "ate_rmse_m": ate["ate_rmse_m"],
    "ate_rmse_percent_of_path": ate["ate_rmse_percent_of_path"],
    "ate_mean_m": ate["ate_mean_m"],
    "ate_median_m": ate["ate_median_m"],
    "segment_translation_error_percent_mean": seg["translation_error_percent_mean"],
    "segment_rotation_error_deg_per_100m_mean": seg["rotation_error_deg_per_100m_mean"],
    "num_segments_total": seg["num_segments_total"],
}

(run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
PY

echo ""
echo "=== OUTPUT FILES ==="
ls -lh "$RUN_DIR"

echo ""
echo "=== DONE ==="
date

#!/usr/bin/env bash
set -euo pipefail

# Runs ORB-SLAM3 stereo on KITTI odometry sequence 00, then evaluates:
#   1. first-pose-aligned ATE
#   2. KITTI-style segment drift
#
# Usage:
#   bash scripts/run_orbslam3_kitti00_stereo_baseline.sh
#
# Optional:
#   RUN_TAG=my_run_name bash scripts/run_orbslam3_kitti00_stereo_baseline.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -z "${CONDA_PREFIX:-}" ]; then
  if [ -f /cm/shared/apps/anaconda/miniforge3/etc/profile.d/conda.sh ]; then
    source /cm/shared/apps/anaconda/miniforge3/etc/profile.d/conda.sh
    conda activate slam-bench
  else
    echo "ERROR: CONDA_PREFIX is not set and conda.sh was not found."
    echo "Run: conda activate slam-bench"
    exit 1
  fi
fi

source "$REPO_ROOT/scripts/orbslam3_env.sh"

RUN_TAG="${RUN_TAG:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="$REPO_ROOT/results/baselines/orbslam3/kitti00_stereo/run_${RUN_TAG}"

KITTI_SEQUENCE_DIR="$REPO_ROOT/data/kitti/dataset/sequences/00"
KITTI_GT="$REPO_ROOT/data/kitti/dataset/poses/00.txt"
SETTINGS_YAML="$REPO_ROOT/systems/ORB_SLAM3/Examples/Stereo/KITTI00-02.yaml"
TRAJECTORY_FILE="$RUN_DIR/CameraTrajectory.txt"
ATE_JSON="$RUN_DIR/ate_metrics.json"
SEGMENT_JSON="$RUN_DIR/kitti_segment_metrics.json"
SUMMARY_JSON="$RUN_DIR/run_summary.json"
SUMMARY_MD="$RUN_DIR/run_summary.md"

echo "=== ORB-SLAM3 KITTI 00 STEREO BASELINE ==="
echo "REPO_ROOT=$REPO_ROOT"
echo "RUN_DIR=$RUN_DIR"
echo "KITTI_SEQUENCE_DIR=$KITTI_SEQUENCE_DIR"
echo "KITTI_GT=$KITTI_GT"
echo "SETTINGS_YAML=$SETTINGS_YAML"

echo ""
echo "=== PRECHECKS ==="
test -x "$ORB_SLAM3_ROOT/Examples/Stereo/stereo_kitti"
test -f "$ORB_SLAM3_VOCAB"
test -d "$KITTI_SEQUENCE_DIR"
test -f "$KITTI_GT"
test -f "$SETTINGS_YAML"
test -x "$REPO_ROOT/scripts/run_orbslam3_stereo_kitti.sh"
test -f "$REPO_ROOT/scripts/evaluate_kitti_ate.py"
test -f "$REPO_ROOT/scripts/evaluate_kitti_segments.py"

mkdir -p "$RUN_DIR"

cat > "$RUN_DIR/run_metadata.txt" <<META
date=$(date)
hostname=$(hostname)
repo_root=$REPO_ROOT
run_dir=$RUN_DIR
orb_slam3_root=$ORB_SLAM3_ROOT
orb_slam3_vocab=$ORB_SLAM3_VOCAB
kitti_sequence_dir=$KITTI_SEQUENCE_DIR
kitti_gt=$KITTI_GT
settings_yaml=$SETTINGS_YAML
conda_prefix=${CONDA_PREFIX:-}
META

echo ""
echo "=== RUN ORB-SLAM3 ==="
cd "$RUN_DIR"

set +e
bash "$REPO_ROOT/scripts/run_orbslam3_stereo_kitti.sh" \
  "$KITTI_SEQUENCE_DIR" \
  "$SETTINGS_YAML" \
  > "$RUN_DIR/orbslam3_stdout.log" \
  2> "$RUN_DIR/orbslam3_stderr.log"
ORB_STATUS=$?
set -e

echo "ORB_STATUS=$ORB_STATUS"

if [ "$ORB_STATUS" -ne 0 ]; then
  echo "ERROR: ORB-SLAM3 run failed. See:"
  echo "  $RUN_DIR/orbslam3_stdout.log"
  echo "  $RUN_DIR/orbslam3_stderr.log"
  exit "$ORB_STATUS"
fi

if [ ! -f "$TRAJECTORY_FILE" ]; then
  echo "ERROR: Expected trajectory file not found: $TRAJECTORY_FILE"
  exit 1
fi

echo ""
echo "=== TRAJECTORY CHECK ==="
wc -l "$TRAJECTORY_FILE"
ls -lh "$TRAJECTORY_FILE"

echo ""
echo "=== EVALUATE ATE ==="
cd "$REPO_ROOT"
python "$REPO_ROOT/scripts/evaluate_kitti_ate.py" \
  --estimate "$TRAJECTORY_FILE" \
  --groundtruth "$KITTI_GT" \
  --output-json "$ATE_JSON"

echo ""
echo "=== EVALUATE KITTI-STYLE SEGMENT DRIFT ==="
python "$REPO_ROOT/scripts/evaluate_kitti_segments.py" \
  --estimate "$TRAJECTORY_FILE" \
  --groundtruth "$KITTI_GT" \
  --output-json "$SEGMENT_JSON"

echo ""
echo "=== WRITE SUMMARY ==="
python - <<PY
import json
from pathlib import Path

run_dir = Path("$RUN_DIR")
ate = json.loads(Path("$ATE_JSON").read_text())
seg = json.loads(Path("$SEGMENT_JSON").read_text())

summary = {
    "run_dir": str(run_dir),
    "trajectory": "$TRAJECTORY_FILE",
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

Path("$SUMMARY_JSON").write_text(json.dumps(summary, indent=2) + "\n")

md = f"""# ORB-SLAM3 KITTI 00 Stereo Baseline Run

- Run directory: {run_dir}
- Frames evaluated: {summary["frames_evaluated"]}
- Ground-truth path length: {summary["gt_path_length_m"]} m
- ATE RMSE: {summary["ate_rmse_m"]} m
- ATE RMSE / path length: {summary["ate_rmse_percent_of_path"]}%
- ATE mean: {summary["ate_mean_m"]} m
- ATE median: {summary["ate_median_m"]} m
- KITTI-style mean translation drift: {summary["segment_translation_error_percent_mean"]}%
- KITTI-style mean rotation drift: {summary["segment_rotation_error_deg_per_100m_mean"]} deg / 100 m
- Total evaluated segments: {summary["num_segments_total"]}

## Files

- CameraTrajectory.txt
- ate_metrics.json
- kitti_segment_metrics.json
- run_summary.json
- orbslam3_stdout.log
- orbslam3_stderr.log

## Note

Segment drift is KITTI-style unless cross-checked against the official KITTI odometry evaluator.
"""
Path("$SUMMARY_MD").write_text(md)
print(json.dumps(summary, indent=2))
PY

echo ""
echo "=== OUTPUT FILES ==="
ls -lh "$RUN_DIR"

echo ""
echo "=== DONE ==="
echo "Run summary:"
cat "$SUMMARY_JSON"

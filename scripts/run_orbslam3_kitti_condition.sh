#!/usr/bin/env bash
set -euo pipefail

SEQ_ID="${1:?Usage: SEQ_ID CONDITION_NAME SEQUENCE_DIR REPEAT}"
CONDITION_NAME="${2:?Usage: SEQ_ID CONDITION_NAME SEQUENCE_DIR REPEAT}"
SEQUENCE_DIR="${3:?Usage: SEQ_ID CONDITION_NAME SEQUENCE_DIR REPEAT}"
REPEAT="${4:-1}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if command -v conda >/dev/null 2>&1; then
  CONDA_BASE="$(conda info --base)"
  source "$CONDA_BASE/etc/profile.d/conda.sh"
  conda activate slam-bench || true
fi

ORB_SLAM3_ROOT="$REPO_ROOT/systems/ORB_SLAM3"
ORB_SLAM3_VOCAB="$ORB_SLAM3_ROOT/Vocabulary/ORBvoc.txt"
SETTINGS_YAML="$ORB_SLAM3_ROOT/Examples/Stereo/KITTI00-02.yaml"
KITTI_GT="$REPO_ROOT/data/kitti/dataset/poses/${SEQ_ID}.txt"
SEQ_ABS="$(realpath "$SEQUENCE_DIR")"

RUN_ROOT="$REPO_ROOT/results/generalization/orbslam3/kitti${SEQ_ID}/${CONDITION_NAME}"
RUN_DIR="$RUN_ROOT/run_repeat_${REPEAT}_$(date +%Y%m%d_%H%M%S)_job${SLURM_JOB_ID:-manual}_pid$$"
mkdir -p "$RUN_DIR"

echo "=== ORB-SLAM3 KITTI CONDITION RUN ==="
echo "SEQ_ID=$SEQ_ID"
echo "CONDITION_NAME=$CONDITION_NAME"
echo "SEQUENCE_DIR=$SEQ_ABS"
echo "RUN_DIR=$RUN_DIR"
echo "KITTI_GT=$KITTI_GT"

test -x "$ORB_SLAM3_ROOT/Examples/Stereo/stereo_kitti"
test -f "$ORB_SLAM3_VOCAB"
test -f "$SETTINGS_YAML"
test -f "$KITTI_GT"
test -d "$SEQ_ABS/image_0"
test -d "$SEQ_ABS/image_1"

pushd "$RUN_DIR" >/dev/null
set +e
"$ORB_SLAM3_ROOT/Examples/Stereo/stereo_kitti" \
  "$ORB_SLAM3_VOCAB" \
  "$SETTINGS_YAML" \
  "$SEQ_ABS" \
  > orbslam3_stdout.log \
  2> orbslam3_stderr.log
ORB_STATUS=$?
set -e
popd >/dev/null

echo "ORB_STATUS=$ORB_STATUS"

TRAJ="$RUN_DIR/CameraTrajectory.txt"
if [[ ! -s "$TRAJ" ]]; then
  echo "ERROR: missing CameraTrajectory.txt"
  tail -n 120 "$RUN_DIR/orbslam3_stdout.log" || true
  tail -n 120 "$RUN_DIR/orbslam3_stderr.log" || true
  exit 2
fi

echo "=== TRAJECTORY CHECK ==="
wc -l "$TRAJ"
ls -lh "$TRAJ"

python scripts/evaluate_kitti_ate.py \
  --estimate "$TRAJ" \
  --groundtruth "$KITTI_GT" \
  --output-json "$RUN_DIR/ate_metrics.json"

python scripts/evaluate_kitti_segments.py \
  --estimate "$TRAJ" \
  --groundtruth "$KITTI_GT" \
  --output-json "$RUN_DIR/kitti_segment_metrics.json"

export RUN_DIR TRAJ CONDITION_NAME SEQ_ID SEQ_ABS

python - <<'PY'
import json, os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR"])
ate = json.loads((run_dir / "ate_metrics.json").read_text())
seg = json.loads((run_dir / "kitti_segment_metrics.json").read_text())

summary = {
    "seq_id": os.environ["SEQ_ID"],
    "condition_name": os.environ["CONDITION_NAME"],
    "sequence_dir": os.environ["SEQ_ABS"],
    "run_dir": str(run_dir),
    "num_est_poses": ate["num_est_poses"],
    "num_evaluated_poses": ate["num_evaluated_poses"],
    "ate_rmse_m": ate["ate_rmse_m"],
    "ate_rmse_percent_of_path": ate["ate_rmse_percent_of_path"],
    "segment_translation_error_percent_mean": seg["translation_error_percent_mean"],
    "segment_rotation_error_deg_per_100m_mean": seg["rotation_error_deg_per_100m_mean"],
    "num_segments_total": seg["num_segments_total"],
}

(run_dir / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
PY

echo "=== DONE ==="

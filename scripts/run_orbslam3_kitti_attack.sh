#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/run_orbslam3_kitti_attack.sh <ATTACK_NAME> <ATTACK_SEQUENCE_DIR>
#
# Example:
#   bash scripts/run_orbslam3_kitti_attack.sh \
#     seq00_checkerboard_5pct_bottom_right_leftonly \
#     data/kitti_attacks/seq00_checkerboard_5pct_bottom_right_leftonly

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <ATTACK_NAME> <ATTACK_SEQUENCE_DIR>"
  exit 1
fi

ATTACK_NAME="$1"
ATTACK_SEQ_INPUT="$2"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -z "${CONDA_PREFIX:-}" ]; then
  source /cm/shared/apps/anaconda/miniforge3/etc/profile.d/conda.sh
  conda activate slam-bench
fi

source "$REPO_ROOT/scripts/orbslam3_env.sh"

ATTACK_SEQ="$(realpath "$ATTACK_SEQ_INPUT")"
RUN_TAG="${RUN_TAG:-$(date +%Y%m%d_%H%M%S)}"
RUN_DIR="$REPO_ROOT/results/attacks/orbslam3/${ATTACK_NAME}/run_${RUN_TAG}"

KITTI_GT="$REPO_ROOT/data/kitti/dataset/poses/00.txt"
SETTINGS_YAML="$REPO_ROOT/systems/ORB_SLAM3/Examples/Stereo/KITTI00-02.yaml"

mkdir -p "$RUN_DIR"

echo "=== ORB-SLAM3 KITTI ATTACK RUN ==="
echo "ATTACK_NAME=$ATTACK_NAME"
echo "ATTACK_SEQ=$ATTACK_SEQ"
echo "RUN_DIR=$RUN_DIR"
echo "DATE=$(date)"
echo "HOSTNAME=$(hostname)"

cd "$RUN_DIR"

bash "$REPO_ROOT/scripts/run_orbslam3_stereo_kitti.sh" \
  "$ATTACK_SEQ" \
  "$SETTINGS_YAML" \
  > orbslam3_stdout.log \
  2> orbslam3_stderr.log

echo ""
echo "=== TRAJECTORY CHECK ==="
wc -l CameraTrajectory.txt
ls -lh CameraTrajectory.txt

python "$REPO_ROOT/scripts/evaluate_kitti_ate.py" \
  --estimate "$RUN_DIR/CameraTrajectory.txt" \
  --groundtruth "$KITTI_GT" \
  --output-json "$RUN_DIR/ate_metrics.json"

python "$REPO_ROOT/scripts/evaluate_kitti_segments.py" \
  --estimate "$RUN_DIR/CameraTrajectory.txt" \
  --groundtruth "$KITTI_GT" \
  --output-json "$RUN_DIR/kitti_segment_metrics.json"

python "$REPO_ROOT/scripts/compare_attack_to_baseline.py" \
  --attack-run "$RUN_DIR" \
  --baseline-summary "$REPO_ROOT/results/baselines/orbslam3/kitti00_stereo/repeat_summary.json" \
  > "$RUN_DIR/attack_vs_baseline.txt"

export RUN_DIR ATTACK_NAME ATTACK_SEQ
python - <<'PY'
import json
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR"])
ate = json.loads((run_dir / "ate_metrics.json").read_text())
seg = json.loads((run_dir / "kitti_segment_metrics.json").read_text())

summary = {
    "attack_name": os.environ["ATTACK_NAME"],
    "attack_sequence": os.environ["ATTACK_SEQ"],
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

echo ""
echo "=== ATTACK VS BASELINE ==="
cat "$RUN_DIR/attack_vs_baseline.txt"

echo ""
echo "=== DONE ==="
date

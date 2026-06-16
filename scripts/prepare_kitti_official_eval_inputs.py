#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text())


def get_metric(summary, key):
    value = summary[key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def run_dir_from_record(record):
    if isinstance(record, dict):
        return Path(record["run_dir"])
    return Path(record)


def run_metric(record, key):
    if isinstance(record, dict) and key in record:
        return float(record[key])
    return None


def representative_run(summary, metric="ate_rmse_m"):
    target = get_metric(summary, metric)
    runs = summary["runs"]

    scored = []
    for r in runs:
        val = run_metric(r, metric)
        if val is None:
            continue
        scored.append((abs(val - target), r))

    if scored:
        return run_dir_from_record(min(scored, key=lambda x: x[0])[1])

    # Baseline schema may store runs as strings only.
    # Fall back to the middle run after sorting for deterministic behavior.
    dirs = sorted(run_dir_from_record(r) for r in runs)
    return dirs[len(dirs) // 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", required=True, help="KITTI sequence id, e.g. 00 or 02")
    ap.add_argument("--condition", required=True)
    ap.add_argument("--summary", required=True, type=Path)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument("--output-root", required=True, type=Path)
    args = ap.parse_args()

    summary = load_json(args.summary)
    run_dir = representative_run(summary)
    traj = run_dir / "CameraTrajectory.txt"

    if not traj.exists():
        raise FileNotFoundError(f"Missing trajectory: {traj}")

    if not args.groundtruth.exists():
        raise FileNotFoundError(f"Missing ground truth: {args.groundtruth}")

    out_dir = args.output_root / f"kitti{args.seq}_{args.condition}"
    pred_dir = out_dir / "predictions"
    gt_dir = out_dir / "groundtruth"
    pred_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    pred_out = pred_dir / f"{args.seq}.txt"
    gt_out = gt_dir / f"{args.seq}.txt"

    shutil.copyfile(traj, pred_out)
    shutil.copyfile(args.groundtruth, gt_out)

    manifest = {
        "seq": args.seq,
        "condition": args.condition,
        "summary": str(args.summary),
        "selected_run_dir": str(run_dir),
        "selected_trajectory": str(traj),
        "prediction_file": str(pred_out),
        "groundtruth_file": str(gt_out),
        "note": "Prediction file is ORB-SLAM3 CameraTrajectory.txt copied into KITTI odometry text format: one 3x4 pose per line.",
    }

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

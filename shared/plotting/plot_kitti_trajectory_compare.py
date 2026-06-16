#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_poses(path: Path) -> np.ndarray:
    poses = []
    for line in path.read_text().strip().splitlines():
        vals = [float(x) for x in line.split()]
        if len(vals) != 12:
            continue
        T = np.eye(4)
        T[:3, :] = np.array(vals).reshape(3, 4)
        poses.append(T)
    if not poses:
        raise ValueError(f"No poses loaded from {path}")
    return np.array(poses)


def align_first_pose(est: np.ndarray, gt: np.ndarray) -> np.ndarray:
    n = min(len(est), len(gt))
    est = est[:n]
    gt = gt[:n]
    T_align = gt[0] @ np.linalg.inv(est[0])
    return np.array([T_align @ T for T in est])


def run_ate_rmse(run):
    """Support both summary schemas:
    1) runs as dicts with ate_rmse_m and run_dir
    2) runs as strings pointing to run dirs
    """
    if isinstance(run, dict):
        return float(run["ate_rmse_m"])

    run_dir = Path(run)
    summary_path = run_dir / "run_summary.json"
    ate_path = run_dir / "ate_metrics.json"

    if summary_path.exists():
        return float(json.loads(summary_path.read_text())["ate_rmse_m"])
    if ate_path.exists():
        return float(json.loads(ate_path.read_text())["ate_rmse_m"])

    raise FileNotFoundError(f"Could not find run_summary.json or ate_metrics.json in {run_dir}")


def run_dir_from_record(run):
    if isinstance(run, dict):
        return Path(run["run_dir"])
    return Path(run)


def representative_run(summary_path: Path) -> Path:
    d = json.loads(summary_path.read_text())
    target = d["ate_rmse_m"]["mean"]
    runs = d["runs"]

    chosen = min(runs, key=lambda run: abs(run_ate_rmse(run) - target))
    return run_dir_from_record(chosen)


def plot_sequence(seq, gt_path, conditions, output):
    gt = load_poses(gt_path)
    plt.figure(figsize=(8, 7))

    gt_xyz = gt[:, :3, 3]
    plt.plot(gt_xyz[:, 0], gt_xyz[:, 2], linewidth=2, label="ground truth")

    for label, summary_path in conditions:
        run_dir = representative_run(Path(summary_path))
        traj_path = run_dir / "CameraTrajectory.txt"
        est = load_poses(traj_path)
        est_aligned = align_first_pose(est, gt)
        xyz = est_aligned[:, :3, 3]
        plt.plot(xyz[:, 0], xyz[:, 2], linewidth=1.5, label=label)

    plt.title(f"KITTI {seq}: ORB-SLAM3 trajectory under patch conditions")
    plt.xlabel("x position (m)")
    plt.ylabel("z position (m)")
    plt.axis("equal")
    plt.grid(True, linewidth=0.3)
    plt.legend()
    plt.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=220)
    print(f"saved {output}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", required=True)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument(
        "--condition",
        action="append",
        nargs=2,
        metavar=("LABEL", "SUMMARY_JSON"),
        required=True,
        help="Label and repeat_summary.json path",
    )
    args = ap.parse_args()

    plot_sequence(
        seq=args.seq,
        gt_path=args.groundtruth,
        conditions=args.condition,
        output=args.output,
    )


if __name__ == "__main__":
    main()

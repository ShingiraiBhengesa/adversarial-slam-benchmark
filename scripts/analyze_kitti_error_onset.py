#!/usr/bin/env python3
import argparse
import json
import statistics as stats
from pathlib import Path

import numpy as np


def load_kitti_poses(path: Path) -> np.ndarray:
    poses = []
    for line in path.read_text().strip().splitlines():
        vals = [float(x) for x in line.split()]
        if len(vals) != 12:
            continue
        T = np.eye(4)
        T[:3, :] = np.array(vals, dtype=float).reshape(3, 4)
        poses.append(T)
    if not poses:
        raise ValueError(f"No KITTI-format poses found in {path}")
    return np.stack(poses)


def align_first_pose(est: np.ndarray, gt: np.ndarray) -> np.ndarray:
    align = gt[0] @ np.linalg.inv(est[0])
    return align[None, :, :] @ est


def cumulative_path_m(poses: np.ndarray) -> np.ndarray:
    xyz = poses[:, :3, 3]
    if len(xyz) == 0:
        return np.array([])
    step = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(step)])


def first_sustained_crossing(errors: np.ndarray, threshold: float, consecutive: int):
    if len(errors) < consecutive:
        return None
    mask = errors >= threshold
    run = 0
    for i, ok in enumerate(mask):
        if ok:
            run += 1
            if run >= consecutive:
                return i - consecutive + 1
        else:
            run = 0
    return None


def summarize(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(vals),
        "mean": float(stats.mean(vals)),
        "median": float(stats.median(vals)),
        "min": float(min(vals)),
        "max": float(max(vals)),
    }


def analyze_run(run_dir: Path, gt: np.ndarray, thresholds, consecutive: int, fps: float):
    traj = run_dir / "CameraTrajectory.txt"
    if not traj.exists():
        return {
            "run_dir": str(run_dir),
            "valid_trajectory": False,
            "reason": "missing CameraTrajectory.txt",
        }

    est = load_kitti_poses(traj)
    n = min(len(est), len(gt))
    est = est[:n]
    gt_n = gt[:n]

    est_aligned = align_first_pose(est, gt_n)
    errors = np.linalg.norm(est_aligned[:, :3, 3] - gt_n[:, :3, 3], axis=1)
    path = cumulative_path_m(gt_n)

    out = {
        "run_dir": str(run_dir),
        "valid_trajectory": True,
        "num_poses": int(n),
        "max_error_m": float(errors.max()),
        "max_error_frame": int(errors.argmax()),
        "max_error_path_m": float(path[int(errors.argmax())]),
        "final_error_m": float(errors[-1]),
        "onsets": {},
    }

    for thr in thresholds:
        idx = first_sustained_crossing(errors, thr, consecutive)
        key = f"{thr:g}m"
        if idx is None:
            out["onsets"][key] = None
        else:
            out["onsets"][key] = {
                "frame": int(idx),
                "time_s": float(idx / fps),
                "path_m": float(path[idx]),
                "error_m": float(errors[idx]),
            }

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument("--output-json", required=True, type=Path)
    ap.add_argument("--thresholds", nargs="+", type=float, default=[5.0, 10.0, 25.0, 50.0, 100.0])
    ap.add_argument("--consecutive", type=int, default=20)
    ap.add_argument("--fps", type=float, default=10.0)
    args = ap.parse_args()

    gt = load_kitti_poses(args.groundtruth)
    run_dirs = sorted([p for p in args.root.glob("run*") if p.is_dir()])

    runs = [
        analyze_run(run_dir, gt, args.thresholds, args.consecutive, args.fps)
        for run_dir in run_dirs
    ]

    summary = {
        "root": str(args.root),
        "groundtruth": str(args.groundtruth),
        "num_run_dirs": len(run_dirs),
        "num_valid_trajectories": sum(1 for r in runs if r.get("valid_trajectory")),
        "thresholds_m": args.thresholds,
        "consecutive_frames": args.consecutive,
        "fps": args.fps,
        "onset_summary": {},
        "runs": runs,
    }

    for thr in args.thresholds:
        key = f"{thr:g}m"
        frames = []
        paths = []
        for r in runs:
            onset = r.get("onsets", {}).get(key)
            if onset is not None:
                frames.append(onset["frame"])
                paths.append(onset["path_m"])
        summary["onset_summary"][key] = {
            "frame": summarize(frames),
            "path_m": summarize(paths),
        }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

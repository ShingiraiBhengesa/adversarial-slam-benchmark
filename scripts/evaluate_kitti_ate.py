#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import numpy as np


def load_kitti_poses(path: Path) -> np.ndarray:
    poses = []
    with path.open("r") as f:
        for line in f:
            vals = [float(x) for x in line.strip().split()]
            if not vals:
                continue
            if len(vals) != 12:
                raise ValueError(f"{path}: expected 12 values per KITTI pose line, got {len(vals)}")
            T = np.eye(4, dtype=np.float64)
            T[:3, :4] = np.array(vals, dtype=np.float64).reshape(3, 4)
            poses.append(T)
    if not poses:
        raise ValueError(f"No poses loaded from {path}")
    return np.stack(poses, axis=0)


def align_first_pose(est: np.ndarray, gt: np.ndarray) -> np.ndarray:
    # Applies one SE(3) correction so estimated first pose matches GT first pose.
    A = gt[0] @ np.linalg.inv(est[0])
    return A[None, :, :] @ est


def translation_errors(est: np.ndarray, gt: np.ndarray) -> np.ndarray:
    return np.linalg.norm(est[:, :3, 3] - gt[:, :3, 3], axis=1)


def path_length(poses: np.ndarray) -> float:
    xyz = poses[:, :3, 3]
    if len(xyz) < 2:
        return 0.0
    return float(np.sum(np.linalg.norm(np.diff(xyz, axis=0), axis=1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", required=True, type=Path)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument("--output-json", required=True, type=Path)
    args = ap.parse_args()

    est = load_kitti_poses(args.estimate)
    gt = load_kitti_poses(args.groundtruth)

    n = min(len(est), len(gt))
    est = est[:n]
    gt = gt[:n]

    est_aligned = align_first_pose(est, gt)
    err = translation_errors(est_aligned, gt)

    gt_path_length_m = path_length(gt)
    ate_rmse_m = float(np.sqrt(np.mean(err ** 2)))

    metrics = {
        "estimate": str(args.estimate),
        "groundtruth": str(args.groundtruth),
        "num_est_poses": int(len(est)),
        "num_gt_poses": int(len(gt)),
        "num_evaluated_poses": int(n),
        "alignment": "first_pose_SE3",
        "gt_path_length_m": gt_path_length_m,
        "ate_rmse_m": ate_rmse_m,
        "ate_rmse_percent_of_path": float(100.0 * ate_rmse_m / gt_path_length_m) if gt_path_length_m > 0 else None,
        "ate_mean_m": float(np.mean(err)),
        "ate_median_m": float(np.median(err)),
        "ate_min_m": float(np.min(err)),
        "ate_max_m": float(np.max(err)),
        "ate_std_m": float(np.std(err)),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(metrics, indent=2) + "\n")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

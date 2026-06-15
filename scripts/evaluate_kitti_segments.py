#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

import numpy as np


SEGMENT_LENGTHS_M = [100, 200, 300, 400, 500, 600, 700, 800]


def load_kitti_poses(path: Path) -> np.ndarray:
    poses = []
    with path.open("r") as f:
        for line in f:
            vals = [float(x) for x in line.strip().split()]
            if not vals:
                continue
            if len(vals) != 12:
                raise ValueError(f"{path}: expected 12 values per pose line, got {len(vals)}")
            T = np.eye(4, dtype=np.float64)
            T[:3, :4] = np.array(vals).reshape(3, 4)
            poses.append(T)
    if not poses:
        raise ValueError(f"No poses loaded from {path}")
    return np.stack(poses)


def trajectory_distances(poses: np.ndarray) -> np.ndarray:
    dist = [0.0]
    for i in range(1, len(poses)):
        step = np.linalg.norm(poses[i, :3, 3] - poses[i - 1, :3, 3])
        dist.append(dist[-1] + float(step))
    return np.array(dist, dtype=np.float64)


def last_frame_from_segment_length(distances: np.ndarray, first: int, length: float):
    target = distances[first] + length
    idx = np.searchsorted(distances, target, side="left")
    if idx >= len(distances):
        return None
    return int(idx)


def rotation_error_rad(T: np.ndarray) -> float:
    R = T[:3, :3]
    d = 0.5 * (np.trace(R) - 1.0)
    d = float(np.clip(d, -1.0, 1.0))
    return math.acos(d)


def translation_error_m(T: np.ndarray) -> float:
    return float(np.linalg.norm(T[:3, 3]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", required=True, type=Path)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument("--output-json", required=True, type=Path)
    ap.add_argument("--step-size", type=int, default=10)
    args = ap.parse_args()

    est = load_kitti_poses(args.estimate)
    gt = load_kitti_poses(args.groundtruth)

    n = min(len(est), len(gt))
    est = est[:n]
    gt = gt[:n]

    distances = trajectory_distances(gt)
    rows = []

    for first in range(0, n, args.step_size):
        for length in SEGMENT_LENGTHS_M:
            last = last_frame_from_segment_length(distances, first, length)
            if last is None or last >= n:
                continue

            gt_delta = np.linalg.inv(gt[first]) @ gt[last]
            est_delta = np.linalg.inv(est[first]) @ est[last]

            error = np.linalg.inv(est_delta) @ gt_delta

            trans_rel = translation_error_m(error) / length
            rot_rel = rotation_error_rad(error) / length

            rows.append({
                "first_frame": int(first),
                "last_frame": int(last),
                "length_m": float(length),
                "translation_error_percent": float(trans_rel * 100.0),
                "rotation_error_deg_per_100m": float(rot_rel * 180.0 / math.pi * 100.0),
            })

    if not rows:
        raise ValueError("No valid KITTI segment errors computed")

    by_length = {}
    for length in SEGMENT_LENGTHS_M:
        vals = [r for r in rows if r["length_m"] == float(length)]
        if not vals:
            continue
        by_length[str(length)] = {
            "num_segments": len(vals),
            "translation_error_percent_mean": float(np.mean([v["translation_error_percent"] for v in vals])),
            "rotation_error_deg_per_100m_mean": float(np.mean([v["rotation_error_deg_per_100m"] for v in vals])),
        }

    metrics = {
        "estimate": str(args.estimate),
        "groundtruth": str(args.groundtruth),
        "num_est_poses": int(len(est)),
        "num_gt_poses": int(len(gt)),
        "num_evaluated_poses": int(n),
        "step_size": int(args.step_size),
        "segment_lengths_m": SEGMENT_LENGTHS_M,
        "num_segments_total": len(rows),
        "translation_error_percent_mean": float(np.mean([r["translation_error_percent"] for r in rows])),
        "rotation_error_deg_per_100m_mean": float(np.mean([r["rotation_error_deg_per_100m"] for r in rows])),
        "by_length": by_length,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def load_poses(path):
    mats = []
    for line in Path(path).read_text().strip().splitlines():
        vals = [float(x) for x in line.split()]
        if len(vals) != 12:
            continue
        T = np.eye(4)
        T[:3, :] = np.array(vals).reshape(3, 4)
        mats.append(T)
    return np.stack(mats)


def align_first_pose(est, gt):
    return gt[0] @ np.linalg.inv(est[0]) @ est


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", required=True, type=Path)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument("--output-csv", required=True, type=Path)
    ap.add_argument("--output-json", required=True, type=Path)
    ap.add_argument("--thresholds", nargs="+", type=float, default=[5, 10, 25, 50, 100])
    args = ap.parse_args()

    est = load_poses(args.estimate)
    gt = load_poses(args.groundtruth)
    n = min(len(est), len(gt))
    est = est[:n]
    gt = gt[:n]

    est_aligned = align_first_pose(est, gt)
    err = np.linalg.norm(est_aligned[:, :3, 3] - gt[:, :3, 3], axis=1)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "translation_error_m"])
        for i, e in enumerate(err):
            w.writerow([i, float(e)])

    first_crossing = {}
    for th in args.thresholds:
        idx = np.where(err >= th)[0]
        first_crossing[f"{th:g}"] = int(idx[0]) if len(idx) else None

    summary = {
        "estimate": str(args.estimate),
        "groundtruth": str(args.groundtruth),
        "num_evaluated_poses": int(n),
        "error_mean_m": float(err.mean()),
        "error_median_m": float(np.median(err)),
        "error_rmse_m": float(np.sqrt(np.mean(err ** 2))),
        "error_max_m": float(err.max()),
        "error_max_frame": int(err.argmax()),
        "first_crossing_frame": first_crossing,
    }

    args.output_json.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

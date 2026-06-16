#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


PATTERNS = {
    "tracking_failures": "Fail to track local map",
    "new_maps": "Creation of new map",
    "stored_maps": "Stored map with ID",
    "loop_detections": "*Loop detected",
    "merge_detections": "*Merge detected",
    "shutdown": "Shutdown",
}


def count_pattern(text, pattern):
    return text.count(pattern)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--output-json", required=True, type=Path)
    args = ap.parse_args()

    runs = []
    for run_dir in sorted(args.root.glob("run*")):
        stdout = run_dir / "orbslam3_stdout.log"
        stderr = run_dir / "orbslam3_stderr.log"
        traj = run_dir / "CameraTrajectory.txt"

        if not stdout.exists():
            continue

        text = stdout.read_text(errors="ignore")
        serr = stderr.read_text(errors="ignore") if stderr.exists() else ""

        row = {
            "run_dir": str(run_dir),
            "trajectory_exists": traj.exists(),
            "trajectory_lines": sum(1 for _ in traj.open()) if traj.exists() else 0,
            "stderr_bytes": len(serr.encode()),
        }

        for key, pat in PATTERNS.items():
            row[key] = count_pattern(text, pat)

        runs.append(row)

    summary = {
        "root": str(args.root),
        "num_runs": len(runs),
        "runs": runs,
        "totals": {},
    }

    for key in list(PATTERNS.keys()) + ["trajectory_lines", "stderr_bytes"]:
        vals = [r[key] for r in runs]
        summary["totals"][key] = {
            "sum": sum(vals),
            "mean": sum(vals) / len(vals) if vals else 0.0,
            "min": min(vals) if vals else 0,
            "max": max(vals) if vals else 0,
        }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

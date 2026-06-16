#!/usr/bin/env python3
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

IDENTITY_POSE = "1 0 0 0 0 1 0 0 0 0 1 0\n"


def parse_errors_file(path: Path):
    if not path.exists():
        return None

    rows = []
    for line in path.read_text().strip().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        first_frame = int(float(parts[0]))
        r_err = float(parts[1])
        t_err = float(parts[2])
        length = float(parts[3])
        speed = float(parts[4])
        rows.append((first_frame, r_err, t_err, length, speed))

    if not rows:
        return None

    t_vals = [r[2] for r in rows]
    r_vals = [r[1] for r in rows]

    return {
        "num_segments": len(rows),
        "translation_error_percent_mean": 100.0 * sum(t_vals) / len(t_vals),
        "rotation_error_deg_per_100m_mean": (180.0 / math.pi) * 100.0 * sum(r_vals) / len(r_vals),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", required=True, help="KITTI sequence id, e.g. 00 or 02")
    ap.add_argument("--condition", required=True)
    ap.add_argument("--prediction", required=True, type=Path)
    ap.add_argument("--groundtruth", required=True, type=Path)
    ap.add_argument(
        "--devkit-binary",
        type=Path,
        default=Path("tools/kitti_odometry_devkit/devkit/cpp/eval_odometry_local"),
    )
    ap.add_argument(
        "--output-root",
        type=Path,
        default=Path("results/official_kitti_devkit_eval"),
    )
    args = ap.parse_args()

    seq = f"{int(args.seq):02d}"
    result_sha = f"kitti{seq}_{args.condition}"
    out_dir = args.output_root / result_sha

    if not args.prediction.exists():
        raise FileNotFoundError(f"Missing prediction: {args.prediction}")
    if not args.groundtruth.exists():
        raise FileNotFoundError(f"Missing groundtruth: {args.groundtruth}")
    if not args.devkit_binary.exists():
        raise FileNotFoundError(f"Missing devkit binary: {args.devkit_binary}")

    if out_dir.exists():
        shutil.rmtree(out_dir)

    gt_dir = out_dir / "data" / "odometry" / "poses"
    pred_dir = out_dir / "results" / result_sha / "data"
    gt_dir.mkdir(parents=True, exist_ok=True)
    pred_dir.mkdir(parents=True, exist_ok=True)

    # KITTI devkit loops over 00-21. Give all non-target sequences
    # harmless one-pose identity placeholders so the evaluator does not fail.
    for i in range(22):
        sid = f"{i:02d}"
        (gt_dir / f"{sid}.txt").write_text(IDENTITY_POSE)
        (pred_dir / f"{sid}.txt").write_text(IDENTITY_POSE)

    shutil.copyfile(args.groundtruth, gt_dir / f"{seq}.txt")
    shutil.copyfile(args.prediction, pred_dir / f"{seq}.txt")

    cmd = [str(args.devkit_binary.resolve()), result_sha]
    print("Running:", " ".join(cmd))

    env = dict(__import__("os").environ)
    env["KITTI_EVAL_SEQ"] = seq

    proc = subprocess.run(
        cmd,
        cwd=out_dir,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    (out_dir / "official_stdout.log").write_text(proc.stdout)
    (out_dir / "official_stderr.log").write_text(proc.stderr)

    print(proc.stdout)
    if proc.stderr.strip():
        print(proc.stderr)

    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    err_file = out_dir / "results" / result_sha / "errors" / f"{seq}.txt"
    parsed = parse_errors_file(err_file)

    summary = {
        "sequence": seq,
        "condition": args.condition,
        "result_sha": result_sha,
        "prediction": str(args.prediction),
        "groundtruth": str(args.groundtruth),
        "output_dir": str(out_dir),
        "devkit_binary": str(args.devkit_binary),
        "note": "Official KITTI odometry devkit evaluation. Non-target sequences are represented by one-pose identity placeholders so the legacy devkit can complete its 00-21 loop.",
        "target_sequence_metrics": parsed,
    }

    (out_dir / "official_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

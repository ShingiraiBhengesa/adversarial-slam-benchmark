#!/usr/bin/env python3
import argparse
from pathlib import Path


def read_lines(path):
    lines = [ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip()]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prediction", required=True)
    ap.add_argument("--groundtruth", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    pred_path = Path(args.prediction)
    gt_path = Path(args.groundtruth)
    out_path = Path(args.output)

    pred = read_lines(pred_path)
    gt = read_lines(gt_path)

    if len(pred) > len(gt):
        raise ValueError(f"Prediction longer than GT: {len(pred)} > {len(gt)}")

    missing = len(gt) - len(pred)

    if missing > 0:
        if not pred:
            raise ValueError("Cannot pad empty prediction file")
        pred = pred + [pred[-1]] * missing

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(pred) + "\n")

    print({
        "prediction": str(pred_path),
        "groundtruth": str(gt_path),
        "output": str(out_path),
        "original_prediction_poses": len(read_lines(pred_path)),
        "groundtruth_poses": len(gt),
        "missing_padded_with_last_pose": missing,
        "final_output_poses": len(pred),
    })


if __name__ == "__main__":
    main()

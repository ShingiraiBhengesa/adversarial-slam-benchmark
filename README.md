# Adversarial SLAM Benchmark

Reproducible benchmark harness for evaluating adversarial pressure on SLAM systems.

## Core question

When SLAM input is corrupted in a controlled way, which system breaks first, how badly, at what pipeline stage, and does the failure pattern differ by architecture?

## First experiment block

- Systems: ORB-SLAM3, DROID-SLAM
- Dataset: TUM RGB-D
- Sequences: fr1/desk, fr1/room
- Conditions: clean, occlusion, texture injection
- Metrics: ATE, RPE, tracking failure, frames tracked
- Repetitions: N = 5 per cell

## Contribution framing

This project reuses existing SLAM systems and published attack ideas where appropriate. The contribution is the benchmark harness, cross-architecture protocol, and statistical treatment.

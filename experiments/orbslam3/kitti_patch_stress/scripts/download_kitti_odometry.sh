#!/usr/bin/env bash
set -euo pipefail

DATA_ROOT="data/kitti"
mkdir -p "$DATA_ROOT"

cd "$DATA_ROOT"

echo "PWD=$(pwd)"
echo "=== DOWNLOAD KITTI ODOMETRY GRAY IMAGES ==="
if [ ! -f data_odometry_gray.zip ]; then
  wget -c https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_gray.zip
else
  echo "data_odometry_gray.zip already exists"
fi

echo ""
echo "=== DOWNLOAD KITTI ODOMETRY POSES ==="
if [ ! -f data_odometry_poses.zip ]; then
  wget -c https://s3.eu-central-1.amazonaws.com/avg-kitti/data_odometry_poses.zip
else
  echo "data_odometry_poses.zip already exists"
fi

echo ""
echo "=== UNZIP GRAY IMAGES ==="
if [ ! -d dataset/sequences/00 ]; then
  unzip -q data_odometry_gray.zip
else
  echo "dataset/sequences/00 already exists"
fi

echo ""
echo "=== UNZIP POSES ==="
if [ ! -d dataset/poses ]; then
  unzip -q data_odometry_poses.zip
else
  echo "dataset/poses already exists"
fi

echo ""
echo "=== VERIFY KITTI 00 ==="
ls -lh dataset/sequences/00
(ls -lh dataset/sequences/00/image_0 | head) || true
ls -lh dataset/sequences/00/times.txt
ls -lh dataset/poses/00.txt

echo ""
echo "=== DONE ==="

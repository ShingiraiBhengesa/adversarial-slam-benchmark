#!/bin/bash
#SBATCH --job-name=build_orbslam3
#SBATCH --partition=compute
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/build_orbslam3_%j.out
#SBATCH --error=logs/build_orbslam3_%j.err

set -euo pipefail

echo "HOSTNAME=$(hostname)"
echo "DATE=$(date)"
echo "PWD=$(pwd)"
echo "USER=$(whoami)"

source /cm/shared/apps/anaconda/miniforge3/etc/profile.d/conda.sh
conda activate slam-bench

export CC="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc"
export CXX="$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++"
export CMAKE_PREFIX_PATH="$CONDA_PREFIX:${CMAKE_PREFIX_PATH:-}"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"

echo ""
echo "=== ENVIRONMENT ==="
which python
python --version
which cmake
cmake --version | head -n 1
which g++
g++ --version | head -n 1

echo ""
echo "=== CMAKE CONFIG PATHS ==="
find "$CONDA_PREFIX" -name "OpenCVConfig.cmake" | head
find "$CONDA_PREFIX" -name "Eigen3Config.cmake" | head
find "$CONDA_PREFIX" -iname "*Pangolin*Config.cmake" | head


cd /home/sbhengesa/research/adversarial-slam-benchmark/systems/ORB_SLAM3

echo ""
echo "=== BUILD DBoW2 ==="
cd Thirdparty/DBoW2
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== BUILD g2o ==="
cd ../../g2o
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== BUILD Sophus ==="
cd ../../Sophus
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== UNCOMPRESS VOCABULARY ==="
cd ../../../Vocabulary
if [ ! -f ORBvoc.txt ]; then
  tar -xf ORBvoc.txt.tar.gz
fi

echo ""
echo "=== BUILD ORB_SLAM3 ==="
cd ..
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== BUILD COMPLETE ==="
date

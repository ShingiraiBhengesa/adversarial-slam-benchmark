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

GCC_EXEC="$CONDA_PREFIX/libexec/gcc/x86_64-conda-linux-gnu/15.2.0"
GCC_LIB="$CONDA_PREFIX/lib/gcc/x86_64-conda-linux-gnu/15.2.0"
SYSROOT="$CONDA_PREFIX/x86_64-conda-linux-gnu/sysroot"

export PATH="$GCC_EXEC:$CONDA_PREFIX/bin:$PATH"
export COMPILER_PATH="$GCC_EXEC:$GCC_LIB:${COMPILER_PATH:-}"
export LIBRARY_PATH="$GCC_LIB:$SYSROOT/usr/lib64:$CONDA_PREFIX/lib:${LIBRARY_PATH:-}"

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
echo "CC=$CC"
echo "CXX=$CXX"
which "$CC"
which "$CXX"
"$CC" --version | head -n 1
"$CXX" --version | head -n 1

echo ""
echo "=== COMPILER SANITY TEST ==="
cat > /tmp/orbslam3_test_compile.c <<'EOC'
int main(){return 0;}
EOC
"$CC" /tmp/orbslam3_test_compile.c -o /tmp/orbslam3_test_compile

cat > /tmp/orbslam3_test_compile.cpp <<'EOCXX'
#include <iostream>
int main(){ std::cout << "ok\\n"; return 0; }
EOCXX
"$CXX" /tmp/orbslam3_test_compile.cpp -o /tmp/orbslam3_test_compile_cpp
echo "compiler sanity test passed"

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
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== BUILD g2o ==="
cd ../../g2o
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== BUILD Sophus ==="
cd ../../Sophus
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DBUILD_TESTS=OFF -DBUILD_EXAMPLES=OFF
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== UNCOMPRESS VOCABULARY ==="
cd ../../../Vocabulary
if [ ! -f ORBvoc.txt ]; then
  tar -xf ORBvoc.txt.tar.gz
fi

echo ""
echo "=== PATCH ORB_SLAM3 CMAKE FOR C++14 ==="
cd ..
python - <<'PATCHPY'
from pathlib import Path
p = Path("CMakeLists.txt")
text = p.read_text()
text = text.replace("-std=c++11", "-std=c++14")
text = text.replace("COMPILEDWITHC11", "COMPILEDWITHC14")
text = text.replace("Using flag -std=c++11.", "Using flag -std=c++14.")
p.write_text(text)
PATCHPY
grep -n "std=c++\|COMPILEDWITH" CMakeLists.txt | head -n 20

echo ""
echo ""
echo "=== PATCH ORB_SLAM3 EXAMPLES FOR MODERN CHRONO ==="
python - <<'PATCHPY'
from pathlib import Path

patched = []
for p in Path("Examples").rglob("*.cc"):
    text = p.read_text()
    new = text.replace("std::chrono::monotonic_clock", "std::chrono::steady_clock")
    if new != text:
        p.write_text(new)
        patched.append(str(p))

print("patched_files=" + str(len(patched)))
for name in patched:
    print(name)
PATCHPY

grep -R "monotonic_clock" -n Examples || true
grep -R "steady_clock" -n Examples | head -n 20

echo "=== BUILD ORB_SLAM3 ==="
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CONDA_PREFIX" -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j"${SLURM_CPUS_PER_TASK:-4}"

echo ""
echo "=== BUILD COMPLETE ==="
date

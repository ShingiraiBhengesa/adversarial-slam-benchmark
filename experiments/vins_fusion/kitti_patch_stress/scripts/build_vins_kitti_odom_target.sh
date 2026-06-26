#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$REPO_ROOT/experiments/vins_fusion/kitti_patch_stress/scripts"
VINS_WS="$REPO_ROOT/systems/vins_fusion_ws"
VINS_ROOT="$VINS_WS/src/VINS-Fusion"
LOG_DIR="$REPO_ROOT/logs/vins_fusion_build"

JOBS="${JOBS:-8}"
LOAD="${LOAD:-8}"
CLEAN="${CLEAN:-1}"

if [ ! -d "$VINS_ROOT" ]; then
  echo "ERROR: VINS-Fusion source not found at: $VINS_ROOT" >&2
  echo "Expected local ignored source tree: systems/vins_fusion_ws/src/VINS-Fusion" >&2
  exit 1
fi

# Robostack activation scripts may reference unset variables such as CONDA_BUILD.
# Temporarily disable nounset only during environment activation.
set +u
source "$SCRIPT_DIR/vins_ros_env.sh"
set -u

echo "=== APPLY VINS-FUSION CLUSTER PATCH ==="
"$SCRIPT_DIR/patch_vins_fusion_for_cluster.sh" "$VINS_ROOT"

echo ""
echo "=== SCRUB COMPILER ENVIRONMENT ==="
unset CC
unset CXX
unset CFLAGS
unset CXXFLAGS
unset CPPFLAGS
unset LDFLAGS
unset CPATH
unset C_INCLUDE_PATH
unset CPLUS_INCLUDE_PATH
unset LIBRARY_PATH
unset GCC_EXEC_PREFIX
unset COMPILER_PATH

export PATH="$(python - <<'PY'
import os
parts = os.environ["PATH"].split(":")
bad = "libexec/gcc/x86_64-conda-linux-gnu"
print(":".join(p for p in parts if bad not in p))
PY
)"

export PATH="/usr/libexec/gcc/x86_64-redhat-linux/11:$PATH"
export CPATH="/usr/lib/gcc/x86_64-redhat-linux/11/include"
export LIBRARY_PATH="$CONDA_PREFIX/lib:/usr/lib/gcc/x86_64-redhat-linux/11"
export COMPILER_PATH="/usr/libexec/gcc/x86_64-redhat-linux/11"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"

hash -r

echo ""
echo "=== BUILD ENV CHECK ==="
echo "REPO_ROOT=$REPO_ROOT"
echo "VINS_WS=$VINS_WS"
echo "CONDA_PREFIX=$CONDA_PREFIX"
echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "CC=/usr/bin/gcc"
echo "CXX=/usr/bin/g++"
/usr/bin/gcc --version | head -n 1
/usr/bin/g++ --version | head -n 1
python --version

echo ""
echo "=== DEPENDENCY VERSION CHECK ==="
mamba list | grep -Ei "eigen|ceres|opencv|suitesparse|glog|gflags" || true

echo ""
echo "=== QUICK COMPILER TEST ==="
cat > /tmp/test_vins_compiler.c <<'C_EOF'
#include <stdio.h>
int main(){ printf("C compiler works\n"); return 0; }
C_EOF

cat > /tmp/test_vins_compiler.cpp <<'CPP_EOF'
#include <iostream>
int main(){ std::cout << "C++ compiler works" << std::endl; return 0; }
CPP_EOF

/usr/bin/gcc /tmp/test_vins_compiler.c -o /tmp/test_vins_c_system
/tmp/test_vins_c_system

/usr/bin/g++ /tmp/test_vins_compiler.cpp -o /tmp/test_vins_cpp_system
/tmp/test_vins_cpp_system

mkdir -p "$LOG_DIR"

if [ "$CLEAN" = "1" ]; then
  echo ""
  echo "=== CLEAN LOCAL BUILD PRODUCTS ==="
  rm -rf "$VINS_WS/build" "$VINS_WS/devel"
fi

cd "$VINS_WS"

LOG_FILE="$LOG_DIR/build_kitti_odom_target_$(date +%Y%m%d_%H%M%S).log"

echo ""
echo "=== BUILD VINS-FUSION KITTI ODOM TARGET ==="
echo "log: $LOG_FILE"
date

set -o pipefail

catkin_make -j"$JOBS" -l"$LOAD" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  kitti_odom_test \
  2>&1 | tee "$LOG_FILE"

echo ""
echo "=== BUILD PRODUCT CHECK ==="
ls -lh "$VINS_WS/devel/lib/vins/kitti_odom_test"

echo ""
echo "=== LINK LINE CHECK ==="
cat "$VINS_WS/build/VINS-Fusion/vins_estimator/CMakeFiles/kitti_odom_test.dir/link.txt" \
  | tr ' ' '\n' \
  | grep -E "opencv_video|opencv_core|rpath|stdc|vins_lib" \
  | sort -u || true

echo ""
echo "=== BUILD COMPLETE ==="
date

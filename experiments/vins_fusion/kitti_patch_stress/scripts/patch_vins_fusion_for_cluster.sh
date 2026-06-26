#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
VINS_ROOT="${1:-$REPO_ROOT/systems/vins_fusion_ws/src/VINS-Fusion}"

if [ ! -d "$VINS_ROOT" ]; then
  echo "ERROR: VINS-Fusion source folder not found: $VINS_ROOT" >&2
  exit 1
fi

python - "$VINS_ROOT" <<'PY'
from pathlib import Path
import re
import sys

vins_root = Path(sys.argv[1])

def read(p):
    return p.read_text()

def write(p, text):
    p.write_text(text)
    print(f"patched {p}")

# ---------------------------------------------------------------------
# 1) camera_models: OpenCV 4 compatibility for old CV_* constants
# ---------------------------------------------------------------------
compat = vins_root / "camera_models/include/camodocal/opencv4_compat.h"
compat.write_text(r'''#pragma once

#include <opencv2/imgproc.hpp>
#include <opencv2/calib3d.hpp>

#ifndef CV_GRAY2BGR
#define CV_GRAY2BGR cv::COLOR_GRAY2BGR
#endif

#ifndef CV_BGR2GRAY
#define CV_BGR2GRAY cv::COLOR_BGR2GRAY
#endif

#ifndef CV_GRAY2RGB
#define CV_GRAY2RGB cv::COLOR_GRAY2RGB
#endif

#ifndef CV_CALIB_CB_ADAPTIVE_THRESH
#define CV_CALIB_CB_ADAPTIVE_THRESH cv::CALIB_CB_ADAPTIVE_THRESH
#endif

#ifndef CV_CALIB_CB_NORMALIZE_IMAGE
#define CV_CALIB_CB_NORMALIZE_IMAGE cv::CALIB_CB_NORMALIZE_IMAGE
#endif

#ifndef CV_CALIB_CB_FILTER_QUADS
#define CV_CALIB_CB_FILTER_QUADS cv::CALIB_CB_FILTER_QUADS
#endif

#ifndef CV_CALIB_CB_FAST_CHECK
#define CV_CALIB_CB_FAST_CHECK cv::CALIB_CB_FAST_CHECK
#endif

#ifndef CV_ADAPTIVE_THRESH_MEAN_C
#define CV_ADAPTIVE_THRESH_MEAN_C cv::ADAPTIVE_THRESH_MEAN_C
#endif

#ifndef CV_THRESH_BINARY
#define CV_THRESH_BINARY cv::THRESH_BINARY
#endif

#ifndef CV_THRESH_BINARY_INV
#define CV_THRESH_BINARY_INV cv::THRESH_BINARY_INV
#endif

#ifndef CV_SHAPE_CROSS
#define CV_SHAPE_CROSS cv::MORPH_CROSS
#endif

#ifndef CV_SHAPE_RECT
#define CV_SHAPE_RECT cv::MORPH_RECT
#endif

#ifndef CV_TERMCRIT_EPS
#define CV_TERMCRIT_EPS cv::TermCriteria::EPS
#endif

#ifndef CV_TERMCRIT_ITER
#define CV_TERMCRIT_ITER cv::TermCriteria::COUNT
#endif

#ifndef CV_RETR_CCOMP
#define CV_RETR_CCOMP cv::RETR_CCOMP
#endif

#ifndef CV_CHAIN_APPROX_SIMPLE
#define CV_CHAIN_APPROX_SIMPLE cv::CHAIN_APPROX_SIMPLE
#endif

#ifndef CV_AA
#define CV_AA cv::LINE_AA
#endif
''')
print(f"wrote {compat}")

camera_cmake = vins_root / "camera_models/CMakeLists.txt"
text = read(camera_cmake)
text = text.replace(
    'set(CMAKE_CXX_FLAGS "-std=c++11")',
    'set(CMAKE_CXX_FLAGS "-std=c++11 -include ${CMAKE_CURRENT_SOURCE_DIR}/include/camodocal/opencv4_compat.h")'
)
text = re.sub(
    r'find_package\(OpenCV REQUIRED(?: COMPONENTS [^)]+)?\)',
    'find_package(OpenCV REQUIRED COMPONENTS core imgproc imgcodecs calib3d features2d)',
    text,
    count=1,
)
write(camera_cmake, text)

# ---------------------------------------------------------------------
# 2) vins_estimator CMake: headless OpenCV, no cv_bridge/image_transport
# ---------------------------------------------------------------------
vins_cmake = vins_root / "vins_estimator/CMakeLists.txt"
text = read(vins_cmake)

text = re.sub(
    r'find_package\(catkin REQUIRED COMPONENTS.*?\)\s*',
    '''find_package(catkin REQUIRED COMPONENTS
    roscpp
    std_msgs
    geometry_msgs
    nav_msgs
    tf
    camera_models
    message_filters
)

''',
    text,
    count=1,
    flags=re.S,
)

# Remove any previous OpenCV/linker patch block, then insert clean one.
text = re.sub(
    r'\nfind_package\(OpenCV REQUIRED[^\n]*\)\n'
    r'(?:set\(OPENCV_VIDEO_LIB[^\n]*\)\n)?'
    r'(?:link_directories\(\$ENV\{CONDA_PREFIX\}/lib\)\n)?'
    r'(?:set\(CMAKE_EXE_LINKER_FLAGS[^\n]*\)\n)?'
    r'(?:set\(CMAKE_SHARED_LINKER_FLAGS[^\n]*\)\n)?',
    '\n',
    text,
)

opencv_block = '''
find_package(OpenCV REQUIRED COMPONENTS core imgproc imgcodecs calib3d features2d video)
set(OPENCV_VIDEO_LIB "$ENV{CONDA_PREFIX}/lib/libopencv_video.so")
link_directories($ENV{CONDA_PREFIX}/lib)
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath,$ENV{CONDA_PREFIX}/lib -Wl,-rpath-link,$ENV{CONDA_PREFIX}/lib")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-rpath,$ENV{CONDA_PREFIX}/lib -Wl,-rpath-link,$ENV{CONDA_PREFIX}/lib")
'''

marker = '# message(WARNING "OpenCV_VERSION: ${OpenCV_VERSION}")'
if marker not in text:
    raise SystemExit("Could not find OpenCV insertion marker in vins_estimator/CMakeLists.txt")
text = text.replace(marker, marker + "\n" + opencv_block, 1)

text = re.sub(
    r'target_link_libraries\(vins_lib[^\n]*\)',
    'target_link_libraries(vins_lib ${catkin_LIBRARIES} ${OpenCV_LIBS} ${OPENCV_VIDEO_LIB} ${CERES_LIBRARIES})',
    text,
    count=1,
)
text = re.sub(
    r'target_link_libraries\(kitti_odom_test[^\n]*\)',
    'target_link_libraries(kitti_odom_test vins_lib ${OpenCV_LIBS} ${OPENCV_VIDEO_LIB} stdc++)',
    text,
    count=1,
)

write(vins_cmake, text)

# ---------------------------------------------------------------------
# 3) Patch old OpenCV constants in VINS estimator sources
# ---------------------------------------------------------------------
feature_tracker = vins_root / "vins_estimator/src/featureTracker/feature_tracker.cpp"
text = read(feature_tracker)
text = text.replace("CV_GRAY2RGB", "cv::COLOR_GRAY2RGB")
write(feature_tracker, text)

for rel in [
    "vins_estimator/src/KITTIOdomTest.cpp",
    "vins_estimator/src/KITTIGPSTest.cpp",
]:
    p = vins_root / rel
    if p.exists():
        text = read(p)
        text = text.replace("CV_LOAD_IMAGE_GRAYSCALE", "cv::IMREAD_GRAYSCALE")
        write(p, text)

# ---------------------------------------------------------------------
# 4) Remove cv_bridge from KITTIOdomTest.cpp
# ---------------------------------------------------------------------
kitti = vins_root / "vins_estimator/src/KITTIOdomTest.cpp"
text = read(kitti)

if "#include <algorithm>" not in text:
    text = text.replace("#include <ros/ros.h>", "#include <ros/ros.h>\n#include <algorithm>\n#include <string>")

text = text.replace(
    "#include <cv_bridge/cv_bridge.h>",
    "#include <sensor_msgs/Image.h>\n#include <std_msgs/Header.h>"
)

helper = r'''
static sensor_msgs::ImagePtr makeImageMsg(const cv::Mat& image, const std::string& encoding)
{
    sensor_msgs::ImagePtr msg(new sensor_msgs::Image());
    msg->height = image.rows;
    msg->width = image.cols;
    msg->encoding = encoding;
    msg->is_bigendian = false;
    msg->step = static_cast<sensor_msgs::Image::_step_type>(image.cols * image.elemSize());

    const size_t size = static_cast<size_t>(msg->step) * image.rows;
    msg->data.resize(size);

    if (image.isContinuous())
    {
        std::copy(image.datastart, image.datastart + size, msg->data.begin());
    }
    else
    {
        for (int r = 0; r < image.rows; ++r)
        {
            const unsigned char* row = image.ptr<unsigned char>(r);
            std::copy(row, row + msg->step, msg->data.begin() + static_cast<size_t>(r) * msg->step);
        }
    }

    return msg;
}
'''

if "static sensor_msgs::ImagePtr makeImageMsg" not in text:
    text = text.replace("using namespace std;\n", "using namespace std;\n" + helper + "\n", 1)

text = text.replace(
    'cv_bridge::CvImage(std_msgs::Header(), "mono8", imLeft).toImageMsg()',
    'makeImageMsg(imLeft, "mono8")'
)
text = text.replace(
    'cv_bridge::CvImage(std_msgs::Header(), "mono8", imRight).toImageMsg()',
    'makeImageMsg(imRight, "mono8")'
)

write(kitti, text)

# ---------------------------------------------------------------------
# 5) Remove cv_bridge from visualization helper used by vins_lib
# ---------------------------------------------------------------------
viz_h = vins_root / "vins_estimator/src/utility/visualization.h"
text = read(viz_h)
text = text.replace(
    "#include <cv_bridge/cv_bridge.h>",
    "#include <sensor_msgs/Image.h>\n#include <std_msgs/Header.h>"
)
write(viz_h, text)

viz_cpp = vins_root / "vins_estimator/src/utility/visualization.cpp"
text = read(viz_cpp)

if "#include <algorithm>" not in text:
    text = text.replace('#include "visualization.h"', '#include "visualization.h"\n#include <algorithm>\n#include <string>')

helper = r'''
static sensor_msgs::ImagePtr makeImageMsg(const cv::Mat& image, const std::string& encoding, const std_msgs::Header& header)
{
    sensor_msgs::ImagePtr msg(new sensor_msgs::Image());
    msg->header = header;
    msg->height = image.rows;
    msg->width = image.cols;
    msg->encoding = encoding;
    msg->is_bigendian = false;
    msg->step = static_cast<sensor_msgs::Image::_step_type>(image.cols * image.elemSize());

    const size_t size = static_cast<size_t>(msg->step) * image.rows;
    msg->data.resize(size);

    if (image.isContinuous())
    {
        std::copy(image.datastart, image.datastart + size, msg->data.begin());
    }
    else
    {
        for (int r = 0; r < image.rows; ++r)
        {
            const unsigned char* row = image.ptr<unsigned char>(r);
            std::copy(row, row + msg->step, msg->data.begin() + static_cast<size_t>(r) * msg->step);
        }
    }

    return msg;
}
'''

if "static sensor_msgs::ImagePtr makeImageMsg" not in text:
    text = text.replace("void pubTrackImage", helper + "\nvoid pubTrackImage", 1)

text = re.sub(
    r'sensor_msgs::ImagePtr\s+imgTrackMsg\s*=\s*cv_bridge::CvImage\(\s*header\s*,\s*"bgr8"\s*,\s*imgTrack\s*\)\.toImageMsg\(\)\s*;',
    'sensor_msgs::ImagePtr imgTrackMsg = makeImageMsg(imgTrack, "bgr8", header);',
    text,
)

write(viz_cpp, text)

print("VINS-Fusion cluster patch complete.")
PY

echo "Patch applied to: $VINS_ROOT"

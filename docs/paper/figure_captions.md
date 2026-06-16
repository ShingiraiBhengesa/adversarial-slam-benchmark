# Figure Captions

## Figure: Feature mechanism diagnostic

ORB keypoint diagnostic for a representative KITTI 00 frame under clean, black-patch, and checkerboard-patch conditions. The same 5% top-left region contains 18/2000 keypoints in the clean image and 8/2000 keypoints under black occlusion, but 405/2001 keypoints under the checkerboard patch. This shows that the checkerboard patch acts as a high-texture feature attractor rather than a simple occlusion.

## Figure: KITTI 00 trajectory comparison

ORB-SLAM3 stereo trajectory on KITTI 00 under clean, black 10%, checkerboard 5%, and checkerboard 10% conditions. Clean and black-patch trajectories remain close to ground truth, while checkerboard trajectories deviate severely, indicating geometry corruption caused by high-texture patch structure.

## Figure: KITTI 02 trajectory comparison

ORB-SLAM3 stereo trajectory on KITTI 02 under clean, black 10%, checkerboard 5%, and checkerboard 10% conditions. The sequence reproduces the main KITTI 00 pattern: black occlusion remains near baseline, while checkerboard patches cause severe trajectory corruption.

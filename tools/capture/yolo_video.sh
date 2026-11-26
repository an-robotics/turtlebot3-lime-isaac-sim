#!/usr/bin/env bash
# Video for tutorial 10: YOLO's /detections/image while the robot turns left and right.
# Not part of the tutorials - this is how docs/assets/video/tutorial10_yolo.mp4 is made.
#
#   tools/capture/yolo_video.sh
#
# 1. stops leftover simulations / ROS processes  2. starts isaac/10_yolo.py (headless)
# 3. starts the detector in the container (default settings)  4. records the sweep
#    (tools/capture/yolo_sweep.py)  5. cleans up  6. encodes the frames as H.264.
set -u
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
OUT=_out/yolo_video
rm -rf "$OUT"; mkdir -p "$OUT/frames"

tools/stop_isaac.sh >/dev/null; docker/ros_clean.sh >/dev/null
( source scripts/isaac_env.sh >/dev/null && exec timeout 300 python isaac/10_yolo.py --headless >"$OUT/isaac.log" 2>&1 ) &
ISAAC=$!
for _ in $(seq 1 150); do grep -q "^\[10\] ready" "$OUT/isaac.log" 2>/dev/null && break; sleep 2; done
grep -q "^\[10\] ready" "$OUT/isaac.log" || { echo "[yolo_video] 10_yolo.py did not become ready"; kill $ISAAC; exit 1; }

docker/run_ros.sh bash -c "nohup ros2 launch lime_yolo yolo.launch.py > /lime/$OUT/yolo.log 2>&1 &"
docker/run_ros.sh timeout 180 ros2 topic echo /detections vision_msgs/msg/Detection2DArray --once >/dev/null \
  || { echo "[yolo_video] no detections"; docker/ros_clean.sh >/dev/null; kill $ISAAC; exit 1; }
docker/run_ros.sh python3 /lime/tools/capture/yolo_sweep.py "/lime/$OUT/frames"

docker/ros_clean.sh >/dev/null; kill $ISAAC 2>/dev/null; tools/stop_isaac.sh >/dev/null

FFMPEG=$("$REPO_ROOT/.venv/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')
FPS=$(cat "$OUT/frames/fps.txt")
"$FFMPEG" -y -loglevel error -framerate "$FPS" -i "$OUT/frames/frame_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 28 -movflags +faststart docs/assets/video/tutorial10_yolo.mp4
echo "[yolo_video] saved docs/assets/video/tutorial10_yolo.mp4 ($(ls "$OUT/frames" | grep -c png) frames at $FPS fps)"

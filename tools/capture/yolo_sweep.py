# SPDX-FileCopyrightText: 2026 An (an-robotics)
# SPDX-License-Identifier: Apache-2.0

"""Record YOLO's /detections/image while the robot turns left and right (tutorial 10's video).

Not part of the tutorials - tools/capture/yolo_video.sh runs this in the ROS 2 container:

    python3 /lime/tools/capture/yolo_sweep.py OUT_DIR

It publishes /cmd_vel (still, left, right, left, still) and saves every annotated image as
OUT_DIR/frame_NNNN.png, then writes OUT_DIR/fps.txt (frames per second actually received).
"""

import sys
import time
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
TURN = 0.35  # rad/s
# (seconds, turn rate): about 40 degrees to the left, 80 to the right, back to the start
PROGRAM = [(2.0, 0.0), (2.0, TURN), (4.0, -TURN), (2.0, TURN), (2.0, 0.0)]

rclpy.init()
node = rclpy.create_node("lime_yolo_sweep")
bridge = CvBridge()
cmd = node.create_publisher(Twist, "/cmd_vel", 10)
frames = []


def on_image(msg):
    frames.append(bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8"))  # cv2.imwrite wants BGR


node.create_subscription(Image, "/detections/image", on_image, 10)

start = time.monotonic()
for seconds, turn in PROGRAM:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        t = Twist()
        t.angular.z = turn
        cmd.publish(t)
        rclpy.spin_once(node, timeout_sec=0.05)
cmd.publish(Twist())
duration = time.monotonic() - start

for i, img in enumerate(frames):
    cv2.imwrite(str(OUT / f"frame_{i:04d}.png"), img)
fps = len(frames) / duration
(OUT / "fps.txt").write_text(f"{fps:.2f}\n")
print(f"[sweep] {len(frames)} frames in {duration:.1f} s ({fps:.1f} per second) -> {OUT}", flush=True)
node.destroy_node()
rclpy.shutdown()

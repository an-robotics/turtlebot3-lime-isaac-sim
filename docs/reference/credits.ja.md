# クレジットとライセンス { #credits-license }

このプロジェクトは **Apache License 2.0** で公開しています（リポジトリの `LICENSE` と `NOTICE` を参照）。

## 利用しているプロジェクト { #built-on }

| プロジェクト | 用途 | ライセンス |
|---|---|---|
| [ROBOTIS-JAPAN-GIT/turtlebot3_lime](https://github.com/ROBOTIS-JAPAN-GIT/turtlebot3_lime)（`humble-devel`、コミット `3363b27`） | ロボットの記述（xacro、メッシュ）と MoveIt の設定。`ros2_ws/src/turtlebot3_lime/` に同梱し、Jazzy に移植 | Apache-2.0 |
| [Turtlebot3_Lime_IsaacSim_Humble](https://github.com/momoiorg-repository/Turtlebot3_Lime_IsaacSim_Humble) | このプロジェクトの前身（Isaac Sim 4.5 / Humble 版）。トピック名とコントローラー名 | MIT |
| [Turtlebot3_Lime_IsaacSim_Humble](https://github.com/momoiorg-repository/Turtlebot3_Lime_IsaacSim_Humble) `docs/imgs/lime1.jpg` | 実機の TurtleBot3 Lime の写真（`docs/assets/img/real_lime.jpg`、`real_vs_sim.jpg`、リサイズ済み）と、シミュレーション上のロボットの塗装に使った色 | MIT |
| [realsense-ros](https://github.com/IntelRealSense/realsense-ros) `realsense2_description` | D435 カメラのメッシュ (`assets/urdf/meshes/d435.dae`) | Apache-2.0 |
| [NVIDIA Isaac Sim 6.2](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/) | シミュレーター。各自が pip でインストール | NVIDIA license（ここでは再配布していません） |
| [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/)、Nav2、MoveIt 2、ros2_control | ROS 側（Docker コンテナ内） | Apache-2.0 / BSD |
| [nav2_bringup](https://github.com/ros-navigation/navigation2/tree/jazzy/nav2_bringup) | `nav2_params.yaml` は、その Jazzy のデフォルト設定から生成（`nav2_params_tidy.yaml` は、同じものにチュートリアル 16 の変更を加えたもの）。`navigation.rviz` は、その RViz 設定を改変したコピー | Apache-2.0 |
| [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox) | チュートリアル 14 の SLAM。`slam_params.yaml` は、その Jazzy 版の `mapper_params_online_async.yaml` から生成 | LGPL-2.1 |
| [py_trees](https://github.com/splintered-reality/py_trees) | チュートリアル 15 と 16 のビヘイビアツリー（`ros-jazzy-py-trees`、コンテナ内） | BSD-3-Clause |
| [Nav2](https://github.com/ros-navigation/navigation2/tree/jazzy/nav2_bt_navigator/behavior_trees) `navigate_to_pose_w_replanning_and_recovery.xml` | チュートリアル 15 で引用 | Apache-2.0 |
| [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) | `lime_yolo` での物体検出（コンテナにインストール。再配布はしていません） | AGPL-3.0 |
| [MkDocs](https://www.mkdocs.org/) + [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) | このウェブサイト | BSD-2 / MIT |

## TurtleBot3 Lime パッケージへの変更 { #changes-to-the-turtlebot3-lime-packages }

- `turtlebot3_lime.urdf.xacro`：Gazebo-classic のプラグイン（Jazzy では使えません）と、実機用の `ros2_control` ブロックを削除しました。ロボットの形状は変えていません。
- `package.xml`：不足していた `realsense2_description` への依存関係を宣言しました。
- `turtlebot3_lime.srdf`：`home` 姿勢は `joint3 = 1.87` を使っていましたが、これは URDF のジョイントの制限 (1.8567) の外です。現在は 1.80 を使うので、MoveIt が開始状態として受け付け、重力でアームが垂れる分の余裕も残ります。

変更したファイルには、すべてヘッダーにその旨を記載しています。

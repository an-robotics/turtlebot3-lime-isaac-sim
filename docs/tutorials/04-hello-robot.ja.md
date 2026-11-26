# 04 · Python でロボットを動かす（Hello Robot） { #04-move-the-robot-from-python-hello-robot }

<p class="tutorial-meta">⏱ 20 分 · レベル：初級 · スクリプト：<code>isaac/04_hello_robot.py</code></p>

**目標：** ROS もグラフも使わずに、Python スクリプトから Lime の車輪、アーム、グリッパーを直接制御します。これはいろいろ試すのに最も手早い方法で、強化学習やテストのスクリプトがロボットとやりとりするときの方法でもあります。

<figure class="result" markdown>
<video controls autoplay loop muted playsinline>
  <source src="../../../assets/video/tutorial04_hello_robot.mp4" type="video/mp4">
</video>
<figcaption>0.6 m 前進し、左に 90° 旋回し、アームを伸ばし、グリッパーを開いて閉じ、アームを折りたたみます。</figcaption>
</figure>

## 考え方 { #concepts }

**アーティキュレーション：** Isaac Sim のロボットは*アーティキュレーション*（articulation）です。アーティキュレーションとは、ジョイントでつながった剛体のリンクのツリーで、まとめてシミュレーションされます。`Articulation(path_of_the_root)` を使うと、そのすべての **DoF**（自由度、つまり動かせるジョイント）にまとめてアクセスできます。

```python
robot = Articulation("/World/turtlebot3_lime/Geometry/base_footprint/base_link")
robot.dof_names    # ['wheel_left_joint', 'wheel_right_joint', 'joint1', ..., 'gripper_right_joint']
wheels = robot.get_dof_indices(["wheel_left_joint", "wheel_right_joint"])
```

| やりたいこと | 呼び出し | 使われるドライブ（チュートリアル 03 で設定） |
|---|---|---|
| 車輪の速度 | `set_dof_velocity_targets([[wl, wr]], dof_indices=wheels)` | 速度ドライブ（減衰） |
| アーム / グリッパーの位置 | `set_dof_position_targets([[...]], dof_indices=arm)`（少しずつ動かします。下を参照） | 位置ドライブ（剛性 + 減衰） |
| 状態を読む | `get_dof_positions()`、`get_dof_velocities()`、`get_world_poses()` | |

角度は**ラジアン**、直動ジョイント（グリッパー）は**メートル**で表します。

**Python で差動二輪駆動：** `isaacsim.robot.experimental.wheeled_robots` の `DifferentialController` は、チュートリアル 06 のグラフのノードと同じ式を計算します。

```python
controller = DifferentialController(wheel_radius=0.06, wheel_base=0.29425)
wheel_speeds = controller.forward(np.array([0.2, 0.0]))   # 0.2 m/s forward -> [3.33, 3.33] rad/s
robot.set_dof_velocity_targets([wheel_speeds], dof_indices=wheels)
```

## 実行してみる { #run-it }

```bash
source scripts/isaac_env.sh
python isaac/04_hello_robot.py
python isaac/04_hello_robot.py --headless --test
```

スクリプトは、時刻ごとに動作を決めた小さなプログラムを実行します。

```python
program = [
    (0.5, lambda: drive(0.2, 0.0)),                          # forward 0.2 m/s for 3 s -> 0.6 m
    (3.5, lambda: drive(0.0, math.pi / 2 / 2.0)),            # turn left: 90 deg in 2 s
    (5.5, lambda: drive(0.0, 0.0)),
    (6.0, lambda: move_arm(REACH)),                          # smoothly, in 1.5 s (see below)
    (8.0, lambda: robot.set_dof_position_targets([[0.019]], dof_indices=gripper)),   # open
    (9.0, lambda: robot.set_dof_position_targets([[-0.010]], dof_indices=gripper)),  # close
    (10.0, lambda: move_arm(lime.ARM_HOME)),
]
```

```text
[04][check] ok   drove 0.58 m forward (commanded 0.6 m)
[04][check] ok   turned left to 84.2 deg (commanded 90)
[04][check] ok   arm reached the reach pose (max error 0.002 rad)
[04][check] ok   gripper opened to 0.0190 m
[04][check] ok   base stayed flat on the floor while the arm moved (max tilt 0.0 deg)
[04][test] PASS
```

指令値とのわずかな差は、加速によるものです。ロボットが指令された速度に達するまでには、少し時間がかかります。

### アームは一気に動かさず、なめらかに動かす { #move-the-arm-smoothly-never-in-one-jump }

`robot.set_dof_position_targets([REACH], dof_indices=arm)` のように、アームを目標へ直接送ることも*できます*。すると位置ドライブは、アームをサーボの最高速度（約 4.7 rad/s）で振り、動き出しも停止も一瞬で行います。その反動でロボット全体が傾きます。Lime の車輪は前寄りにあり、重心は車軸のわずか約 4 cm 後ろにあるので、後部が床から浮き上がります。測定結果は次のとおりです。

| アームの動かし方 | 台車の最大の傾き |
|---|---|
| 目標へ一気に（サーボの最高速度） | 伸ばすとき 19.6°、折りたたむとき **46.7°** |
| 同じ動かし方で、バッテリーの質量を 2 倍の 3 kg にした場合 | 伸ばすとき 1.4°、折りたたむとき 16.7° |
| 速度を 1 rad/s に制限 | 0.5° |
| **1.5 s かけてなめらかに** (`move_arm`) | **0.04°** |

実際のアームのコントローラーも、目標へ一気に飛ぶことはありません。MoveIt（チュートリアル 12）は、速度と加速度の制限を守る軌道を計画します。`move_arm` はその最も単純な版です。毎フレーム目標を少しずつ動かし、動き出しと停止をなめらかにします。

```python
--8<-- "isaac/04_hello_robot.py:move_arm"
```

!!! note "指令を出すのは左のグリッパーの指だけです"
    `gripper_right_joint` は、mimic ジョイント（チュートリアル 03）によって自動的に `gripper_left_joint` に追従します。

??? example "スクリプト全体：`isaac/04_hello_robot.py`"
    ```python
    --8<-- "isaac/04_hello_robot.py"
    ```

**次へ：** [05 · はじめての Action Graph](05-action-graph.md)

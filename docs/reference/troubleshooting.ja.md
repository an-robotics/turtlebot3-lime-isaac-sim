# トラブルシューティング { #troubleshooting }

これらのチュートリアルを Isaac Sim 6.2（pip でのインストール、Ubuntu 24.04）上で作る中で実際に遭遇した問題と、その対処法です。

## Isaac Sim { #isaac-sim }

### コア拡張機能が読み込めない (`charset_normalizer`) { #core-extensions-fail-to-load-charset_normalizer }

**症状：** GUI (`isaacsim`) は起動しますが、コンソールに次のように表示されます。

```text
Failed to import python module isaacsim.core.experimental.prims ... charset_normalizer.md.MessDetectorPlugin
size changed, may indicate binary incompatibility. Expected 24 from C header, got 16 from PyObject
[ext: isaacsim.core.experimental.prims-1.12.1] Failed to startup python extension.
```

そして、ロボティクスの機能の多くが使えません。

**原因：** pip でインストールした場合、いくつかの Kit 拡張機能が、それぞれ別々にコンパイルされた `charset_normalizer` パッケージのコピーを同梱しています。完全な GUI アプリが起動するとき、インポートの連鎖 (`scipy` → `numpy.f2py` → `charset_normalizer`) によって、2 つのコピーのモジュールが混ざってしまいます。

**対処：** `scripts/setup_isaacsim.sh` は、インタープリターの起動時に `charset_normalizer` を一度だけインポートする 1 行の `.pth` ファイルを venv に追加します。これにより、以降のインポートはすべて、矛盾のない同じ 1 つのコピーを使います。

```bash
echo "import charset_normalizer, charset_normalizer.md, charset_normalizer.cd" \
  > .venv/lib/python3.12/site-packages/zz_preload_charset_normalizer.pth
```

### `ROS2 Bridge startup failed … libament_index_cpp.so: cannot open shared object file` { #ros2-bridge-startup-failed-libament_index_cppso-cannot-open-shared-object-file }

同梱の ROS 2 ライブラリが `LD_LIBRARY_PATH` に入っていません。Isaac Sim を起動する**前に**、ターミナルで `source scripts/isaac_env.sh` を実行してください。ダイナミックリンカーは `LD_LIBRARY_PATH` をプロセスの起動時にしか読まないので、あとから Isaac Sim の中で設定しても効果はありません。

### `uv` を使った `pip install` で `isaacsim` を解決できない { #pip-install-with-uv-fails-to-resolve-isaacsim }

`uv pip install isaacsim…` が、`no version of mujoco-usd-converter==…` や `tinyobjloader==2.0.0rc13 … pre-releases weren't enabled` で止まります。NVIDIA のガイドや `scripts/setup_isaacsim.sh` と同じように、venv の中で通常の `pip` を使ってください。

### ロボットに物理が設定されていない / アーティキュレーションが見つからない { #the-robot-has-no-physics-no-articulation-is-found }

6.2 の URDF インポーターで作ったアセットには `Physics` バリアントセットがあり、その**デフォルトの選択がありません**。`physx` を選ぶ (Property ▸ Variants) か、`add_reference_to_stage` に `variants=[("Physics", "physx")]` を渡してください。調整済みのアセット `turtlebot3_lime_tuned.usda` では、すでに選択されています。

### `Undefined 'xformOp:translate' property … Set the 'reset_xform_op_properties' parameter to True` { #undefined-xformoptranslate-property-set-the-reset_xform_op_properties-parameter-to-true }

実験的な `XformPrim` API は、プリムを動かす前に標準的なトランスフォームスタックを必要とします：`XformPrim(path, reset_xform_op_properties=True).set_world_poses(...)`。

### 両輪に同じ指令を出しているのに、ロボットがゆっくりしか走らない、または曲がる { #the-robot-drives-slowly-or-curves-although-both-wheels-get-the-same-command }

キャスターが床を擦って抵抗になっています。調整済みのアセットを使い、[03 · ロボットの調整](../tutorials/03-tune-robot.md)を参照してください。キャスターのマテリアルの摩擦の結合モードを `min` にします。

## ROS 2 { #ros-2 }

### トピックは一覧に出るのに、`ros2 topic echo` で何も表示されない { #topics-are-listed-but-ros2-topic-echo-shows-nothing }

これは DDS のトランスポートの問題です。両側で同じ `ROS_DOMAIN_ID` と RMW、そしてこのプロジェクトでは `config/fastdds.xml` にある Fast DDS の UDP 専用プロファイルを使う必要があります。コンテナは `--network host` を使います。また、シミュレーションが**再生中**かどうかも確認してください。ROS 2 ブリッジは、再生（Play）中にしかパブリッシュしません。

### Docker イメージのビルドがとても遅い { #building-the-docker-image-is-very-slow }

お使いのネットワークからは、`apt` のミラーが遅いことがあります。より近いミラーを使ってください：`UBUNTU_MIRROR=http://<mirror>/ubuntu/ ./docker/run_ros.sh`。これは `archive.ubuntu.com` と `security.ubuntu.com` の両方を置き換えます。

### コンテナから RViz が開かない { #rviz-does-not-open-from-the-container }

`run_ros.sh` は `DISPLAY` を渡し、`xhost +local:docker` を実行します。デスクトップのターミナルから起動するか、呼び出す前に `DISPLAY` を設定してください（例えば `DISPLAY=:0` や、使っている VNC のディスプレイ）。

### オドメトリは正確なのに、SLAM の地図がドリフトしたりねじれたりする { #the-slam-map-drifts-or-twists-although-odometry-is-exact }

Isaac Sim の RTX LiDAR は、何にも当たらなかったビームに **−1.0** を書き込みますが、ROS は `inf` を想定しています。slam_toolbox のスキャンマッチャーは、それぞれの −1 を 1 m 先にある架空の点に変えてしまい、ドリフトします。スキャンを頻繁に追加する場合（`minimum_travel_*` が小さい場合）は、1 m を超えてずれます。`slam.launch.py` と同じように、`scan_fix` ノードからの `/scan_fixed` を入力し、`minimum_travel_*` はデフォルトのままにしてください（[チュートリアル 14](../tutorials/14-slam.md)）。

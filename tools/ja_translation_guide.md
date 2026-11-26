# Japanese translation guide (docs/**/*.ja.md)

The website has a Japanese version: every English page `docs/<path>.md` has a sibling `docs/<path>.ja.md`,
published under `/ja/` by the mkdocs-static-i18n plugin (see `plugins:` in `mkdocs.yml`). A page without a
`.ja.md` shows the English text in the Japanese site.

Readers: Japanese engineers/students opening Isaac Sim for the first time. They can use a Linux
terminal and read Python. Translate so a Japanese beginner reads it as natural, clear technical Japanese.

## Updating a Japanese page

1. Change the English page first, then make the same change in the `.ja.md` page. Translate the whole change;
   don't add, drop or reorder content. Keep every number, unit, value, name and caveat.
2. Every Japanese heading ends with the English heading's id, `{ #id }` (the id the English heading gets
   in the built site), so anchors and links such as `06-ros2-drive.md#ros-2-in-10-minutes` work in both languages.
   A new English heading needs a new Japanese heading with that id.
3. Raw HTML media paths (`<source src="...">`) need one more `../` than in the English page, because the
   Japanese site lives in `/ja/`. Markdown links and images (`![..](..)`) stay the same as in English.
   `python3 tools/check_ja_docs.py --fix-media` adds the `../` for you.
4. Check:

   ```bash
   .venv-docs/bin/mkdocs build --strict && python3 tools/check_ja_docs.py
   ```

   The checker compares each `.ja.md` with its English page (code blocks, snippets, math, link targets,
   callouts, heading ids, page structure, media paths) and warns about numbers that differ, lines that look
   untranslated and paragraphs split over several lines.
5. A new page: add it to `nav:` in `mkdocs.yml` as usual and its Japanese title to `nav_translations`.

## Tone

- です・ます調. Plain, short, friendly sentences, like the English. No 二重敬語, no 「〜させていただきます」.
- Steps: 「〜を選びます。」「〜をクリックします。」 or 「〜してください。」 — pick one style per list and keep it.
- English "you" is usually dropped. "we" (the tutorials) → 「このチュートリアルでは」 or drop it.

## Keep byte-for-byte identical (do NOT translate or touch)

- **Fenced code blocks**: everything between the fences, including `#` comments, shell commands and
  program output (`text` blocks). Also keep the fence lines and their indentation.
- `--8<-- "..."` snippet lines.
- Inline code `` `...` ``, math `$...$` and `$$...$$` blocks.
- Link and image **targets** (the `(...)` part), URLs, anchors (`#...`), attribute lists such as `{ .full }`.
- Raw HTML tags and attributes: `<figure class="result" markdown>`, `<video ...>`, `<source src=...>`,
  `<div class="callouts" markdown>`, every `<span class="callout" ...>N</span>` line (copy as is), `<b>`, `<code>`
  (except the extra `../` in media paths, see "Updating a Japanese page").
  (Translate only the human text between tags, e.g. inside `<figcaption>` and `<p class="tutorial-meta">`.)
- Admonition keywords and their syntax: `!!! note "..."`, `??? info "..."`, `???+ ...` (translate only the
  quoted title), and the 4-space indentation of their bodies.
- Tab labels used on several pages: keep exactly `=== "GUI"` and `=== "Python (standalone)"` — tabs are linked
  across pages (and languages) by their label text. A label used on one page only may be translated.
- The `{ #id }` at the end of each heading: keep it exactly, translate only the heading text before it.
- Names: product/tool names (Isaac Sim, Omniverse, USD, PhysX, OmniGraph, Action Graph, Replicator, ROS 2,
  Jazzy, Humble, Nav2, MoveIt 2, RViz, ros2_control, slam_toolbox, py_trees, YOLO, Ultralytics, Docker, Git…),
  topic/frame/prim/joint/link/file/package/node names, CLI flags, `PASS`/`FAIL`, keyboard keys.

## GUI strings stay English

Isaac Sim and RViz have English UIs, and the screenshots are English. Keep menu paths, panel names,
button names, property/attribute names and OmniGraph node names in English, in the same bold/italic as the
source, so readers can match them on screen:
**Create ▸ Physics ▸ Ground Plane**, **Stage**, **Property**, **Viewport**, **Content**, **Console**,
**Play** ▶, **Stop** ■, *Translate*, **Max Force**, **Stiffness**, **On Playback Tick**, **2D Goal Pose**, …
Write the Japanese around them: 「**Create ▸ Physics ▸ Ground Plane** を選びます。」「**Property** パネルで…」.

## Markdown/format rules (important — the build depends on them)

1. **No hard line breaks inside a paragraph, list item, admonition paragraph or figcaption.** The English
   source wraps at ~115 columns; in Japanese a line break renders as a visible space. Join each paragraph
   into ONE line. Keep the blank lines, list markers, indentation (4 spaces inside admonitions, tabs and
   nested lists) and the overall line structure of blocks otherwise the same.
   Exception: a figcaption or meta line that is one line in English stays one line.
2. Tables: same number of rows and columns, ASCII `|` only (never full-width `｜`), same alignment row.
3. Emphasis: use `*`/`**` only, never `_`. `**重要**です` works in this Markdown engine without spaces.
4. Never use the full-width space U+3000 for indentation.
5. Spacing: put a half-width space between Japanese and Latin words, numbers, inline code and bold/italic
   Latin terms: 「Isaac Sim を起動します」「`/cmd_vel` にパブリッシュします」「0.87 m 進みます」「**Play** ▶ を押します」.
   No space next to Japanese punctuation（。、「」（）：）.
6. Punctuation: 、。 Use 「」 for quotes (“…” → 「…」). Full-width （） and ： when the content is Japanese;
   keep half-width ( ) when the content is only Latin/code, e.g. `(URDF → USD)`. Keep the `·` in titles.
7. Half-width digits; units as in English with a space: `0.87 m`, `5 rad/s`, `N·m/deg`, `20 分`, `約 9 時間`.
   Ranges: `30〜60 分`, `00〜05` (English en dash ranges `00–05` may also stay as `00–05`; be consistent in a page).
8. Link text is translated; link targets are not. `[What you need](#what-you-need)` → `[必要なもの](#what-you-need)`.
9. Image alt text is translated. Admonition titles are translated (code inside them stays code).

## Fixed strings

`<p class="tutorial-meta">⏱ 25 min · Level: beginner → intermediate · Scripts: <code>…</code> · ROS: <code>…</code></p>`
→ `<p class="tutorial-meta">⏱ 25 分 · レベル：初級 → 中級 · スクリプト：<code>…</code> · ROS：<code>…</code></p>`
Levels: first contact → はじめて · beginner → 初級 · intermediate → 中級 · advanced → 上級.
`30–60 min (mostly downloads)` → `30〜60 分（ほとんどはダウンロード）`.

`**Goal.** …` → `**目標：** …`
`**Next:** [03 · Tune the robot](03-tune-robot.md)` → `**次へ：** [03 · ロボットの調整](03-tune-robot.md)` (translate any rest of the sentence).
Headings "Concepts" → 考え方 · "Build it" → 作ってみる · "Automatic check" → 自動チェック ·
"Check the result" → 結果を確かめる · "Troubleshooting" → トラブルシューティング.
Admonition "Automatic check" → 自動チェック, "Shortcut" → 近道.

### Page titles (use exactly these, in H1s, link texts, tables and "Next" links)

| # | English | 日本語 (H1 after `NN · `) | short form (links, tables) |
|---|---|---|---|
| 00 | Setup | セットアップ | セットアップ |
| 01 | Isaac Sim basics & Hello World | Isaac Sim の基本と Hello World | same |
| 02 | Import TurtleBot3 Lime (URDF → USD) | TurtleBot3 Lime のインポート (URDF → USD) | TurtleBot3 Lime のインポート |
| 03 | Tune the robot | ロボットの調整 | same |
| 04 | Move the robot from Python ("Hello Robot") / Move it from Python | Python でロボットを動かす（Hello Robot） | Python でロボットを動かす |
| 05 | Your first Action Graph: keyboard driving | はじめての Action Graph：キーボードで運転 | はじめての Action Graph |
| 06 | Drive TurtleBot3 Lime with ROS 2 (`/cmd_vel`) / Drive with ROS 2 | ROS 2 で TurtleBot3 Lime を走らせる（`/cmd_vel`） | ROS 2 で走らせる |
| 07 | Odometry, TF and RViz / Odometry, TF & RViz | オドメトリ、TF、RViz | same |
| 08 | Camera (RealSense D435) | カメラ（RealSense D435） | same |
| 09 | LiDAR & IMU | LiDAR と IMU | same |
| 10 | Object detection with YOLO | YOLO で物体検出 | same |
| 11 | Navigation with Nav2 | Nav2 でナビゲーション | same |
| 12 | Arm control with MoveIt 2 | MoveIt 2 でアームを制御 | same |
| 13 | Pick and place | ピック＆プレース | same |
| 14 | Make your own map with SLAM | SLAM で自分の地図を作る | same |
| 15 | Behavior trees | ビヘイビアツリー | same |
| 16 | All together: tidy the room | 総仕上げ：部屋を片付ける | same |
| – | Troubleshooting | トラブルシューティング | same |
| – | Credits & license | クレジットとライセンス | same |

Nav sections: Getting Started → はじめに · Robot Setup → ロボットの準備 · OmniGraph → OmniGraph ·
ROS 2 → ROS 2 · Applications → 応用 · Reference → リファレンス · Home → ホーム.

## Glossary (use consistently)

| English | 日本語 |
|---|---|
| the Lime / TurtleBot3 Lime | Lime / TurtleBot3 Lime |
| the real robot | 実機 |
| simulated Lime / in simulation | シミュレーション上の Lime / シミュレーションで |
| tutorial | チュートリアル |
| mobile manipulator | モバイルマニピュレーター |
| differential-drive base | 差動二輪の台車 |
| arm / gripper / finger | アーム / グリッパー / 指（フィンガー） |
| end effector | エンドエフェクター |
| wheel / caster / tyre | 車輪 / キャスター / タイヤ |
| stage (USD) / prim / schema / attribute | ステージ / プリム / スキーマ / 属性 |
| reference (USD) / payload / variant | リファレンス / ペイロード / バリアント |
| asset | アセット |
| articulation | アーティキュレーション |
| joint / link | ジョイント / リンク |
| joint drive | ジョイントドライブ |
| stiffness / damping / gain | 剛性（stiffness）/ 減衰（damping）/ ゲイン — GUI field names stay English |
| collider / rigid body / mass | コライダー / 剛体 / 質量 |
| friction / combine mode | 摩擦 / 結合モード（combine mode） |
| physics material | 物理マテリアル |
| solver iterations | ソルバーの反復回数 |
| physics step / render | 物理ステップ / レンダリング |
| scene | シーン |
| viewport | ビューポート |
| standalone script | スタンドアロンスクリプト |
| headless | ヘッドレス |
| GUI tab / Python tab | GUI タブ / Python タブ |
| play / stop (simulation) | 再生 / 停止 (GUI buttons stay **Play** / **Stop**) |
| graph / node (OmniGraph) | グラフ / ノード |
| ROS 2 node / topic / message / service / action | ノード / トピック / メッセージ / サービス / アクション |
| publish / subscribe / publisher / subscriber | パブリッシュ / サブスクライブ / パブリッシャー / サブスクライバー |
| launch file / package / workspace | launch ファイル / パッケージ / ワークスペース |
| container / image (Docker) | コンテナ / イメージ |
| simulation time / clock | シミュレーション時間 / クロック |
| frame / optical frame / TF tree | フレーム / 光学フレーム / TF ツリー |
| odometry | オドメトリ |
| depth (image/camera) / point cloud | 深度（画像/カメラ）/ 点群 |
| detection / bounding box / confidence | 検出 / バウンディングボックス / 信頼度 |
| LiDAR scan / beam / no return | LiDAR スキャン / ビーム / 反射なし |
| map / occupancy map | 地図 / 占有格子地図 |
| costmap (global / local) | コストマップ（グローバル / ローカル） |
| inflation radius / footprint | インフレーション半径 / フットプリント |
| planner / controller | プランナー / コントローラー |
| goal / pose / waypoint | ゴール / 姿勢 / ウェイポイント |
| position / orientation | 位置 / 向き |
| localization (AMCL) | 自己位置推定（AMCL） |
| drift / keyframe / loop closure | ドリフト / キーフレーム / ループクロージャ |
| ground truth | 正解（ground truth） |
| behavior tree / blackboard / tick | ビヘイビアツリー / ブラックボード / tick |
| Sequence / Selector / Fallback / decorator (node types) | keep the English node-type names; decorator → デコレーター |
| pick and place / grasp | ピック＆プレース / 把持 |
| inverse kinematics (IK) | 逆運動学（IK） |
| lookout (tutorial 16) | 見回り地点 |
| banana / bowl / mug / bottle / mustard bottle / traffic cone | バナナ / ボウル / マグカップ / ボトル / マスタードのボトル / カラーコーン |
| check (automatic) / test | チェック / テスト |
| troubleshooting | トラブルシューティング |
| terminal | ターミナル |
| repository | リポジトリ |
| GPU / VRAM / driver | GPU / VRAM / ドライバー |

## More decisions (made while translating)

- Bold lead-in labels: `**Drives.**` → `**ドライブ：**`, `**Save as an override layer.**` → `**オーバーライドレイヤーとして保存：**`.
- A colon that introduces a code block or table: end the Japanese sentence with 「。」 (or 「：」 if it reads better).
- **Durations in prose use 秒/分/時間**: 「2 秒待ちます」「3 秒間」「約 15 分」. Keep `s` in tables, in `t = 12.8 s`-style
  values, in compound units (`m/s`, `rad/s`, `Hz`) and in anything quoted from program output.
- Parentheses: full-width （） for glosses after Japanese words even when the gloss is Latin: 剛性（stiffness）.
  Half-width ( ) for value/code-only asides: 円柱 (URDF), 車輪 (×2), (0.1°). Add glosses sparingly, only where they help.
- `≤ 4` → `4 以下`, `≥ 4` → `4 以上` in prose (keep the symbols inside tables of values if clearer).
- Headings/titles: "Experiment" → 実験してみる · "Full script: `…`" → スクリプト全体：`…` · "Tune it" → 調整してみる ·
  "The values" → 設定値 · "Try it" → 試してみる · "Look at it from ROS 2" → ROS 2 から見る.
- More terms: ground plane → グラウンドプレーン · visual mesh → ビジュアルメッシュ · mimic joint → mimic ジョイント ·
  yaw rate → ヨー角速度 · collision (shape) → 衝突形状 · override / override layer → オーバーライド / オーバーライドレイヤー ·
  instance / instancing → インスタンス / インスタンス化 · "lime" as a colour → ライムグリーン (keeps it apart from the robot) ·
  upstream → upstream · max force (prose) → 最大力 (GUI field stays **Max Force**) · standoff → スペーサー.
- Bold sentence lead-ins stay sentences: 「**Isaac Sim がはじめての人。**」. Troubleshooting labels:
  `**Symptom.** / **Cause.** / **Fix.**` → `**症状：** / **原因：** / **対処：**`; table header "Symptom | Fix" → 症状 | 対処.
- Headings: "Run it" → 実行してみる · "The graph(s)" → グラフ · "See it in RViz" → RViz で見る ·
  "Where to go from here" → この先へ · "Part N: …" → パート N：… · "ROS 2 in 10 minutes" → 10 分でわかる ROS 2.
- Durations under a second in prose: ミリ秒 (75 ミリ秒). Tutorial-number ranges: 00〜05.
- More terms: extension → 拡張機能 · parameter → パラメーター · message type → メッセージ型 · trajectory → 軌道 ·
  planning scene → プランニングシーン · leaf (behavior tree) → 葉（リーフ） · behaviour (py_trees) → ビヘイビア ·
  recovery → リカバリー · thing (tutorial 16) → 物 · pillar / divider / crate → 柱 / 仕切り / 箱 · cup/mug (the object) → マグカップ
  (YOLO class labels such as `cup`, *frisbee* stay English) · convex hull / decomposition → 凸包 / 凸分解 (GUI values stay English).
- Behavior-tree behaviour names that appear in diagrams or logs stay English in prose (**What now?**, **Leave it**) so
  readers can match them; a short Japanese gloss once is fine.
- Quoted log/error messages stay English: 「*Failed to make progress*」.

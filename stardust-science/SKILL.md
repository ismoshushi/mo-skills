# 星尘科普动画 · Stardust Science

输入一个科学概念，输出一部「粒子 + 矢量 Canvas」科普动画成片（MP4）。

## 什么时候用

用户想做一期科普短视频（科学概念讲解、纪录片式动画），且希望全流程可控、可复现时，用本 skill。
不适合：实拍剪辑、AI 生成视频（Sora/Seedance 那类走外部模型的）。

## 流程（必须按顺序）

### 1. 调研
用联网搜索核实用户给的科学概念：定义、关键数据（数字、单位、年份）、2–3 个最出彩的"视觉钩子"。
只用可信来源（百科、论文、官方机构）；不确定的数字宁可不写，也不要编。

### 2. 写分镜脚本 → 用户确认
按 `references/pipeline.md` 的分镜 JSON 格式写脚本，每镜包含：
`type / duration / title / subtitle / narration / labels|bars|bodies`。
**必须把分镜脚本发给用户确认后再往下走**，用户改哪里就改哪里。

### 3. 收集图片（可选）
本 skill 默认纯 Canvas 绘制、不依赖外部图片。如分镜需要真实照片（如星系实拍），
只用明确可商用/授权的图源，并在成片片尾标注来源；找不到授权图就改用矢量绘制。

### 4. 生成
```bash
python3 scripts/build.py 分镜.json -o 作品/黑洞
```
得到自包含的 `作品/黑洞/index.html`，直接用浏览器打开即可预览（`window.seek(t)` 跳转）。

### 5. 渲染成片
```bash
node scripts/render.mjs 作品/黑洞/index.html -o 黑洞.mp4
# 有旁白音频：
node scripts/render.mjs 作品/黑洞/index.html --audio 口播.wav -o 黑洞.mp4
```
render.mjs 会用无头 Chrome 逐帧截图（30fps、1920×1080），再用 ffmpeg 合成 H.264 + 音频。
常用选项：`--preview`（快速预览）、`--stills 2.1,7.5`（抽静帧检查）、`--no-audio`。

### 6. 质检
- 抽 3–5 张静帧检查：文字有无截断/叠字、粒子文字是否成形、标注线是否对齐。
- 数字、单位、人名与第 1 步调研来源逐条核对。
- 有问题改分镜 JSON，重新 build + render，不要手工改生成的 HTML。

## 镜头类型

| type | 用途 | 关键字段 |
|---|---|---|
| title | 粒子大字开场 | title / subtitle |
| blackhole | 黑洞/吸积盘粒子 | labels（左右标注） |
| orbits | 轨道示意（恒星-行星-卫星） | bodies |
| bars | 数据对比条 | bars[{label, value, note}] |
| outro | 粒子字收尾 | title / subtitle |

## 依赖

- Node 18+（render.mjs 零 npm 依赖，用 Node 自带 WebSocket + CDP）
- Chrome / Chromium（`CHROME_PATH` 环境变量或自动查找）
- ffmpeg
- Python 3（build.py 仅用标准库）

## 出处说明

本 skill 为独立实现的原创作品，流程设计灵感来自 YouMind 平台的质感粒子科普动画 skill
（公开页面描述），代码、模板与渲染管线均为原创。
`scripts/render.mjs` 改编自 dashi-animationstyle 的无头 Chrome 逐帧渲染器（同一作者）。

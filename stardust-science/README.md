# 星尘科普动画 · Stardust Science

输入一个科学概念，输出一部「粒子 + 矢量 Canvas」科普动画成片（MP4）。

风格：深空黑底、星空视差、金白星芒粒子大字、纪录片式中文字幕——高端科学纪录片 +
博物馆级科研可视化质感。全流程代码生成，不依赖外部视频模型。

## 安装

```bash
# Claude Code / Codex 通用
npx -y skills add <你的仓库地址> --skill stardust-science

# 或手动：把本目录拷到
#   ~/.claude/skills/stardust-science   (Claude Code)
#   .agents/skills/stardust-science     (Codex)
```

## 快速开始

```bash
# 1. 写分镜（见 references/pipeline.md，examples/blackhole.json 是完整示例）
# 2. 生成舞台 HTML（可直接浏览器打开预览）
python3 scripts/build.py examples/blackhole.json -o 作品/黑洞

# 3. 渲染成片（无头 Chrome 逐帧截图 + ffmpeg 合成，30fps / 1920×1080）
node scripts/render.mjs 作品/黑洞/index.html -o 黑洞.mp4

# 有旁白音频时：
node scripts/render.mjs 作品/黑洞/index.html --audio 口播.wav -o 黑洞.mp4

# 快速预览 / 抽静帧检查
node scripts/render.mjs 作品/黑洞/index.html --preview
node scripts/render.mjs 作品/黑洞/index.html --stills 2.0,6.5,12.0
```

## 完整流程（Agent 用）

1. **调研**：联网核实科学概念的定义与关键数据（只用可信来源，不编数字）
2. **分镜**：按 `references/pipeline.md` 写分镜 JSON，**发用户确认后再往下走**
3. **图片（可选）**：默认纯 Canvas 绘制；如需实拍图只用明确授权的图源
4. **生成**：`build.py` → 自包含 `index.html`
5. **渲染**：`render.mjs` → MP4（H.264）
6. **质检**：抽静帧看截断/叠字，数字与来源逐条核对

详见 `SKILL.md`。

## 镜头类型

| type | 用途 |
|---|---|
| title | 粒子大字开场 |
| blackhole | 黑洞吸积盘粒子 + 左右标注 |
| orbits | 轨道示意（恒星-行星-卫星） |
| bars | 数据对比条 |
| outro | 粒子字收尾 |

## 依赖

- Node 18+、Chrome/Chromium、ffmpeg、Python 3（均只用标准库 / 零 npm 依赖）

## 许可证

MIT，见 LICENSE。

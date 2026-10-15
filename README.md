# mo-skills

魔术师的 Agent Skills 合集。每个 skill 独立一个文件夹，开箱即用。

## Skills

| Skill | 一句话 | 目录 |
|---|---|---|
| 星尘科普动画 · Stardust Science | 输入科学概念，输出「粒子 + 矢量 Canvas」科普动画成片（MP4）：联网调研 → 分镜确认 → Canvas 粒子渲染 → 无头 Chrome 逐帧导出 | [stardust-science](./stardust-science) |

## 安装单个 skill（Claude Code / Codex 通用）

```bash
npx -y skills add ismoshushi/mo-skills --skill stardust-science
```

也可以把对应文件夹拷到 `~/.claude/skills/`（Claude Code）或 `.agents/skills/`（Codex）。

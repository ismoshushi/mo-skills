# mo-skills

魔术师的 Agent Skills 合集。每个 skill 独立一个文件夹，开箱即用。

## Skills

| Skill | 一句话 | 来源 | 目录 |
|---|---|---|---|
| 星尘科普动画 · Stardust Science | 输入科学概念，输出「粒子 + 矢量 Canvas」科普动画成片（MP4）：联网调研 → 分镜确认 → Canvas 粒子渲染 → 无头 Chrome 逐帧导出 | 原创 | [stardust-science](./stardust-science) |
| 中文长篇小说 · Chinese Novelist | 一句指令开写 10–50 章中文长篇小说：三层问答定大纲 → 逐章创作（3000–5000 字/章）→ 自动校验去 AI 味 | 收录自 [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)（MIT；演示图片外链原仓库） | [chinese-novelist](./chinese-novelist) |
| 微信公众号文章 · WeChat Article | 公众号发文一条龙：爆款技法写稿 → Markdown 转排版 HTML → API 建草稿（或手动发布） | 原创整理 | [wechat-article](./wechat-article) |
| 今日头条发文 · Toutiao Article | 头条发文一条龙：算法逻辑写稿（标题/微头条）→ Playwright 浏览器自动化建草稿 | 原创整理 | [toutiao-article](./toutiao-article) |

## 安装单个 skill（Claude Code / Codex 通用）

```bash
npx -y skills add ismoshushi/mo-skills --skill chinese-novelist
```

`--skill` 后换成上表中的目录名即可。也可以把对应文件夹拷到 `~/.claude/skills/`（Claude Code）或 `.agents/skills/`（Codex）。

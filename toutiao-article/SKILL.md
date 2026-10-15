---
name: toutiao-article
description: |
  往今日头条（头条号）发内容的一条龙 skill：按头条算法逻辑写稿（标题 30 字内、
  开头 100 字出钩子、微头条短体裁），再用浏览器自动化建草稿（文章/微头条）。
  头条没有公开的发布 API，本 skill 走 Playwright 浏览器自动化路线。
  当用户说：发头条、写微头条、发布到今日头条时使用。
metadata:
  trigger: 发头条、写微头条、发布到今日头条、头条号发文
  version: 1.0.0
---

# Toutiao Article：今日头条发文一条龙

## 先说清楚

今日头条**没有**像微信公众号那样的公开文章发布 API。
业内通用做法是浏览器自动化：扫码登录一次保存会话，之后自动填标题、
贴正文、传封面、存草稿。本 skill 按这个路线做。

## 流程总览

```
用户给主题/素材
  → [1. 定体裁] 长文章（图文）还是微头条？→ 用户确认
  → [2. 写稿] 按 references/writing.md 的头条技法写
  → [3. 发布] scripts/toutiao_publish.py 浏览器自动化建草稿
       → 用户去 mp.toutiao.com 草稿箱检查，手动点发布
```

> 原则：脚本只建草稿、不自动发布。发布是不可逆操作，这一下必须人来点。

## 各阶段说明

### 1. 定体裁（二选一，用户确认）

- **长文章**：深度内容，2000 字以上，需要标题（≤30 字）+ 封面图（16:9）
- **微头条**：300–500 字短内容 + 最多 9 张图，流量更大、更吃标题和开头

### 2. 写稿

读 `references/writing.md`。头条和公众号写法不一样，核心差异：
- 标题 ≤ 30 字，是生死线（算法推荐全看它）
- 开头 100 字内必须出钩子，比公众号更快
- 原创首发加权，洗稿会被限流

### 3. 发布

```bash
pip install playwright && playwright install chromium

# 首次：扫码登录（手机头条 APP 扫），会话自动保存
python3 scripts/toutiao_publish.py login

# 发长文章（Markdown 或 HTML 都行，自动转）
python3 scripts/toutiao_publish.py draft --title "标题" --content 文章.md --cover 封面.png

# 发微头条
python3 scripts/toutiao_publish.py weitoutiao --content 微头条.md --images 图1.png 图2.png
```

发布细节（登录有效期、标题截断规则、封面要求）见 `references/publishing.md`。

## 文件说明

| 文件 | 干嘛的 |
|---|---|
| `references/writing.md` | 头条写作技法：算法逻辑、标题公式、微头条体裁 |
| `references/publishing.md` | 发布指南：登录、会话、草稿流程、注意事项 |
| `scripts/toutiao_publish.py` | Playwright 浏览器自动化：登录/发文章/发微头条 |
| `examples/sample.md` | 示例稿（微头条体） |

# 今日头条发布指南

## 为什么走浏览器自动化

今日头条**没有公开的文章发布 API**（微信公众号有 `draft/add`，头条没有）。
社区通用方案：Playwright 控制真实浏览器，扫码登录一次，会话保存后自动发布。
反爬存在，操作间隔留 3–5 秒，不要批量狂发。

## 1. 环境准备（一次性）

```bash
pip install playwright
playwright install chromium   # 或用你本机已装的 Chrome，加 --executable-path
```

## 2. 扫码登录（一次性，会话 7 天左右有效）

```bash
python3 scripts/toutiao_publish.py login
```

浏览器会自动打开头条号登录页（https://mp.toutiao.com），
用**手机今日头条 APP 扫码**登录。成功后会话存到
`~/.config/toutiao-article/session.json`，7 天内免登录。
过期了重新跑一遍 `login` 就行。

## 3. 发布（只建草稿，不自动发）

```bash
# 长文章：标题≤30字（超长自动截断并提示），内容支持 md/html/txt
python3 scripts/toutiao_publish.py draft \
  --title "文章标题" --content 文章.md --cover 封面.png

# 微头条：300-500字，配图最多9张
python3 scripts/toutiao_publish.py weitoutiao \
  --content 微头条.md --images 图1.png 图2.png 图3.png
```

跑完去 https://mp.toutiao.com 草稿箱检查，手动点发布。
**脚本永远不会点"发布"**，这是故意留的安全边界。

## 4. 规格要求

| 项 | 要求 |
|---|---|
| 文章标题 | 2–30 字，超长自动截断（会打印提示） |
| 封面图 | 16:9，JPG/PNG，小于 5MB |
| 微头条图片 | 最多 9 张 |
| 原创声明 | 默认不勾，在草稿箱手动勾（按实际情况） |

## 5. 注意事项

- 页面改版会导致选择器失效：脚本按"先找文本、再找角色"写，尽量扛改版；
  如果某天跑不通，把报错发回来，我来修选择器
- 不要短时间内连发多篇，间隔 5 分钟以上
- 首次跑建议先用 `--headless` 关掉（默认有头），看着它操作一遍确认没问题
- 会话文件含登录态，别传给别人，别提交到 git

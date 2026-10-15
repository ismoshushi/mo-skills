# 今日头条发文 · Toutiao Article

往今日头条（头条号）发内容的一条龙 skill：**写稿 → 发布**。

## 先说清楚

头条**没有**公开的文章发布 API（不像微信公众号），所以发布走的是
**Playwright 浏览器自动化**：扫码登录一次，会话保存 7 天，之后自动填标题、
贴正文、传封面、存草稿。**脚本只建草稿、不点发布**，最后一下你自己去
mp.toutiao.com 草稿箱点。

## 能干嘛

- **写稿**：按头条算法逻辑写——标题 ≤30 字、开头 100 字出钩子、微头条 300–500 字短体裁（`references/writing.md`）
- **发长文章**：标题+正文+封面，自动存草稿
- **发微头条**：正文+最多 9 张配图，自动存草稿

## 快速上手

```bash
pip install playwright && playwright install chromium

# 1. 扫码登录（手机头条 APP 扫，会话存 7 天）
python3 scripts/toutiao_publish.py login

# 2a. 发长文章
python3 scripts/toutiao_publish.py draft --title "标题" --content 文章.md --cover 封面.png

# 2b. 发微头条
python3 scripts/toutiao_publish.py weitoutiao --content 微头条.md --images 图1.png 图2.png

# 3. 去 mp.toutiao.com 草稿箱检查，手动发布
```

## 协议

MIT，见 [LICENSE](./LICENSE)。原创整理。

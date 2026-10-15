# 微信公众号文章 · WeChat Article

一个 skill 干完公众号发文的全部脏活：**写稿 → 排版 → 发布**。

## 能干嘛

- **写稿**：按公众号爆款技法写——标题公式、3 秒开头钩子、小标题节奏、金句结尾（`references/writing.md`）
- **排版**：`scripts/md2gzh.py` 把 Markdown 转成公众号兼容 HTML，全内联样式，手机端字号/行距已调好，零依赖本地可跑
- **发布**：`scripts/gzh_draft.py` 调微信官方接口传图、建草稿（只建草稿不群发，安全边界留给你点那一下）；嫌麻烦也可以手动复制 HTML 去后台

## 快速上手

```bash
# 1. 写稿（Markdown，见 examples/sample.md 的格式）
# 2. 排版
python3 scripts/md2gzh.py 稿件.md -o article.html --theme green
# 3. 发布（二选一）
export GZH_APPID="wx..." GZH_APPSECRET="..."
python3 scripts/gzh_draft.py upload cover.png            # 拿封面 media_id
python3 scripts/gzh_draft.py draft --title "标题" --html article.html --cover MEDIA_ID
# 4. 去 mp.weixin.qq.com 草稿箱检查，手动群发
```

## 主题色

`--theme` 可选 `green`（微信绿，默认）/ `blue` / `orange` / `pink`，排版规范见 `references/typesetting.md`。

## 协议

MIT，见 [LICENSE](./LICENSE)。原创整理。

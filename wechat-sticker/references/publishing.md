# 存草稿与发表

## 存草稿（官方 API）

```bash
export GZH_APPID="wx..."
export GZH_APPSECRET="..."

python3 scripts/sticker_draft.py \
  --title "一句话标题" \
  --copy 文案.txt \
  --images 主图.png 对比.png 能力.png 场景.png \
  --author "作者名（可选）"
```

脚本做的事：
1. 校验文案 ≤250 字（超了直接报错退出）
2. 4 张图经 `uploadimg` 上传拿微信 CDN URL
3. 第 1 张图再经 `add_material` 拿 `media_id` 做封面
4. 调 `draft/add` 建图文草稿（标题 + 文案 + 4 张图）
5. 打印 `media_id`，结束

## 核查（存完必须做）

- [ ] 去 mp.weixin.qq.com 草稿箱，看到这篇草稿
- [ ] 点开：标题、文案、4 张图都在，顺序对
- [ ] 文案没被截断，图片能正常加载

## 手机端发表（人来做）

1. 公众号助手 App → 草稿箱 → 找到这篇
2. 逐条预览：图齐全、文案完整、风格统一
3. 没问题 → 点"发表"，当场扫码验证
4. 一次只发一条，不攒一批盲发

## 禁区

- 脚本没有群发功能，也永远不会加
- 不要把 AppSecret 写进代码或发给别人，用环境变量
- IP 白名单：在公众号后台把服务器 IP 加进白名单，否则调 API 报 40164

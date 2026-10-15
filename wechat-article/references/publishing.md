# 公众号发布指南

发文只有两种路线，按你的情况二选一。

## 路线 A：API 自动建草稿（推荐，一劳永逸）

### 1. 准备工作（一次性，5 分钟）

1. 登录 [mp.weixin.qq.com](https://mp.weixin.qq.com)，左下角"设置与开发 → 基本配置"
2. 拿到 **开发者 ID（AppID）** 和 **开发者密码（AppSecret）**
3. 把服务器 IP 加进"IP 白名单"（脚本跑在哪台机器就加哪台）
4. 在 shell 里设环境变量（别写进代码）：
   ```bash
   export GZH_APPID="wx1234567890abcdef"
   export GZH_APPSECRET="abcdefghijklmnopqrstuvwxyz123456"
   ```

> 订阅号/服务号都支持草稿接口。个人订阅号每天群发 1 次，写之前想好节奏。

### 2. 用法

```bash
# 先传封面图，拿到 media_id
python3 scripts/gzh_draft.py upload cover.png
# 建草稿（正文用排版后的 HTML）
python3 scripts/gzh_draft.py draft --title "标题" --html article.html --cover MEDIA_ID --digest "摘要（选填）"
```

成功后去公众号后台"草稿箱"能看到这篇，检查一遍点"群发"就行。
**群发是不可逆操作**，脚本只建草稿不群发，这个边界是故意留的。

### 3. 接口说明

脚本只用标准库（urllib），零依赖，调的是微信官方接口：
- `cgi-bin/token` — 拿 access_token（2 小时有效，脚本自动缓存复用）
- `cgi-bin/media/uploadimg` — 上传正文内图片，返回 URL
- `cgi-bin/material/add_material` — 上传封面图（永久素材），返回 media_id
- `cgi-bin/draft/add` — 创建草稿

封面图要求：900×500 以上，JPG/PNG，小于 2MB。

## 路线 B：手动复制（零配置，适合偶尔发）

1. 跑 `scripts/md2gzh.py 稿件.md -o article.html`，浏览器打开预览
2. 公众号后台新建图文，全选复制 HTML 内容粘贴进去
   （直接粘贴渲染后的页面，不是粘贴代码——样式是内联的，会跟着走）
3. 上传封面图、写摘要、预览（一定用手机预览一遍）
4. 存草稿 → 群发

## 发前检查（两条路线通用）

- [ ] 手机预览：没有错位、没有超宽图片、代码块能横滑
- [ ] 所有图片都显示（防盗链图会挂，传到公众号素材库最稳）
- [ ] 标题、摘要、封面三件套齐了
- [ ] 原创声明按需勾选（洗稿/整合类内容别勾）
- [ ] 定时群发 vs 立即群发想清楚

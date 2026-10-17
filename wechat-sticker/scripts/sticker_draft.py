#!/usr/bin/env python3
"""微信贴图号：官方 API 存图文草稿（多图少文近似贴图形态）.

配置（环境变量，不要写进代码）:
    export GZH_APPID="wx..."
    export GZH_APPSECRET="..."

用法:
    python3 sticker_draft.py --title "一句话标题" --copy 文案.txt \
        --images 主图.png 对比.png 能力.png 场景.png [--author 作者名]

流程: 校验文案<=250字 -> 4张图 uploadimg 拿URL -> 第1张加传封面拿 media_id
      -> draft/add 建图文草稿 -> 打印 media_id.

注意：只建草稿、不群发。发表请去公众号后台/手机端手动点。
"""
import argparse
import json
import os
import sys
import time
import urllib.request

API = "https://api.weixin.qq.com"
TOKEN_CACHE = os.path.expanduser("~/.cache/wechat-sticker-token.json")
MAX_COPY_LEN = 250


def _get(env):
    v = os.environ.get(env)
    if not v:
        sys.exit("缺少环境变量 %s，请先 export %s=..." % (env, env))
    return v


def _http(url, data=None, files=None):
    if files:
        boundary = "----stk%d" % int(time.time() * 1000)
        body = b""
        for name, (filename, content, ctype) in files.items():
            body += (
                '--%s\r\nContent-Disposition: form-data; name="%s"; '
                'filename="%s"\r\nContent-Type: %s\r\n\r\n'
                % (boundary, name, filename, ctype)
            ).encode() + content + b"\r\n"
        body += ("--%s--\r\n" % boundary).encode()
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary})
    elif data is not None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url, data=raw, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _check(resp, action):
    if resp.get("errcode", 0) != 0:
        sys.exit("%s 失败：%s（errcode=%s）\n常见原因：IP 不在白名单 / AppSecret 错误 / 图片超限"
                 % (action, resp.get("errmsg"), resp.get("errcode")))
    return resp


def get_token():
    try:
        cache = json.load(open(TOKEN_CACHE))
        if cache["expires_at"] > time.time() + 300:
            return cache["token"]
    except (OSError, KeyError, ValueError):
        pass
    appid = _get("GZH_APPID")
    secret = _get("GZH_APPSECRET")
    url = ("%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"
           % (API, appid, secret))
    resp = _check(_http(url), "获取 access_token")
    os.makedirs(os.path.dirname(TOKEN_CACHE), exist_ok=True)
    json.dump({"token": resp["access_token"],
               "expires_at": time.time() + resp["expires_in"]},
              open(TOKEN_CACHE, "w"))
    return resp["access_token"]


def upload_image_url(path):
    token = get_token()
    with open(path, "rb") as f:
        content = f.read()
    ctype = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    resp = _check(_http(
        "%s/cgi-bin/media/uploadimg?access_token=%s" % (API, token),
        files={"media": (os.path.basename(path), content, ctype)}),
        "上传正文图片 %s" % path)
    return resp["url"]


def upload_cover_media_id(path):
    size = os.path.getsize(path)
    if size > 2 * 1024 * 1024:
        sys.exit("封面图 %.1fMB 超过 2MB 限制，请先压缩" % (size / 1024 / 1024))
    token = get_token()
    with open(path, "rb") as f:
        content = f.read()
    ctype = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    resp = _check(_http(
        "%s/cgi-bin/material/add_material?access_token=%s&type=image" % (API, token),
        files={"media": (os.path.basename(path), content, ctype)}),
        "上传封面图")
    return resp["media_id"]


def build_content(copy_text, img_urls):
    parts = ["<p>%s</p>" % copy_text]
    for u in img_urls:
        parts.append('<p><img src="%s" /></p>' % u)
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="微信贴图号：官方 API 存图文草稿（只建草稿不群发）")
    ap.add_argument("--title", required=True, help="一句话标题")
    ap.add_argument("--copy", required=True, help="文案文件（<=250字，含标点空格）")
    ap.add_argument("--images", nargs="+", required=True, help="图片文件（建议4张：主图/对比/能力/场景）")
    ap.add_argument("--author", default="", help="作者名")
    a = ap.parse_args()

    with open(a.copy, encoding="utf-8") as f:
        copy_text = f.read().strip()
    if len(copy_text) > MAX_COPY_LEN:
        sys.exit("文案 %d 字，超过 %d 字上限，请删减后重试" % (len(copy_text), MAX_COPY_LEN))
    if len(copy_text) == 0:
        sys.exit("文案是空的")
    if len(a.images) < 4:
        print("提醒：贴图规范是 4 张图，你只给了 %d 张" % len(a.images))

    print("文案 %d 字，OK" % len(copy_text))
    img_urls = []
    for p in a.images:
        url = upload_image_url(p)
        img_urls.append(url)
        print("已上传：%s" % p)
    cover_id = upload_cover_media_id(a.images[0])
    print("封面 media_id：%s" % cover_id)

    token = get_token()
    article = {
        "title": a.title,
        "author": a.author,
        "digest": copy_text[:60],
        "content": build_content(copy_text, img_urls),
        "content_source_url": "",
        "thumb_media_id": cover_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    resp = _check(_http(
        "%s/cgi-bin/draft/add?access_token=%s" % (API, token),
        data={"articles": [article]}), "创建草稿")
    print("草稿已创建，media_id: %s" % resp["media_id"])
    print("去 mp.weixin.qq.com → 草稿箱检查，手机端预览后手动发表。")


if __name__ == "__main__":
    main()

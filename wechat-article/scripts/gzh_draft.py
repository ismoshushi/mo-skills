#!/usr/bin/env python3
"""微信公众号 API：上传图片、创建草稿（零依赖，只用标准库）.

配置（环境变量，不要写进代码）:
    export GZH_APPID="wx..."
    export GZH_APPSECRET="..."

用法:
    # 上传封面图（永久素材），返回 media_id
    python3 gzh_draft.py upload cover.png

    # 上传正文内图片，返回可直接用的 URL
    python3 gzh_draft.py uploadimg body1.png

    # 创建草稿（HTML 来自 md2gzh.py 的输出）
    python3 gzh_draft.py draft --title "标题" --html article.html \\
        --cover MEDIA_ID --digest "摘要" --author "作者"

注意：脚本只建草稿、不群发。群发请去公众号后台手动点，这是故意留的安全边界。
"""
import json
import os
import sys
import time
import urllib.request
import urllib.parse

API = "https://api.weixin.qq.com"
TOKEN_CACHE = os.path.expanduser("~/.cache/wechat-article-token.json")


def _get(env: str) -> str:
    v = os.environ.get(env)
    if not v:
        sys.exit(f"缺少环境变量 {env}，请先 export {env}=...")
    return v


def _http(url: str, data=None, files=None):
    """极简 HTTP：支持 JSON POST、表单 POST、multipart 文件上传."""
    if files:
        boundary = "----gzh%d" % int(time.time() * 1000)
        body = b""
        for name, (filename, content, ctype) in files.items():
            body += (
                f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"\r\nContent-Type: {ctype}\r\n\r\n'
            ).encode() + content + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    elif data is not None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url, data=raw, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _check(resp: dict, action: str) -> dict:
    if resp.get("errcode", 0) != 0:
        sys.exit(f"{action} 失败：{resp.get('errmsg')}（errcode={resp.get('errcode')}）\n"
                 f"常见原因：IP 不在白名单 / AppSecret 错误 / 素材大小超限")
    return resp


def get_token() -> str:
    """拿 access_token，带本地缓存（有效期 2 小时，提前 5 分钟刷新）."""
    try:
        cache = json.load(open(TOKEN_CACHE))
        if cache["expires_at"] > time.time() + 300:
            return cache["token"]
    except (OSError, KeyError, ValueError):
        pass
    appid = _get("GZH_APPID")
    secret = _get("GZH_APPSECRET")
    url = (f"{API}/cgi-bin/token?grant_type=client_credential"
           f"&appid={appid}&secret={secret}")
    resp = _check(_http(url), "获取 access_token")
    os.makedirs(os.path.dirname(TOKEN_CACHE), exist_ok=True)
    json.dump({"token": resp["access_token"],
               "expires_at": time.time() + resp["expires_in"]},
              open(TOKEN_CACHE, "w"))
    return resp["access_token"]


def upload_image(path: str) -> str:
    """上传正文内图片，返回微信 CDN URL（直接嵌进 HTML img 用）."""
    token = get_token()
    with open(path, "rb") as f:
        content = f.read()
    ctype = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    resp = _check(_http(
        f"{API}/cgi-bin/media/uploadimg?access_token={token}",
        files={"media": (os.path.basename(path), content, ctype)}),
        "上传正文图片")
    return resp["url"]


def upload_cover(path: str) -> str:
    """上传封面图为永久素材，返回 media_id."""
    size = os.path.getsize(path)
    if size > 2 * 1024 * 1024:
        sys.exit(f"封面图 {size/1024/1024:.1f}MB 超过 2MB 限制，请先压缩")
    token = get_token()
    with open(path, "rb") as f:
        content = f.read()
    ctype = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    resp = _check(_http(
        f"{API}/cgi-bin/material/add_material?access_token={token}&type=image",
        files={"media": (os.path.basename(path), content, ctype)}),
        "上传封面图")
    return resp["media_id"]


def create_draft(title: str, html_path: str, cover_media_id: str,
                 digest: str = "", author: str = "") -> str:
    """创建草稿，返回 media_id。去后台草稿箱检查后手动群发."""
    token = get_token()
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    # 草稿接口要的是 content 字段（HTML），content_source_url 可空
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content,
        "content_source_url": "",
        "thumb_media_id": cover_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    resp = _check(_http(
        f"{API}/cgi-bin/draft/add?access_token={token}",
        data={"articles": [article]}),
        "创建草稿")
    return resp["media_id"]


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: gzh_draft.py upload|uploadimg|draft ...（详见文件头注释）")
    cmd = sys.argv[1]
    if cmd in ("upload", "uploadimg") and len(sys.argv) < 3:
        sys.exit(f"用法: gzh_draft.py {cmd} <图片路径>")
    if cmd == "upload":
        print("cover media_id:", upload_cover(sys.argv[2]))
    elif cmd == "uploadimg":
        print("图片 URL:", upload_image(sys.argv[2]))
    elif cmd == "draft":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("--title", required=True)
        ap.add_argument("--html", required=True)
        ap.add_argument("--cover", required=True, help="封面图 media_id")
        ap.add_argument("--digest", default="")
        ap.add_argument("--author", default="")
        a = ap.parse_args(sys.argv[2:])
        mid = create_draft(a.title, a.html, a.cover, a.digest, a.author)
        print(f"草稿已创建，media_id: {mid}")
        print("去 mp.weixin.qq.com → 草稿箱检查，确认无误后手动群发。")
    else:
        sys.exit(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()

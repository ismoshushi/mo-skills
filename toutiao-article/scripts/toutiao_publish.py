#!/usr/bin/env python3
"""Toutiao publisher via browser automation (Playwright).

头条没有公开的文章发布 API，本脚本用浏览器自动化完成：
扫码登录一次保存会话，之后自动填标题、贴正文、传封面、存草稿。

依赖:
    pip install playwright && playwright install chromium

用法:
    python3 toutiao_publish.py login
    python3 toutiao_publish.py draft --title "标题" --content 文章.md [--cover 封面.png]
    python3 toutiao_publish.py weitoutiao --content 微头条.md [--images 图1.png 图2.png]

注意：脚本只建草稿、不点"发布"。发布请去 mp.toutiao.com 草稿箱手动点。
"""

import argparse
import os
import re
import sys
import time

SESSION_DIR = os.path.expanduser("~/.config/toutiao-article")
SESSION_FILE = os.path.join(SESSION_DIR, "session.json")
MP_HOME = "https://mp.toutiao.com/"
ARTICLE_URL = "https://mp.toutiao.com/profile_v4/graphic/publish"
WEITOUTIAO_URL = "https://mp.toutiao.com/profile_v4/weitoutiao/publish"

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    HAS_PW = True
except ImportError:
    HAS_PW = False
    PwTimeout = Exception


def need_pw():
    if not HAS_PW:
        sys.exit("缺少 playwright，请先执行：pip install playwright && playwright install chromium")


def md_to_html(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if path.endswith((".html", ".htm")):
        return src
    import html as htmllib
    out = []
    para = []
    for line in src.split("\n"):
        s = line.strip()
        if not s:
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            continue
        if s.startswith("### "):
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            out.append("<h3>" + htmllib.escape(s[4:]) + "</h3>")
        elif s.startswith("## "):
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            out.append("<h2>" + htmllib.escape(s[3:]) + "</h2>")
        elif s.startswith("# "):
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            out.append("<h1>" + htmllib.escape(s[2:]) + "</h1>")
        elif s.startswith(">"):
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            out.append("<blockquote>" + htmllib.escape(s.lstrip(">").strip()) + "</blockquote>")
        elif re.match(r"^([-*]|\d+[.)])\s+", s):
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            item = re.sub(r"^([-*]|\d+[.)])\s+", "", s)
            out.append("<p>- " + htmllib.escape(item) + "</p>")
        elif s in ("---", "***", "* * *"):
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para = []
            out.append("<p>* * *</p>")
        else:
            t = htmllib.escape(s)
            t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
            t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
            para.append(t)
    if para:
        out.append("<p>" + "<br>".join(para) + "</p>")
    return "\n".join(out)


def new_context(pw, headless):
    os.makedirs(SESSION_DIR, exist_ok=True)
    browser = pw.chromium.launch(headless=headless)
    if os.path.exists(SESSION_FILE):
        ctx = browser.new_context(storage_state=SESSION_FILE)
    else:
        ctx = browser.new_context()
    return browser, ctx


def save_session(ctx):
    ctx.storage_state(path=SESSION_FILE)
    print("会话已保存：" + SESSION_FILE)


def cmd_login(args):
    need_pw()
    with sync_playwright() as pw:
        browser, ctx = new_context(pw, headless=False)
        page = ctx.new_page()
        page.goto(MP_HOME)
        print("请在打开的浏览器里用【手机今日头条 APP】扫码登录…")
        print("登录成功后脚本会自动保存并退出（最长等 3 分钟）。")
        try:
            page.wait_for_function(
                "() => !location.href.includes('login') && "
                "document.body.innerText.includes('发布')",
                timeout=180000)
        except PwTimeout:
            print("等待超时：似乎还没登录成功，请重新跑 login。")
            browser.close()
            sys.exit(1)
        save_session(ctx)
        browser.close()
        print("登录完成，7 天内直接发文不用再扫码。")


def wait_editor(page, timeout=20000):
    sels = ["[contenteditable='true']", ".editor", "div[role='textbox']"]
    for sel in sels:
        try:
            el = page.wait_for_selector(sel, timeout=timeout // len(sels))
            if el:
                return el
        except PwTimeout:
            continue
    sys.exit("找不到正文编辑器：头条页面可能改版了，请把报错发回。")


def set_title(page, title):
    if len(title) > 30:
        print("提醒：标题 %d 字超 30 字上限，已截断为：%s" % (len(title), title[:30]))
        title = title[:30]
    cands = [
        page.get_by_placeholder(re.compile("标题")),
        page.locator("input").first,
    ]
    for c in cands:
        try:
            c.wait_for(timeout=8000)
            c.fill(title)
            return
        except Exception:
            continue
    sys.exit("找不到标题输入框：页面可能改版，请把报错发回。")


def cmd_draft(args):
    need_pw()
    if not os.path.exists(SESSION_FILE):
        sys.exit("还没登录，先跑：python3 toutiao_publish.py login")
    html = md_to_html(args.content)
    with sync_playwright() as pw:
        browser, ctx = new_context(pw, headless=args.headless)
        page = ctx.new_page()
        page.goto(ARTICLE_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        set_title(page, args.title)
        editor = wait_editor(page)
        editor.click()
        page.evaluate(
            "(el, html) => { el.focus(); "
            "document.execCommand('selectAll', false, null); "
            "document.execCommand('insertHTML', false, html); }",
            editor, html)
        print("正文已填入")
        if args.cover:
            try:
                page.set_input_files("input[type='file']", args.cover)
                print("封面已上传，等待回显…")
                time.sleep(4)
            except Exception as e:
                print("封面上传可能失败（%s），请去草稿箱手动传" % e)
        saved = False
        for pat in ["存草稿", "保存草稿", "保存"]:
            try:
                btn = page.get_by_role("button", name=re.compile(pat))
                btn.first.wait_for(timeout=5000)
                btn.first.click()
                saved = True
                break
            except Exception:
                continue
        if not saved:
            print("没找到存草稿按钮，浏览器保持打开，请手动点存草稿。")
            if not args.headless:
                input("手动存完草稿后回车退出…")
        else:
            time.sleep(3)
            print("已存为草稿。去 mp.toutiao.com 草稿箱检查，手动点发布。")
        browser.close()


def cmd_weitoutiao(args):
    need_pw()
    if not os.path.exists(SESSION_FILE):
        sys.exit("还没登录，先跑：python3 toutiao_publish.py login")
    if args.images and len(args.images) > 9:
        sys.exit("微头条最多配 9 张图")
    with open(args.content, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"^#{1,3}\s+", "", text, flags=re.M)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    if len(text) > 2000:
        print("提醒：微头条内容较长，300-500 字效果最好")
    with sync_playwright() as pw:
        browser, ctx = new_context(pw, headless=args.headless)
        page = ctx.new_page()
        page.goto(WEITOUTIAO_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        editor = wait_editor(page)
        editor.click()
        page.keyboard.type(text, delay=5)
        print("正文已填入")
        if args.images:
            try:
                page.set_input_files("input[type='file']", args.images)
                print("已上传 %d 张图，等待回显…" % len(args.images))
                time.sleep(4)
            except Exception as e:
                print("图片上传可能失败（%s），请去草稿箱手动传" % e)
        saved = False
        for pat in ["存草稿", "保存草稿", "保存"]:
            try:
                btn = page.get_by_role("button", name=re.compile(pat))
                btn.first.wait_for(timeout=5000)
                btn.first.click()
                saved = True
                break
            except Exception:
                continue
        if saved:
            time.sleep(2)
            print("已存为草稿，去草稿箱检查后手动发布。")
        else:
            print("没找到存草稿按钮。如页面只有发布按钮，请手动确认发布。")
        browser.close()


def main():
    ap = argparse.ArgumentParser(description="今日头条浏览器自动化发布（只建草稿不发布）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login", help="扫码登录并保存会话")
    d = sub.add_parser("draft", help="发长文章（存草稿）")
    d.add_argument("--title", required=True, help="标题（≤30字）")
    d.add_argument("--content", required=True, help="正文文件（md/html/txt）")
    d.add_argument("--cover", default=None, help="封面图（16:9 推荐）")
    d.add_argument("--headless", action="store_true", help="无头运行（已登录后可用）")
    w = sub.add_parser("weitoutiao", help="发微头条（存草稿）")
    w.add_argument("--content", required=True, help="正文文件")
    w.add_argument("--images", nargs="*", default=[], help="配图（最多9张）")
    w.add_argument("--headless", action="store_true")
    args = ap.parse_args()
    if args.cmd == "login":
        cmd_login(args)
    elif args.cmd == "draft":
        cmd_draft(args)
    elif args.cmd == "weitoutiao":
        cmd_weitoutiao(args)


if __name__ == "__main__":
    main()

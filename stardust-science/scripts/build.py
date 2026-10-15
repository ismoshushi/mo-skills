#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py：把分镜 JSON 注入舞台模板，生成可渲染的单文件 HTML。

用法：
    python3 build.py 分镜.json -o 作品目录/

分镜.json 格式见 README.md。镜头类型：title / blackhole / orbits / bars / outro。
输出：作品目录/index.html（自包含，可直接浏览器打开预览，也可被 render.mjs 逐帧渲染）。
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "template", "stage.html")

REQUIRED = {"type", "duration"}
KNOWN_TYPES = {"title", "blackhole", "orbits", "bars", "outro"}


def die(msg):
    print(f"build.py 错误：{msg}", file=sys.stderr)
    sys.exit(1)


def validate(sb):
    if not isinstance(sb, dict) or "shots" not in sb:
        die('分镜 JSON 顶层必须是 {"shots": [...]}')
    shots = sb["shots"]
    if not shots:
        die("shots 为空")
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            die(f"第 {i+1} 镜不是对象")
        missing = REQUIRED - set(s.keys())
        if missing:
            die(f"第 {i+1} 镜缺少字段：{sorted(missing)}")
        if s["type"] not in KNOWN_TYPES:
            die(f"第 {i+1} 镜 type 非法：{s['type']}（可选 {sorted(KNOWN_TYPES)}）")
        try:
            d = float(s["duration"])
        except (TypeError, ValueError):
            die(f"第 {i+1} 镜 duration 不是数字")
        if d <= 0:
            die(f"第 {i+1} 镜 duration 必须 > 0")
    return shots


def main():
    ap = argparse.ArgumentParser(description="分镜 JSON → 单文件 HTML")
    ap.add_argument("storyboard", help="分镜 JSON 文件")
    ap.add_argument("-o", "--outdir", default="作品", help="作品目录（默认 ./作品）")
    ap.add_argument("--template", default=TEMPLATE, help="舞台模板路径")
    args = ap.parse_args()

    if not os.path.isfile(args.storyboard):
        die(f"找不到分镜文件：{args.storyboard}")
    if not os.path.isfile(args.template):
        die(f"找不到模板：{args.template}")

    with open(args.storyboard, encoding="utf-8") as f:
        sb = json.load(f)
    shots = validate(sb)

    with open(args.template, encoding="utf-8") as f:
        tpl = f.read()

    marker = "window.STORYBOARD = window.STORYBOARD || "
    if marker not in tpl:
        die("模板里找不到 STORYBOARD 注入点")
    start = tpl.index(marker)
    # brace 配平找到示例 JSON 的结束位置
    i = start + len(marker)
    depth = 0
    in_str = False
    esc = False
    while i < len(tpl):
        ch = tpl[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    i += 1
                    break
        i += 1
    injected = "window.STORYBOARD = " + json.dumps(
        {"title": sb.get("title", ""), "shots": shots}, ensure_ascii=False
    ) + ";"
    html = tpl[:start] + injected + tpl[i:]

    total = sum(float(s["duration"]) for s in shots)
    os.makedirs(args.outdir, exist_ok=True)
    out_html = os.path.join(args.outdir, "index.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    meta = {
        "title": sb.get("title", ""),
        "duration": total,
        "shots": len(shots),
        "output": os.path.abspath(args.outdir) + ".mp4",
    }
    with open(os.path.join(args.outdir, "作品.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"OK：{out_html}")
    print(f"  镜头 {len(shots)} 个，总时长 {total:.1f} 秒")
    print(f"  预览：直接用浏览器打开 {out_html}")
    print(f"  渲染：node scripts/render.mjs {out_html}")


if __name__ == "__main__":
    main()

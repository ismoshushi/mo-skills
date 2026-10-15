#!/usr/bin/env python3
"""Markdown -> 微信公众号兼容 HTML（全部内联样式，零依赖）.

用法:
    python3 md2gzh.py 稿件.md [-o 输出.html] [--theme blue|orange|pink|green]

只转换正文。标题（#）转为文章大标题；封面、摘要请在公众号后台另行设置。
"""
import re
import sys
import html
import argparse

THEMES = {
    "blue":   "#1a73e8",
    "orange": "#e8590c",
    "pink":   "#d6336c",
    "green":  "#07c160",
}

BASE = ("font-size:15px;line-height:1.75;color:#3f3f3f;"
        "text-align:justify;letter-spacing:0.5px;")
P = f"<p style=\"{BASE}margin:0 0 16px 0;\">"


def inline(md: str) -> str:
    """处理行内：转义 -> code -> bold -> italic -> 图片 -> 链接"""
    md = html.escape(md)
    md = re.sub(r"`([^`]+)`",
                r'<code style="font-family:Menlo,Consolas,monospace;font-size:13px;'
                r'background:#f7f7f7;color:#d6336c;padding:2px 5px;border-radius:3px;">\1</code>', md)
    md = re.sub(r"\*\*([^*]+)\*\*",
                r'<strong style="color:{c};">\1</strong>'.format(c="{c}"), md)
    md = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", md)
    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"IMG::\1::\2", md)  # 图片占位，块级处理
    md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                r'<a href="\2" style="color:#576b95;text-decoration:none;">\1</a>', md)
    return md


def convert(md_text: str, theme: str) -> str:
    c = THEMES[theme]
    out = []
    lines = md_text.split("\n")
    i = 0
    in_code = False
    code_buf = []

    def flush_para(buf):
        text = " ".join(buf).strip()
        if text:
            out.append(P + inline(text).replace("{c}", c) + "</p>")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 代码块
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                code = html.escape("\n".join(code_buf))
                out.append(
                    '<pre style="font-family:Menlo,Consolas,monospace;font-size:13px;'
                    'line-height:1.6;background:#f7f7f7;border-radius:6px;'
                    'padding:12px;overflow-x:auto;white-space:pre;'
                    f'margin:0 0 16px 0;"><code>{code}</code></pre>')
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,3})\s+(.*)", stripped)
        if m:
            level, text = len(m.group(1)), inline(m.group(2)).replace("{c}", c)
            if level == 1:
                out.append(
                    f'<h1 style="font-size:20px;font-weight:bold;color:#111;'
                    f'text-align:center;margin:8px 0 20px 0;line-height:1.5;">{text}</h1>')
            elif level == 2:
                out.append(
                    f'<h2 style="font-size:16px;font-weight:bold;color:#111;'
                    f'border-left:4px solid {c};padding-left:10px;'
                    f'margin:24px 0 12px 0;line-height:1.5;">{text}</h2>')
            else:
                out.append(
                    f'<h3 style="font-size:15px;font-weight:bold;color:{c};'
                    f'margin:20px 0 10px 0;line-height:1.5;">{text}</h3>')
            i += 1
            continue

        # 引用
        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            text = "<br/>".join(inline(b).replace("{c}", c) for b in buf)
            out.append(
                f'<blockquote style="margin:0 0 16px 0;padding:10px 14px;'
                f'background:#f7f7f7;border-left:4px solid {c};'
                f'font-size:14px;color:#666;line-height:1.75;">{text}</blockquote>')
            continue

        # 分隔线
        if re.match(r"^---+$", stripped) or stripped in ("* * *", "***"):
            out.append(
                '<p style="text-align:center;color:#999;letter-spacing:8px;'
                'margin:20px 0;">＊ ＊ ＊</p>')
            i += 1
            continue

        # 列表
        if re.match(r"^([-*]|\d+[.)])\s+", stripped):
            items = []
            ordered = bool(re.match(r"^\d+[.)]\s+", stripped))
            while i < len(lines) and re.match(r"^([-*]|\d+[.)])\s+", lines[i].strip()):
                items.append(re.sub(r"^([-*]|\d+[.)])\s+", "", lines[i].strip()))
                i += 1
            lis = "".join(
                f"<li style=\"margin-bottom:8px;\">{inline(t).replace('{c}', c)}</li>"
                for t in items)
            dot = "decimal" if ordered else "disc"
            out.append(
                f"<ul style=\"list-style:{dot};padding-left:20px;"
                f"margin:0 0 16px 0;font-size:15px;line-height:1.75;color:#3f3f3f;\">"
                f"{lis}</ul>" if not ordered else
                f"<ol style=\"padding-left:20px;margin:0 0 16px 0;"
                f"font-size:15px;line-height:1.75;color:#3f3f3f;\">{lis}</ol>")
            continue

        # 图片（独立成行）
        m = re.match(r"^IMG::(.*)::(\S+)$", inline(stripped))
        if m:
            alt, url = m.group(1), m.group(2)
            out.append(
                f'<p style="text-align:center;margin:0 0 6px 0;">'
                f'<img src="{url}" alt="{alt}" style="max-width:100%;border-radius:6px;"/></p>')
            if alt:
                out.append(
                    f'<p style="text-align:center;font-size:12px;color:#999;'
                    f'margin:0 0 16px 0;">{alt}</p>')
            else:
                out.append('<p style="margin:0 0 16px 0;"></p>')
            i += 1
            continue

        # 普通段落（合并连续行）
        buf = [stripped]
        i += 1
        while (i < len(lines) and lines[i].strip()
               and not re.match(r"^(#{1,3}\s|>\s?|([-*]|\d+[.)])\s+|```|---+$)", lines[i].strip())
               and not lines[i].strip().startswith("IMG::")):
            # 注意：inline 之后图片才变 IMG::，这里用原文判断
            if re.match(r"^!\[", lines[i].strip()):
                break
            buf.append(lines[i].strip())
            i += 1
        flush_para(buf)

    body = "\n".join(out)
    return (f'<div style="max-width:677px;margin:0 auto;padding:0 4px;'
            f'font-family:-apple-system,BlinkMacSystemFont,\'Helvetica Neue\','
            f'\'PingFang SC\',\'Hiragino Sans GB\',\'Microsoft YaHei\',sans-serif;">\n'
            f'{body}\n</div>')


def main():
    ap = argparse.ArgumentParser(description="Markdown 转微信公众号 HTML")
    ap.add_argument("input", help="输入的 Markdown 文件")
    ap.add_argument("-o", "--output", help="输出 HTML 文件（默认打印到 stdout）")
    ap.add_argument("--theme", default="green", choices=list(THEMES),
                    help="主题色（默认 green 微信绿）")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        html_out = convert(f.read(), args.theme)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html_out)
        print(f"已生成：{args.output}")
    else:
        print(html_out)


if __name__ == "__main__":
    main()

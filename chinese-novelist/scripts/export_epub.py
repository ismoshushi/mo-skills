#!/usr/bin/env python3
"""合并章节并导出 EPUB（针对 issue #28），附带字数统计（issue #20）.

用法:
    python3 export_epub.py <项目目录> [-o 输出.epub] [--author 作者名]

项目目录指 chinese-novelist/{timestamp}-{书名}/，脚本自动按文件名排序读取
第XX章-*.md。只用标准库（zipfile），零依赖。
"""
import argparse
import html as htmllib
import json
import os
import re
import sys
import zipfile
from datetime import datetime


def md_to_xhtml(md_text):
    out = []
    para = []
    for line in md_text.split("\n"):
        s = line.strip()
        if not s:
            if para:
                out.append("<p>" + "<br/>".join(para) + "</p>")
                para = []
            continue
        if s.startswith("# "):
            if para:
                out.append("<p>" + "<br/>".join(para) + "</p>")
                para = []
            out.append("<h1>" + htmllib.escape(s[2:]) + "</h1>")
        else:
            t = htmllib.escape(s)
            t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
            para.append(t)
    if para:
        out.append("<p>" + "<br/>".join(para) + "</p>")
    return "\n".join(out)


def chapter_files(project_dir):
    files = []
    for name in os.listdir(project_dir):
        m = re.match(r"^第(\d+)章-(.+)\.md$", name)
        if m:
            files.append((int(m.group(1)), name))
    files.sort()
    return [os.path.join(project_dir, n) for _, n in files]


def count_chars(text):
    # 中文字符 + 去掉空白后的长度，作为"字数"口径
    return len(re.sub(r"\s+", "", text))


def build_epub(project_dir, out_path, author):
    plan_path = os.path.join(project_dir, "02-写作计划.json")
    title = os.path.basename(project_dir)
    if os.path.exists(plan_path):
        try:
            plan = json.load(open(plan_path, encoding="utf-8"))
            title = plan.get("novelName", title)
        except (OSError, ValueError):
            pass
    # 去掉目录名里的时间戳前缀
    title = re.sub(r"^\d{8}-\d{6}-", "", title)

    files = chapter_files(project_dir)
    if not files:
        sys.exit("项目目录里没有找到 第XX章-*.md 文件：%s" % project_dir)

    uid = "novel-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
    chapters = []
    total = 0
    for i, fp in enumerate(files):
        with open(fp, encoding="utf-8") as f:
            md = f.read()
        name = os.path.splitext(os.path.basename(fp))[0]
        body = md_to_xhtml(md)
        n = count_chars(md)
        total += n
        chapters.append((name, body, n))
        print("  %s：%d 字" % (name, n))
    print("共 %d 章，合计 %d 字" % (len(chapters), total))

    css = ("body{font-family:serif;line-height:1.8;margin:5%%;}"
           "h1{text-align:center;font-size:1.4em;margin:1em 0;}"
           "p{text-indent:2em;margin:0.6em 0;}")

    def xhtml(title_text, body_html):
        return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\"\n"
                "  \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n"
                "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n<head>\n"
                "<title>%s</title>\n"
                "<style type=\"text/css\">%s</style>\n"
                "</head>\n<body>\n%s\n</body>\n</html>"
                % (htmllib.escape(title_text), css, body_html))

    manifest_items = [
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx"/>']
    spine_items = []
    ncx_points = []
    for i, (name, body, _n) in enumerate(chapters):
        fid = "ch%02d" % i
        fname = "chapter%02d.xhtml" % i
        manifest_items.append(
            '    <item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (fid, fname))
        spine_items.append('    <itemref idref="%s"/>' % fid)
        ncx_points.append(
            '    <navPoint id="np%02d" playOrder="%d">\n'
            '      <navLabel><text>%s</text></navLabel>\n'
            '      <content src="%s"/>\n    </navPoint>'
            % (i, i + 1, htmllib.escape(name), fname))

    opf = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
           "<package xmlns=\"http://www.idpf.org/2007/opf\" version=\"2.0\" "
           "unique-identifier=\"uid\">\n"
           "  <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\">\n"
           "    <dc:identifier id=\"uid\">%s</dc:identifier>\n"
           "    <dc:title>%s</dc:title>\n"
           "    <dc:creator>%s</dc:creator>\n"
           "    <dc:language>zh-CN</dc:language>\n"
           "  </metadata>\n"
           "  <manifest>\n%s\n  </manifest>\n"
           "  <spine toc=\"ncx\">\n%s\n  </spine>\n"
           "</package>" % (uid, htmllib.escape(title), htmllib.escape(author),
                           "\n".join(manifest_items), "\n".join(spine_items)))

    ncx = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
           "<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n"
           "<head><meta name=\"dtb:uid\" content=\"%s\"/></head>\n"
           "<docTitle><text>%s</text></docTitle>\n"
           "<navMap>\n%s\n</navMap>\n</ncx>"
           % (uid, htmllib.escape(title), "\n".join(ncx_points)))

    container = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                 "<container version=\"1.0\" "
                 "xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">\n"
                 "  <rootfiles>\n"
                 "    <rootfile full-path=\"OEBPS/content.opf\" "
                 "media-type=\"application/oebps-package+xml\"/>\n"
                 "  </rootfiles>\n</container>")

    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container,
                   compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf,
                   compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx,
                   compress_type=zipfile.ZIP_DEFLATED)
        # manifest 里声明 ncx
        for i, (name, body, _n) in enumerate(chapters):
            z.writestr("OEBPS/chapter%02d.xhtml" % i,
                       xhtml(name, body),
                       compress_type=zipfile.ZIP_DEFLATED)
    print("EPUB 已生成：%s" % out_path)


def main():
    ap = argparse.ArgumentParser(description="合并章节导出 EPUB（含字数统计）")
    ap.add_argument("project_dir", help="项目目录 chinese-novelist/{timestamp}-{书名}/")
    ap.add_argument("-o", "--output", default=None, help="输出 epub 路径（默认 项目目录.epub）")
    ap.add_argument("--author", default="佚名", help="作者名")
    args = ap.parse_args()
    out = args.output or (args.project_dir.rstrip("/\\") + ".epub")
    build_epub(args.project_dir, out, args.author)


if __name__ == "__main__":
    main()

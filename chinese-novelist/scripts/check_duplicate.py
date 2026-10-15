#!/usr/bin/env python3
"""检查章节内的重复句子与雷同段落（针对 issue #25/#31）.

用法:
    python3 check_duplicate.py 第01章-xxx.md [--min-len 12]

规则:
- 句子：长度 >= min-len（默认12字）且在章内出现 2 次以上 → 标出
- 段落：整段完全相同的文字出现 2 次以上 → 标出
- 标点差异会被归一化，防止换个标点蒙混过关

退出码：0=干净，1=发现重复（可作为流程门禁）。
"""
import re
import sys
import argparse

_PUNCT_MAP = str.maketrans({
    "，": ",", "。": ".", "！": "!", "？": "?",
    "；": ";", "：": ":", "\u201c": '"', "\u201d": '"',
    "'": "'", "'": "'", "（": "(", "）": ")",
    "【": "[", "】": "]", "、": ",", "…": ".",
})


def normalize(s):
    s = s.translate(_PUNCT_MAP)
    return re.sub(r"\s+", "", s)


def split_sentences(text):
    out = []
    for lineno, line in enumerate(text.split("\n"), 1):
        line = line.strip().strip("#>*` -0123456789.").strip()
        if len(line) < 4:
            continue
        parts = re.split(r"(?<=[。！？.!?；;])", line)
        for p in parts:
            p = p.strip()
            if p:
                out.append((lineno, p))
    return out


def check(path, min_len):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    problems = 0
    seen = {}
    for lineno, sent in split_sentences(text):
        key = normalize(sent)
        if len(key) < min_len:
            continue
        seen.setdefault(key, []).append((lineno, sent))
    for key, occ in seen.items():
        if len(occ) >= 2:
            problems += 1
            lines = ",".join(str(l) for l, _ in occ)
            print("[重复句子 x%d] 行 %s：%s…" % (len(occ), lines, occ[0][1][:40]))
    paras = {}
    for lineno, line in enumerate(text.split("\n"), 1):
        p = line.strip()
        if len(p) < 20:
            continue
        key = normalize(p)
        paras.setdefault(key, []).append((lineno, p))
    for key, occ in paras.items():
        if len(occ) >= 2:
            problems += 1
            lines = ",".join(str(l) for l, _ in occ)
            print("[雷同段落 x%d] 行 %s：%s…" % (len(occ), lines, occ[0][1][:40]))
    if problems == 0:
        print("OK：未发现明显重复")
    else:
        print("发现 %d 处重复，请改写后再继续。" % problems)
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description="章节去重检查")
    ap.add_argument("path", help="章节 Markdown 文件")
    ap.add_argument("--min-len", type=int, default=12, help="句子最短判定长度（默认12字）")
    args = ap.parse_args()
    sys.exit(check(args.path, args.min_len))


if __name__ == "__main__":
    main()

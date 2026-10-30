#!/usr/bin/env python3
"""把上游姿势库单页改造成本站 pose/ 子页：域名、下载格式、来源链接全部本地化。"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "pose", "index_src.html")
DST = os.path.join(ROOT, "pose", "index.html")
BASE = "https://jasonbour.github.io/pose-costume-gallery-zh/pose/"
REPO = "https://github.com/JasonBour/pose-costume-gallery-zh"

s = open(SRC, encoding="utf-8").read()

# 1. 站点域名全部指向本站子目录
s = s.replace("https://ai-pose-gallery.anhao.app/", BASE)

# 2. 下载格式：原图已是 WebP
s = s.replace("下载原尺寸 PNG", "下载原图 WebP")
s = s.replace("`${item.id}.png`", "`${item.id}.webp`")
s = s.replace("900 × 1200 原尺寸 PNG", "900 × 1200 原图（WebP）")
s = s.replace("'900 × 1200 PNG'", "'900 × 1200 WebP'")

# 3. 顶栏：把上游仓库链接换成本站仓库，并加「返回总览」
s = s.replace(
    '<a class="action-btn author" href="https://github.com/anhao/ai-pose-gallery-zh"',
    '<a class="action-btn" href="../" aria-label="返回参考库总览">'
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.5 12 4l8 6.5"/><path d="M6 9.5V20h12V9.5"/></svg>'
    '<span class="action-text">总览</span></a>\n'
    '      <a class="action-btn author" href="' + REPO + '"',
)

# 4. 页脚署名：保留原作者与中文版维护者，补充本站托管说明
s = s.replace(
    "中文版由 Anhao 整理维护",
    "中文版由 Anhao 整理维护 · 本站为 GitHub 托管镜像",
)
s = s.replace(
    '<a href="https://github.com/anhao/ai-pose-gallery-zh"',
    '<a href="' + REPO + '"',
)

open(DST, "w", encoding="utf-8").write(s)
print("写入", DST, len(s), "字节")
print("未替换的 anhao.app 引用:", s.count("ai-pose-gallery.anhao.app"))

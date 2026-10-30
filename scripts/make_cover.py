#!/usr/bin/env python3
"""生成 1200×630 社交分享封面：左侧标题，右侧三张姿势缩略图圆角拼贴。"""
import os, glob, random
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
BG = (245, 247, 251)
ACCENT = (91, 91, 214)
TEXT = (23, 26, 33)
TEXT2 = (93, 100, 114)

FONT_B = "C:/Windows/Fonts/msyhbd.ttc"
FONT_R = "C:/Windows/Fonts/msyh.ttc"


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # 右上角柔光
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 620, -320, W + 220, 380], fill=(232, 234, 252))
    img = Image.blend(img, glow, 0.55)
    d = ImageDraw.Draw(img)

    # 右侧三张缩略图，等距一行（取标准系正面站姿，避免选到双人姿势）
    import json
    data = json.load(open(os.path.join(ROOT, "pose/data/pose-zh.json"), encoding="utf-8"))
    pool = [r["缩略图"] for r in data
            if r["体系"] == "全身单人・标准系" and r["角度"] == "正面"]
    random.seed(11)
    picks = [os.path.join(ROOT, "pose", p) for p in random.sample(pool, 3)] if len(pool) >= 3 else []
    cw, ch = 150, 200
    for path, x, y in zip(picks, (676, 851, 1026), (150, 240, 150)):
        try:
            t = Image.open(path).convert("RGB")
        except Exception:
            continue
        # 等比裁切填满卡片
        s = max(cw / t.width, ch / t.height)
        t = t.resize((max(1, round(t.width * s)), max(1, round(t.height * s))), Image.LANCZOS)
        left = (t.width - cw) // 2
        top = (t.height - ch) // 2
        t = t.crop((left, top, left + cw, top + ch))
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=14, fill=255)
        img.paste(t, (x, y), mask)
        d.rounded_rectangle([x, y, x + cw - 1, y + ch - 1], radius=14,
                            outline=(216, 220, 232), width=2)

    fb = ImageFont.truetype(FONT_B, 66)
    fb2 = ImageFont.truetype(FONT_B, 30)
    fr = ImageFont.truetype(FONT_R, 25)
    fr2 = ImageFont.truetype(FONT_R, 21)

    d.text((72, 120), "AI 姿势与衣装", font=fb, fill=TEXT)
    d.text((72, 198), "参考库 · 中文版", font=fb, fill=ACCENT)

    d.text((76, 316), "288 组姿势  ·  1439 张多角度参考图", font=fr, fill=TEXT2)
    d.text((76, 358), "1407 套无人衣装搭配", font=fr, fill=TEXT2)

    # 标签条
    labels = ["4 大体系", "5 种视角", "900×1200", "在线检索"]
    x = 76
    for lb in labels:
        w = d.textlength(lb, font=fr2)
        d.rounded_rectangle([x, 424, x + w + 30, 470], radius=23,
                            fill=(255, 255, 255), outline=(224, 227, 236))
        d.text((x + 15, 435), lb, font=fr2, fill=TEXT2)
        x += w + 42

    d.text((76, 516), "jasonbour.github.io/pose-costume-gallery-zh", font=fr2, fill=ACCENT)

    out = os.path.join(ROOT, "assets")
    os.makedirs(out, exist_ok=True)
    p1 = os.path.join(out, "og-cover.jpg")
    img.save(p1, "JPEG", quality=88, optimize=True)
    img.save(os.path.join(ROOT, "pose", "og-cover.jpg"), "JPEG", quality=88, optimize=True)
    print("生成", p1, os.path.getsize(p1), "字节")


if __name__ == "__main__":
    main()

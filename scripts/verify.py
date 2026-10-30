#!/usr/bin/env python3
"""校验姿势库素材完整性：文件存在、大小合理、图片头可解析。"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSE = os.path.join(ROOT, "pose")


def main():
    data = json.load(open(os.path.join(POSE, "data/pose-zh.json"), encoding="utf-8"))
    miss_t, miss_f, bad = [], [], []
    for r in data:
        t = os.path.join(POSE, r["缩略图"])
        f = os.path.join(POSE, r["原图"])
        if not os.path.exists(t) or os.path.getsize(t) < 1000:
            miss_t.append(r["id"])
        if not os.path.exists(f) or os.path.getsize(f) < 2000:
            miss_f.append(r["id"])
    # 抽样校验图片头
    import random
    for r in random.sample(data, min(40, len(data))):
        for k in ("缩略图", "原图"):
            p = os.path.join(POSE, r[k])
            if not os.path.exists(p):
                continue
            try:
                with Image.open(p) as im:
                    im.verify()
            except Exception as e:
                bad.append((r["id"], k, str(e)))

    print(f"记录数: {len(data)}")
    print(f"缩略图缺失: {len(miss_t)}")
    print(f"原图缺失:   {len(miss_f)}")
    print(f"抽样损坏:   {len(bad)}")
    for name, lst in (("缩略图", miss_t), ("原图", miss_f)):
        if lst:
            print(f"  {name} 示例: {lst[:8]}")
    for b in bad[:5]:
        print("  损坏:", b)
    return 0 if not (miss_t or miss_f or bad) else 1


if __name__ == "__main__":
    sys.exit(main())

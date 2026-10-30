#!/usr/bin/env python3
"""镜像 AI 姿势参考库素材：缩略图直接落盘，原图 PNG 转 WebP 以控制仓库体积。"""
import json, os, io, sys, time, urllib.request, concurrent.futures as cf
from PIL import Image

BASE = "https://ai-pose-gallery.anhao.app/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pose")
UA = {"User-Agent": "Mozilla/5.0 (compatible; gallery-mirror/1.0)"}
WORKERS = int(os.environ.get("WORKERS", "6"))
RETRIES = int(os.environ.get("RETRIES", "6"))


def get(path, retries=RETRIES):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(BASE + path, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))   # 退避：上游对高频请求会直接返 404
    raise last


def do_thumb(rec):
    rel = rec["缩略图"]
    dst = os.path.join(OUT, rel)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    data = get(rel)
    with open(dst, "wb") as f:
        f.write(data)
    return "ok"


def do_full(rec):
    src = "img/%s.png" % rec["id"]           # 上游始终是 PNG，重跑时不会被改坏
    dst = os.path.join(OUT, "img", rec["id"] + ".webp")
    if os.path.exists(dst) and os.path.getsize(dst) > 2000:
        return "skip"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    data = get(src)
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    im.save(dst, "WEBP", quality=85, method=5)
    return "ok"


def main():
    data = json.load(open(os.path.join(ROOT, "pose/data/pose-zh.json"), encoding="utf-8"))
    for rec in data:
        rec["原图"] = rec["原图"].rsplit(".", 1)[0] + ".webp"
    total = len(data)
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = []
    if only in ("all", "thumb"):
        jobs.append(("缩略图", do_thumb))
    if only in ("all", "full"):
        jobs.append(("原图", do_full))
    for name, fn in jobs:
        done = fail = 0
        t0 = time.time()
        with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(fn, r): r for r in data}
            for fu in cf.as_completed(futs):
                try:
                    fu.result()
                    done += 1
                except Exception as e:
                    fail += 1
                    if fail <= 8:
                        print("FAIL", futs[fu]["id"], e, file=sys.stderr)
                if (done + fail) % 100 == 0:
                    print(f"{name}: {done+fail}/{total} (fail {fail}) {time.time()-t0:.0f}s", flush=True)
        print(f"{name} 完成: ok={done} fail={fail}", flush=True)
    json.dump(data, open(os.path.join(ROOT, "pose/data/pose-zh.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()

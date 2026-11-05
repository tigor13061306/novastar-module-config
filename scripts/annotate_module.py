#!/usr/bin/env python3
"""Oznacena slika LED modula: gdje sta pise i kako nastaje ime fajla.

Koraci:
  1) Mreza koordinata, da se odrede pravougaonici:
       python annotate_module.py foto.jpg --grid mreza.png
  2) Oznacena slika iz JSON opisa:
       python annotate_module.py foto.jpg oznake.json izlaz.png

oznake.json (koordinate u pikselima ORIGINALNE fotografije):
{
  "naslov": "Gdje sta pise na modulu",
  "boxes": [
    {"n": 1, "box": [785, 430, 895, 875], "boja": "zuta",  "opis": "Model ploce: Q8H35B5U1-40x20"},
    {"n": 2, "box": [765,1765, 875,2015], "boja": "crvena","opis": "Naljepnica: IC driver + dekoder"}
  ],
  "insets": [
    {"naslov": "2  Naljepnica (uvecano)", "box": [760,1765,880,2015], "rotate": -90, "zoom": 3, "boja": "crvena"}
  ],
  "ime_fajla": {
    "model":   ["Q8H35", "Q8H35B5U1-40x20"],
    "driver":  ["16208", "SM16208SJ"],
    "dekoder": ["5158",  "RUL5158C"],
    "revizija": "A5V1"
  }
}
"revizija" je opciona: bez nje se ispisuje obrazac za pretragu Q8H35*(16208+5158).
"rotate" za inset: -90 = okreni u smjeru kazaljke, 90 = suprotno.
Boje: zuta, crvena, plava, zelena, ljubicasta, siva, narandzasta.

Treba: Python 3.8+ i Pillow (pip install pillow).
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "zuta": (220, 160, 0), "crvena": (215, 45, 45), "plava": (40, 110, 220),
    "zelena": (40, 170, 80), "ljubicasta": (200, 70, 200), "siva": (120, 120, 120),
    "narandzasta": (235, 120, 20),
}
LATIN_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]
MONO_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "C:/Windows/Fonts/consolab.ttf", "/System/Library/Fonts/Menlo.ttc",
]
CJK_FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]


def _font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


class Painter:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    def text(self, xy, s, size, fill, mono=False, anchor=None):
        """Latinica + kineski znakovi u istom redu."""
        lat = _font(MONO_FONTS if mono else LATIN_FONTS, size)
        if anchor:
            self.d.text(xy, s, font=lat, fill=fill, anchor=anchor)
            return
        cjk = _font(CJK_FONTS, size)
        x, y = xy
        run, is_cjk = "", None
        for ch in s + "\0":
            c = "\u3000" <= ch <= "\u9fff" or "\uff00" <= ch <= "\uffef"
            if ch == "\0" or (is_cjk is not None and c != is_cjk):
                if run:
                    f = cjk if is_cjk else lat
                    self.d.text((x, y), run, font=f, fill=fill)
                    x += self.d.textlength(run, font=f)
                run = ch
            else:
                run += ch
            is_cjk = c

    def length(self, s, size, mono=False):
        return self.d.textlength(s, font=_font(MONO_FONTS if mono else LATIN_FONTS, size))

    def arrow(self, x1, y1, x2, y2, c, w=6):
        self.d.line((x1, y1, x2, y2), fill=c, width=w)
        a, L = math.atan2(y2 - y1, x2 - x1), 28
        self.d.polygon([(x2, y2),
                        (x2 - L * math.cos(a - 0.4), y2 - L * math.sin(a - 0.4)),
                        (x2 - L * math.cos(a + 0.4), y2 - L * math.sin(a + 0.4))], fill=c)


def grid(photo, out):
    im = Image.open(photo).convert("RGB")
    p = Painter(im)
    step = 100
    for x in range(0, im.width, step):
        p.d.line((x, 0, x, im.height), fill=(255, 0, 255) if x % 500 == 0 else (255, 255, 0), width=2)
        p.text((x + 4, 4), str(x), 28, (255, 0, 255))
    for y in range(0, im.height, step):
        p.d.line((0, y, im.width, y), fill=(255, 0, 255) if y % 500 == 0 else (255, 255, 0), width=2)
        p.text((4, y + 4), str(y), 28, (255, 0, 255))
    im.save(out)
    print("Velicina fotografije: %dx%d, mreza svakih %d px -> %s" % (im.width, im.height, step, out))


def annotate(photo, spec_path, out):
    spec = json.load(open(spec_path, encoding="utf-8"))
    src = Image.open(photo).convert("RGB")
    im = src.copy()
    p = Painter(im)
    for b in spec.get("boxes", []):
        c = COLORS.get(b.get("boja", "zuta"), COLORS["zuta"])
        x0, y0, x1, y1 = b["box"]
        p.d.rectangle((x0, y0, x1, y1), outline=c, width=8)
        cx, cy = max(x0 - 40, 36), y0 + 40
        p.d.ellipse((cx - 32, cy - 32, cx + 32, cy + 32), fill=c, outline=(0, 0, 0), width=3)
        p.text((cx, cy), str(b["n"]), 40, (0, 0, 0), anchor="mm")

    H = 1800
    ph = im.resize((int(im.width * H / im.height), H))
    insets = []
    for ins in spec.get("insets", []):
        crop = src.crop(tuple(ins["box"]))
        if ins.get("rotate"):
            crop = crop.rotate(ins["rotate"], expand=True)
        z = ins.get("zoom", 2)
        crop = crop.resize((int(crop.width * z), int(crop.height * z)))
        if crop.width > 900:
            crop = crop.resize((900, int(crop.height * 900 / crop.width)))
        insets.append((ins, crop))
    panel_w = max([c.width for _, c in insets] + [860])

    fn = spec.get("ime_fajla")
    bottom = 720 if fn else 0
    W = ph.width + 40 + panel_w + 40
    canvas = Image.new("RGB", (W, H + bottom), (250, 250, 248))
    canvas.paste(ph, (0, 0))
    p = Painter(canvas)
    x0, y = ph.width + 40, 30
    p.text((x0, y), spec.get("naslov", "Gdje šta piše na modulu"), 44, (20, 20, 20))
    y += 90
    for ins, crop in insets:
        c = COLORS.get(ins.get("boja", "crvena"), COLORS["crvena"])
        p.text((x0, y), ins.get("naslov", ""), 30, c)
        y += 50
        canvas.paste(crop, (x0, y))
        p.d.rectangle((x0, y, x0 + crop.width, y + crop.height), outline=c, width=6)
        y += crop.height + 30
    for b in spec.get("boxes", []):
        c = COLORS.get(b.get("boja", "zuta"), COLORS["zuta"])
        p.d.ellipse((x0, y, x0 + 48, y + 48), fill=c)
        p.text((x0 + 24, y + 24), str(b["n"]), 28, (0, 0, 0), anchor="mm")
        p.text((x0 + 64, y + 6), b.get("opis", ""), 28, (20, 20, 20))
        y += 64

    if fn:
        draw_filename(p, canvas.width, H, fn)
    canvas.save(out)
    print("Snimljeno:", out, canvas.size)


def draw_filename(p, W, top, fn):
    Y, R, B, G = COLORS["zuta"], COLORS["crvena"], COLORS["plava"], COLORS["siva"]
    y0 = top + 10
    p.d.line((40, y0, W - 40, y0), fill=(200, 200, 200), width=3)
    rev = fn.get("revizija")
    model, drv, dec = fn["model"], fn["driver"], fn["dekoder"]
    name = "%s%s(%s+%s)" % (model[0], rev or "*", drv[0], dec[0])
    p.text((60, y0 + 25), ("Kako nastaje ime fajla  " if rev else "Traži fajl  ") + name, 44, (20, 20, 20))

    def seg_line(x, y, parts, size, gap):
        pos = []
        for t, c in parts:
            w = p.length(t, size, mono=True)
            if c:
                x += gap
                light = tuple(int(v * 0.18 + 250 * 0.82) for v in c)
                p.d.rounded_rectangle((x - 4, y - 4, x + w + 4, y + size + 10), radius=8, fill=light, outline=c, width=4)
            p.text((x, y), t, size, c if c else (60, 60, 60), mono=True)
            pos.append((x, x + w))
            x += w + (gap if c else 0)
        return pos

    def split(full, part):
        i = full.find(part)
        if i < 0:
            return [(full, None)]
        return [(full[:i], None), (part, "X"), (full[i + len(part):], None)]

    sy = y0 + 120
    boxes = [(50, "PCB natpis (model)", model, Y), (660, "naljepnica: driver", drv, R),
             (1270, "naljepnica: dekoder", dec, B)]
    src_mid = []
    for bx, label, (part, full), c in boxes:
        p.d.rounded_rectangle((bx, sy, bx + 590, sy + 130), radius=12, fill=(255, 255, 255), outline=(190, 190, 190), width=3)
        p.text((bx + 20, sy + 14), label, 26, (90, 90, 90))
        parts = [(t, c if k == "X" else None) for t, k in split(full, part) if t]
        pos = seg_line(bx + 20, sy + 60, parts, 40, 10)
        hi = [ps for ps, (t, k) in zip(pos, parts) if k]
        src_mid.append((hi[0][0] + hi[0][1]) / 2 if hi else bx + 295)

    fy = y0 + 430
    parts = [(model[0], Y), (rev or "*", G), ("(", None), (drv[0], R), ("+", None), (dec[0], B), (").rcfgx", None)]
    fw = sum(p.length(t, 64, mono=True) + (24 if c else 0) for t, c in parts)
    pf = seg_line((W - fw) / 2, fy, parts, 64, 12)
    mid = lambda ps: (ps[0] + ps[1]) / 2
    for i, j, c in [(0, 0, Y), (1, 3, R), (2, 5, B)]:
        p.arrow(src_mid[i], sy + 138, mid(pf[j]), fy - 14, c)
    ly = fy + 95
    for j, t, c in [(0, "model", Y), (1, "revizija" if rev else "bilo šta", G), (3, "driver", R), (5, "dekoder", B)]:
        p.text((mid(pf[j]), ly), t, 28, c, anchor="ma")
    note = ("%s nije sa modula: revizija iz baze. " % rev) if rev else "* = bilo koja revizija ploče. "
    p.text((W / 2, ly + 70), note + "Iste cifre čipova + isti početak modela = pravi fajl.", 26, (60, 60, 60), anchor="ma")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 3 and a[1] == "--grid":
        grid(a[0], a[2])
    elif len(a) == 3:
        annotate(a[0], a[1], a[2])
    else:
        print(__doc__)
        sys.exit(1)

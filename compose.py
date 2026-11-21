#!/usr/bin/env python3
"""Compose the entry image for make.fun news-image-20261120.

Draws a 1024x1024 newspaper front page summing up Friday 20 November
2026, using only Pillow vector drawing (no photographs, no network).
Every story below was checked against same-day reporting (ICJ, Reuters,
AP, BBC, OneTurn) on 21 November 2026. Output is deterministic: fixed
layout, fixed text, no timestamps, no randomness.

Run:  python3 compose.py            # writes entry.png next to this file
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (20, 33, 61)
RED = (185, 28, 28)
NAVY = (20, 33, 61)
NAVY_LIGHT = (223, 232, 240)
GREY = (84, 84, 84)
RULE = (20, 33, 61)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, text, size=19):
    f = font(SANS_B, size)
    draw.text((x, y), text, font=f, fill=RED)
    return y + size + 6


def headline(draw, x, y, text, size, max_w, leading=None):
    f = font(SERIF_B, size)
    lines = wrap(draw, text, f, max_w)
    return draw_lines(draw, lines, x, y, f, INK, leading or int(size * 1.08))


def deck(draw, x, y, text, size, max_w, leading=None):
    f = font(SANS, size)
    lines = wrap(draw, text, f, max_w)
    return draw_lines(draw, lines, x, y, f, (38, 38, 38), leading or int(size * 1.32))


# ---- pictograms (simple vector icons, drawn with PIL primitives) ----

def icon_scales(d, x0, y0, s):
    """Scales of justice, s = height in px."""
    c = INK
    cx = x0 + s // 2
    d.line([(cx, y0 + 8), (cx, y0 + s - 14)], fill=c, width=5)
    d.line([(x0 + 6, y0 + 26), (x0 + s - 6, y0 + 26)], fill=c, width=5)
    d.ellipse([cx - 7, y0, cx + 7, y0 + 14], fill=c)
    for sx in (x0 + 6, x0 + s - 6):
        d.line([(sx, y0 + 26), (sx - 22, y0 + 58)], fill=c, width=3)
        d.line([(sx, y0 + 26), (sx + 22, y0 + 58)], fill=c, width=3)
        d.arc([sx - 26, y0 + 48, sx + 26, y0 + 84], 0, 180, fill=c, width=4)
        d.line([(sx - 26, y0 + 66), (sx + 26, y0 + 66)], fill=c, width=4)
    d.line([(cx - 30, y0 + s - 12), (cx + 30, y0 + s - 12)], fill=c, width=5)
    d.line([(cx - 22, y0 + s - 4), (cx + 22, y0 + s - 4)], fill=c, width=5)


def icon_missile(d, x0, y0, s):
    c = RED
    d.line([(x0 + 8, y0 + s - 14), (x0 + s - 8, y0 + 12)], fill=c, width=8)
    d.polygon([(x0 + s - 8, y0 + 12), (x0 + s - 28, y0 + 10),
               (x0 + s - 10, y0 + 32)], fill=c)
    d.polygon([(x0 + 8, y0 + s - 14), (x0 + 28, y0 + s - 16),
               (x0 + 10, y0 + s - 34)], fill=c)
    d.ellipse([x0 + s - 46, y0 + s - 46, x0 + s - 6, y0 + s - 6],
              outline=INK, width=3)
    d.ellipse([x0 + s - 34, y0 + s - 34, x0 + s - 18, y0 + s - 18], fill=INK)


def icon_bridge(d, x0, y0, s):
    c = INK
    w = s + 24
    d.line([(x0, y0 + s - 16), (x0 + w, y0 + s - 16)], fill=c, width=5)
    for tx in (x0 + 12, x0 + w // 2 - 3, x0 + w - 18):
        d.line([(tx, y0 + 10), (tx, y0 + s - 16)], fill=c, width=5)
    d.arc([x0 + 4, y0 + 26, x0 + w // 2 + 6, y0 + s + 4], 180, 360, fill=c, width=4)
    d.arc([x0 + w // 2 - 6, y0 + 26, x0 + w - 4, y0 + s + 4], 180, 360, fill=c, width=4)


def icon_chart(d, x0, y0, s, light=False):
    c = (255, 255, 255) if light else INK
    r = RED
    d.line([(x0, y0 + s - 8), (x0 + s + 20, y0 + s - 8)], fill=c, width=3)
    d.line([(x0, y0), (x0, y0 + s - 8)], fill=c, width=3)
    pts = [(x0 + 6, y0 + 10), (x0 + 30, y0 + 22), (x0 + 54, y0 + 18),
           (x0 + 78, y0 + 44), (x0 + 102, y0 + 58), (x0 + 126, y0 + s - 16)]
    d.line(pts, fill=r, width=6, joint="curve")
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 14, pts[-1][1] - 2),
               (pts[-1][0] - 2, pts[-1][1] - 14)], fill=r)


def icon_bell(d, x0, y0, s):
    c = INK
    d.arc([x0 + 8, y0 + 6, x0 + s - 8, y0 + s - 6], 180, 360, fill=c, width=5)
    d.line([(x0 + 8, y0 + s - 26), (x0 + s - 8, y0 + s - 26)], fill=c, width=5)
    d.line([(x0 + 2, y0 + s - 22), (x0 + s - 2, y0 + s - 22)], fill=c, width=4)
    d.ellipse([x0 + s // 2 - 6, y0 + s - 12, x0 + s // 2 + 6, y0 + s], fill=c)
    d.line([(x0 + s // 2, y0 - 2), (x0 + s // 2, y0 + 10)], fill=c, width=4)


def icon_flags(d, x0, y0, s):
    # Two small flags: UK (cross) and EU (circle of stars).
    d.rectangle([x0, y0, x0 + 52, y0 + 34], fill=(1, 33, 105), outline=INK, width=2)
    d.line([(x0, y0), (x0 + 52, y0 + 34)], fill=(255, 255, 255), width=4)
    d.line([(x0 + 52, y0), (x0, y0 + 34)], fill=(255, 255, 255), width=4)
    d.line([(x0 + 26, y0), (x0 + 26, y0 + 34)], fill=(200, 16, 46), width=5)
    d.line([(x0, y0 + 17), (x0 + 52, y0 + 17)], fill=(200, 16, 46), width=5)
    d.rectangle([x0 + 62, y0, x0 + 114, y0 + 34], fill=(0, 51, 153), outline=INK, width=2)
    cx, cy = x0 + 88, y0 + 17
    for k in range(8):
        a = math.pi * 2 * k / 8 - math.pi / 2
        sx, sy = cx + 11 * math.cos(a), cy + 11 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 209, 0))


def icon_tower(d, x0, y0, s):
    c = INK
    d.rectangle([x0 + 18, y0 + 26, x0 + 52, y0 + s], fill=c)
    d.polygon([(x0 + 18, y0 + 26), (x0 + 52, y0 + 26), (x0 + 35, y0 + 4)], fill=c)
    for yy in range(y0 + 38, y0 + s - 8, 14):
        for xx in (x0 + 24, x0 + 38):
            d.rectangle([xx, yy, xx + 7, yy + 7], fill=(255, 209, 0))
    for dx, dy in ((26, -14), (30, 0), (26, 14), (12, -18)):
        d.line([(x0 + 62, y0 + 22), (x0 + 62 + dx, y0 + 22 + dy)], fill=RED, width=3)
    d.ellipse([x0 + 54, y0 + 14, x0 + 70, y0 + 30], fill=RED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)

    # ---------- masthead ----------
    f_title = font(SERIF_B, 86)
    d.text((W // 2, 26), "THE WORLD TODAY", font=f_title, fill=INK, anchor="ma")
    d.line([(24, 124), (W - 24, 124)], fill=RULE, width=3)
    f_date = font(SANS_B, 24)
    d.text((24, 134), "FRIDAY 20 NOVEMBER 2026", font=f_date, fill=INK)
    f_side = font(SANS, 20)
    d.text((W - 24, 136), "ONE DAY  •  ONE PAGE", font=f_side, fill=GREY, anchor="ra")

    # ---------- lead story: ICJ Myanmar (168-400) ----------
    d.rectangle([24, 168, 1000, 400], fill=NAVY_LIGHT, outline=INK, width=2)
    y = kicker(d, 44, 182, "THE HAGUE  •  JUSTICE  •  LEAD STORY")
    y = headline(d, 44, y, "WORLD COURT: MYANMAR COMMITTED GENOCIDE", 46, 740)
    y += 8
    deck(d, 44, y,
         "The UN's top court rules Myanmar's forces committed "
         "state-sponsored genocide against the Rohingya.",
         21, 740)
    icon_scales(d, 824, 214, 150)

    # ---------- row 2: Poland / Kyiv (412-640) ----------
    d.rectangle([24, 412, 500, 640], outline=INK, width=2)
    y = kicker(d, 40, 424, "POLAND  •  EUROPE")
    y = headline(d, 40, y, "MISSILES LAND IN POLAND", 30, 440)
    y += 4
    deck(d, 40, y,
         "Two Russian missiles and a drone come down in Poland; NATO "
         "calls it a grave violation of allied airspace.",
         19, 340)
    icon_missile(d, 408, 552, 64)

    d.rectangle([524, 412, 1000, 640], outline=INK, width=2)
    y = kicker(d, 540, 424, "KYIV  •  UKRAINE")
    y = headline(d, 540, y, "THREE KYIV BRIDGES HIT", 30, 440)
    y += 4
    deck(d, 540, y,
         "Russian strikes hit three bridges overnight; three people "
         "killed, about 15 hurt — retaliation after Ukraine struck "
         "the Crimea Bridge again.",
         19, 340)
    icon_bridge(d, 896, 552, 64)

    # ---------- markets band (652-736) ----------
    d.rectangle([24, 652, 1000, 736], fill=NAVY, outline=INK, width=2)
    f_mb = font(SERIF_B, 34)
    d.text((44, 664), "MARKETS PLUNGE", font=f_mb, fill=(255, 255, 255))
    f_md = font(SANS, 22)
    d.text((44, 706),
           "S&P 500 –3.7% into correction  •  Nikkei –5.1% as the AI sell-off spreads",
           font=f_md, fill=(220, 225, 235))
    icon_chart(d, 820, 662, 60, light=True)

    # ---------- row 3: three stories (748-916) ----------
    cols = [
        (24, 328, "RECORD IPO", "Anthropic debuts on Nasdaq",
         "Closes 17% above its $83 price; $81.3bn raised, a record IPO.",
         icon_bell),
        (356, 660, "UK–EU RESET", "UK–EU sign reset deal",
         "Food, carbon and youth-mobility deals agreed in Brussels.",
         icon_flags),
        (688, 1000, "RIYADH TOWER HIT", "Missile hits Riyadh tower",
         "Houthi strike blows out windows on seven floors; no injuries.",
         icon_tower),
    ]
    for x0, x1, kick, head, body, icon in cols:
        d.rectangle([x0, 748, x1, 916], outline=INK, width=2)
        icon(d, x0 + 16, 758, 30)
        y = kicker(d, x0 + 16, 794, kick, size=16)
        y = headline(d, x0 + 16, y, head, 22, x1 - x0 - 32, leading=24)
        deck(d, x0 + 16, y + 2, body, 16, x1 - x0 - 32, leading=20)

    # ---------- ticker + footer ----------
    d.line([(24, 928), (1000, 928)], fill=RULE, width=2)
    f_tk = font(SANS_B, 16)
    d.text((24, 936), "ALSO ON 20 NOVEMBER:", font=f_tk, fill=RED)
    f_tb = font(SANS, 16)
    d.text((24, 958),
           "M6.7 quake hits central Peru  •  BepiColombo reaches Mercury after 8 years",
           font=f_tb, fill=(38, 38, 38))
    d.text((24, 980),
           "Trump, Xi, Putin joint declaration in Shenzhen  •  Lauren Price undisputed champion",
           font=f_tb, fill=(38, 38, 38))
    f_ft = font(SANS, 11)
    d.text((W // 2, 998), "US Senate blocks Iran war-powers vote 51–48  •  US measles cases near 6,000  •  Sources: ICJ, Reuters, AP, BBC",
           font=f_ft, fill=GREY, anchor="ma")
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    img = build()
    out = os.path.join(here, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()

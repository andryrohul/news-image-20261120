#!/usr/bin/env python3
"""Build entry.png for news-image-20261120, V6.

Newspaper front page: masthead, THE DAY IN UTC timeline, THE DAY IN
NUMBERS strip, region bar, 3 lead stories with big drawn pictures, 10
numbered stories with small drawn pictures, world map with pins 1-13,
27 more one-liners, DATE CHECK strip, footer. 40 stories, all verified
as Friday 20 November 2026. Stdlib + Pillow only; deterministic.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/home/hatch/workspace/makefun/news-image-20261120/entry.png"
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

PAPER = (247, 242, 230)
INK = (20, 20, 20)
RED = (192, 0, 0)
GREY = (100, 100, 100)
SEA = (210, 225, 235)
LAND = (232, 222, 190)
YELLOW = (255, 210, 0)
GREEN = (46, 125, 50)

WARNED = []


def SERIF_B(s):
    return ImageFont.truetype(FONT_DIR + "DejaVuSerif-Bold.ttf", s)


def SERIF(s):
    return ImageFont.truetype(FONT_DIR + "DejaVuSerif.ttf", s)


def SANS(s):
    return ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", s)


def SANS_B(s):
    return ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", s)


def wrap(text, font, width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(drw, text, font, x, y, width, max_lines, fill=INK, lh=None):
    lh = lh or int(font.size * 1.25)
    lines = wrap(text, font, width)
    if len(lines) > max_lines:
        WARNED.append("overflow: %r (%d lines > %d)" %
                      (text[:40], len(lines), max_lines))
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        drw.text((x, y + i * lh), line, font=font, fill=fill)
    return y + len(lines) * lh


def draw_centred(drw, text, font, cx, y, fill):
    drw.text((cx - font.getlength(text) / 2, y), text, font=font, fill=fill)


def rule(drw, x0, x1, y, width=1, fill=INK):
    drw.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag(drw, x, y, text, bg, fg, font=None, border=None):
    fnt = font or SANS_B(8)
    w = fnt.getlength(text) + 8
    drw.rectangle([x, y, x + w, y + 13], fill=bg,
                  outline=border or bg, width=1)
    drw.text((x + 4, y + 2), text, font=fnt, fill=fg)
    return w


REGIONS = [("Europe", (31, 78, 121)), ("Asia", (192, 0, 0)),
           ("Middle East", (139, 69, 19)), ("Africa", (46, 125, 50)),
           ("Americas", (106, 27, 154)), ("Oceania", (0, 131, 143)),
           ("Global", (97, 97, 97))]

TIMELINE = [("00:00", "Kyiv bridges hit"),
            ("02:00", "Akvan landfall"),
            ("05:30", "Taipei -6.2%"),
            ("06:00", "Tokyo -5.1%"),
            ("08:00", "Hong Kong -1.9%"),
            ("10:30", "Estonia border"),
            ("21:00", "S&P 500 -3.7%")]

STATS = [("111", "missiles fired at Ukraine"),
         ("372,000", "evacuated before Akvan"),
         ("-3.7%", "S&P 500, Friday's close"),
         ("100,000", "youth visas a year"),
         ("2.2%", "Japan core inflation"),
         ("118", "runs by Glenn Phillips")]

LEADS = [
    (1, "KYIV, UKRAINE", "WAR", "Europe", "111 MISSILES + 404 DRONES",
     "Russian missiles hit three Kyiv bridges",
     "About 110 missiles and 400 drones killed six people in Kyiv and "
     "cut power and water. Two more died in Lviv.",
     "Kyiv Independent, BBC"),
    (2, "ODISHA, INDIA", "CYCLONE", "Asia", "372,000 EVACUATED",
     "Cyclone Akvan comes ashore in eastern India",
     "The storm crossed the coast near Gopalpur from about 7:30 am. "
     "More than 372,000 people were moved to shelters. No deaths "
     "reported.", "IMD, Deccan Herald"),
    (3, "TAIPEI · SEOUL · TOKYO", "MARKETS", "Asia",
     "NASDAQ'S WORST WEEK SINCE 2020",
     "AI sell-off sinks Asia's stock markets",
     "Taiwan's index fell 6.2% to end its worst week since 1991. "
     "Seoul lost 5.2% and Tokyo 5.1%. The S&P 500 fell 3.7% in "
     "New York.", "Al Jazeera, Reuters"),
]

NUMBERED = [
    (4, "BRUSSELS", "DIPLOMACY", "Europe", "UK-EU DEAL",
     "UK and EU seal a 'reset' deal",
     "Food trade, youth visas, carbon link.", "Reuters"),
    (5, "ANTALYA", "CLIMATE", "Global", "COP31: NO DEAL",
     "COP31 reaches its last day with no deal",
     "The draft text leaves out fossil fuels.", "UN News"),
    (6, "EASTERN POLAND", "SECURITY", "Europe", "POLAND: MISSILE",
     "Russian cruise missile lands in Poland",
     "It fell in a field; two airports paused.", "Reuters"),
    (7, "CENTRAL IRAQ", "SECURITY", "Middle East", "IRAQ: ARMY IN",
     "Iraqi army enters a militia stronghold",
     "Troops deploy to Jurf al-Sakhar.", "Reuters"),
    (8, "ITALY", "LABOUR", "Europe", "ITALY: STRIKE",
     "General strike over Italy's budget",
     "Workers and students march.", "Reuters"),
    (9, "TOKYO", "ECONOMY", "Asia", "JAPAN: +2.2%",
     "Japan's core inflation picks up to 2.2%",
     "A December rate rise stays in view.", "Reuters"),
    (10, "SEOUL", "POLITICS", "Asia", "SEOUL: IMPEACH",
     "Korea's ruling party to impeach top judge",
     "Party adopts it as official policy.", "Korea JoongAng Daily"),
    (11, "TURKANA, KENYA", "ENERGY", "Africa", "KENYA: OIL",
     "Kenya starts drilling its first oil well",
     "First crude is due on 1 December.", "People Daily"),
    (12, "SAN SALVADOR", "POLITICS", "Americas", "BUKELE: 3RD BID",
     "Bukele files to run for a third term",
     "The vote is on 28 February 2027.", "AP"),
    (13, "WELLINGTON", "CRICKET", "Oceania", "PHILLIPS: 118",
     "Phillips hits 118 against India",
     "Hundreds in India in all three formats.", "ICC"),
]

ALSO = [
    (14, "Anthropic ends first day up 17%", "Reuters"),
    (15, "Shenzhen: leaders publish peace declaration", "AP"),
    (16, "Senate rejects Iran war-powers 51-48", "AP"),
    (17, "State probes Nvidia over China chips", "Reuters"),
    (18, "Europe agrees binding Ukraine guarantees", "Reuters"),
    (19, "Tonga declares drought emergency", "RNZ"),
    (20, "Somalia orders UAE envoy out in 3 days", "Reuters"),
    (21, "GTA VI makes $2.36bn on day one", "Sensor Tower"),
    (22, "Trump pardons Pete Rose", "AP"),
    (23, "Dow falls below 50,000 as AI rout deepens", "Reuters"),
    (24, "IEA: Iran conflict a historic energy threat", "IEA"),
    (25, "US blockade of Iranian shipping persists", "Reuters"),
    (26, "Hungary lifts its Ukraine EU veto", "Reuters"),
    (27, "US, China: humans to oversee military AI", "Reuters"),
    (28, "Chinese chemicals fuel Sinaloa cartel, US says", "AP"),
    (29, "Saudi coalition downs 5 Houthi missiles", "Reuters"),
    (30, "Venezuela TPS ruling takes effect Friday", "AP"),
    (31, "Anthropic's $81bn offering closes Friday", "Reuters"),
    (32, "US charges Russian over Palantir spying", "Reuters"),
    (33, "NZ court: pay-equity reform broke rights", "RNZ"),
    (34, "Car-trafficking swoop: 2,393 seized", "Interpol"),
    (35, "Zelensky: NATO is the strongest guarantee", "AP"),
    (36, "Russian strike on Lviv rail station kills 2", "The Times"),
    (37, "Estonia to shut Russia road border on 1 Dec", "Reuters"),
    (38, "Israeli strikes kill 6 in Gaza despite truce", "AFP"),
    (39, "Coalition strikes Houthi-held Hodeidah port", "Reuters"),
    (40, "AfDB says 22 African states near debt distress", "AfDB"),
]

DATE_CHECK = (
    "Left out as Thursday 19 November's news: the World Court's Myanmar "
    "ruling, the Denmark-Greenland vote, the Gaza tank raid, the Genoa "
    "drone shutdown, Malawi's protests (17 Nov) and the Hormuz "
    "'14 attacks' count. Not yet happened: BepiColombo's Mercury orbit "
    "entry and any final COP31 text."
)

FOOTER_L = ("Every story here happened, or was first reported, on Friday "
            "20 November 2026. Officials' counts are attributed.")
FOOTER_R = "Sources named beside each story · original drawings"


# ---------------------------------------------------------------- pictures
def _star(drw, cx, cy, r, fill):
    drw.polygon([(cx, cy - r), (cx + r * 0.28, cy - r * 0.28),
                 (cx + r, cy), (cx + r * 0.28, cy + r * 0.28),
                 (cx, cy + r), (cx - r * 0.28, cy + r * 0.28),
                 (cx - r, cy), (cx - r * 0.28, cy - r * 0.28)],
                fill=fill)


def _dash(drw, x0, y0, x1, y1, fill, step=8):
    n = max(1, int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 / step))
    for i in range(0, n, 2):
        t0, t1 = i / n, min(1.0, (i + 1) / n)
        drw.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                  (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                 fill=fill, width=2)


def _label(drw, x, y, text, bg=RED, fg=(255, 255, 255)):
    fnt = SANS_B(10)
    w = fnt.getlength(text) + 10
    drw.rectangle([x, y, x + w, y + 16], fill=bg)
    drw.text((x + 5, y + 3), text, font=fnt, fill=fg)
    return w


def _vtag(drw, x, y, w, text, kind):
    fnt = SANS_B(8)
    tw = fnt.getlength(text) + 8
    tx = x + w - tw
    if kind == "CONFIRMED":
        drw.rectangle([tx, y, tx + tw, y + 13], fill=GREEN)
        drw.text((tx + 4, y + 2), text, font=fnt, fill=(255, 255, 255))
    elif kind == "OFFICIAL":
        drw.rectangle([tx, y, tx + tw, y + 13], fill=(255, 255, 255),
                      outline=RED, width=1)
        drw.text((tx + 4, y + 2), text, font=fnt, fill=RED)
    else:
        drw.rectangle([tx, y, tx + tw, y + 13], fill=GREY)
        drw.text((tx + 4, y + 2), text, font=fnt, fill=(255, 255, 255))


def pic_kyiv(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    for bx in (x + 18, x + 78, x + 138, x + 198, x + 258):
        drw.rectangle([bx, y + 58, bx + 42, y + 104], fill=(30, 40, 70))
        for wy in (y + 66, y + 78, y + 90):
            for wx in (bx + 6, bx + 18, bx + 30):
                drw.rectangle([wx, wy, wx + 5, wy + 5], fill=YELLOW)
    drw.rectangle([x, y + 104, x + w, y + h], fill=(40, 70, 120))
    for cx in (x + 60, x + 160, x + 260):
        drw.arc([cx - 52, y + 78, cx + 52, y + 130], 180, 360,
                fill=(255, 255, 255), width=3)
        drw.line([(cx - 52, y + 104), (cx + 52, y + 104)],
                 fill=(255, 255, 255), width=2)
    for sx, sy, ex, ey in ((x + 40, y + 12, x + 90, y + 52),
                           (x + 150, y + 8, x + 200, y + 48),
                           (x + 240, y + 14, x + 285, y + 50)):
        _dash(drw, sx, sy, ex, ey, (255, 180, 60))
        _star(drw, ex, ey, 7, (255, 200, 80))
    _label(drw, x, y + h - 20, "111 MISSILES + 404 DRONES", bg=YELLOW,
           fg=INK)
    _vtag(drw, x, y, w, "OFFICIAL · KYIV", "OFFICIAL")


def pic_akvan(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(52, 110, 180))
    land = [(x, y), (x + 118, y), (x + 138, y + 30), (x + 122, y + 58),
            (x + 140, y + 88), (x + 112, y + h), (x, y + h)]
    drw.polygon(land, fill=(232, 222, 190), outline=(180, 165, 120))
    drw.text((x + 8, y + 6), "ODISHA", font=SANS_B(10), fill=INK)
    drw.text((x + 8, y + 20), "INDIA", font=SANS(9), fill=INK)
    drw.text((x + 8, y + h - 14), "BAY OF BENGAL", font=SANS(9),
             fill=(255, 255, 255))
    cx, cy = x + 205, y + 66
    for r in (52, 40, 28, 16):
        drw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                fill=(255, 255, 255), width=3)
    drw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))
    drw.ellipse([x + 128, y + 44, x + 136, y + 52], fill=RED,
                outline=(255, 255, 255), width=1)
    _label(drw, x + w - 148, y + 4, "LANDFALL 02:00-03:00 UTC",
           bg=(0, 0, 0))
    _label(drw, x, y + h - 20, "372,000 EVACUATED", bg=RED)


def pic_markets(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(12, 14, 26))
    _label(drw, x, y, "NASDAQ'S WORST WEEK SINCE 2020", bg=RED)
    pts = [(x + 12, y + 34), (x + 42, y + 40), (x + 72, y + 32),
           (x + 102, y + 52), (x + 132, y + 66), (x + 162, y + 92),
           (x + 190, y + 108)]
    for i in range(len(pts) - 1):
        drw.line([pts[i], pts[i + 1]], fill=(255, 60, 60), width=3)
    for px, py in pts:
        drw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 80, 80))
    rows = [("Taipei", "-6.2%"), ("Seoul", "-5.2%"), ("Tokyo", "-5.1%"),
            ("Hong Kong", "-1.9%"), ("S&P 500", "-3.7%")]
    for i, (name, val) in enumerate(rows):
        ry = y + 24 + i * 20
        drw.text((x + 205, ry), name, font=SANS(11),
                 fill=(255, 255, 255))
        vf = SANS_B(11)
        drw.text((x + w - 6 - vf.getlength(val), ry), val, font=vf,
                 fill=(255, 80, 80))
    drw.text((x + 8, y + h - 16), "Closing prices", font=SANS_B(10),
             fill=(255, 255, 255))


def pic_ukeu(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(245, 245, 245))
    drw.rectangle([x, y, x + 88, y + h], fill=(1, 33, 105))
    for cx in (x + 14, x + 44, x + 74):
        drw.line([(cx, y), (cx, y + h)], fill=(255, 255, 255), width=12)
    drw.line([(x, y + 22), (x + 88, y + 22)], fill=(255, 255, 255),
             width=12)
    drw.rectangle([x + 96, y, x + w, y + h], fill=(0, 51, 153))
    for i in range(12):
        import math
        a = math.pi * 2 * i / 12
        sx = x + 144 + 26 * math.cos(a)
        sy = y + 27 + 26 * math.sin(a)
        _star(drw, sx, sy, 4, YELLOW)
    _label(drw, x, y, "UK-EU DEAL")
    _vtag(drw, x, y, w, "OFFICIAL", "OFFICIAL")


def pic_cop31(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(200, 235, 245))
    drw.ellipse([x + 12, y + 6, x + 52, y + 46], fill=(70, 140, 200))
    drw.ellipse([x + 20, y + 14, x + 36, y + 26], fill=(90, 180, 90))
    drw.ellipse([x + 34, y + 30, x + 46, y + 40], fill=(90, 180, 90))
    drw.rectangle([x + 78, y + 10, x + 86, y + 34], fill=(220, 220, 220),
                  outline=INK, width=1)
    drw.ellipse([x + 73, y + 32, x + 91, y + 48], fill=RED)
    drw.text((x + 98, y + 8), "38°", font=SANS_B(16), fill=RED)
    drw.text((x + 98, y + 30), "ANTALYA", font=SANS_B(9), fill=INK)
    _label(drw, x, y, "COP31: NO DEAL")
    _vtag(drw, x, y, w, "CONFIRMED", "CONFIRMED")


def pic_poland(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(190, 220, 245))
    drw.rectangle([x, y + 30, x + w, y + h], fill=(150, 200, 110))
    drw.rectangle([x, y + 42, x + w, y + h], fill=(120, 180, 90))
    _dash(drw, x + 20, y + 10, x + 120, y + 30, (120, 120, 120))
    drw.polygon([(x + 118, y + 24), (x + 134, y + 30), (x + 118, y + 36)],
                fill=(90, 90, 90))
    _star(drw, x + 150, y + 34, 10, (255, 200, 60))
    drw.polygon([(x + 30, y + 54), (x + 44, y + 28), (x + 58, y + 54)],
                fill=(60, 120, 60))
    drw.polygon([(x + 60, y + 54), (x + 74, y + 28), (x + 88, y + 54)],
                fill=(60, 120, 60))
    _label(drw, x, y, "POLAND: MISSILE")
    _vtag(drw, x, y, w, "OFFICIAL", "OFFICIAL")


def pic_iraq(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(245, 230, 190))
    drw.ellipse([x + 150, y + 6, x + 182, y + 38], fill=(255, 200, 90))
    drw.rectangle([x + 16, y + 26, x + 96, y + 40], fill=(90, 100, 70))
    drw.rectangle([x + 30, y + 40, x + 82, y + 46], fill=(70, 80, 55))
    drw.rectangle([x + 44, y + 12, x + 60, y + 26], fill=(70, 80, 55))
    for wx in (x + 22, x + 34, x + 46, x + 58, x + 70, x + 82):
        drw.ellipse([wx, y + 46, wx + 9, y + 54], fill=(40, 40, 40))
    drw.line([(x + 128, y + 50), (x + 128, y + 14)], fill=(120, 90, 40),
             width=3)
    for a, ln in ((-50, 16), (-20, 20), (10, 18), (40, 15)):
        import math
        r = math.radians(a)
        drw.line([(x + 128, y + 16),
                  (x + 128 + ln * math.sin(r), y + 16 - ln * math.cos(r))],
                 fill=(60, 140, 60), width=3)
    _label(drw, x, y, "IRAQ: ARMY IN")
    _vtag(drw, x, y, w, "OFFICIAL", "OFFICIAL")


def pic_italy(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
    for i, col in enumerate([(0, 140, 70), (255, 255, 255), (200, 0, 0)]):
        drw.rectangle([x + i * 64, y, x + (i + 1) * 64, y + 10], fill=col)
    for i, col in enumerate([(200, 60, 60), (60, 120, 200), (220, 180, 60),
                             (60, 160, 90), (150, 90, 180)]):
        cx = x + 22 + i * 38
        drw.ellipse([cx - 11, y + 20, cx + 11, y + 42], fill=col)
        drw.polygon([(cx - 13, y + 54), (cx + 13, y + 54),
                     (cx + 8, y + 42), (cx - 8, y + 42)], fill=col)
    _label(drw, x, y, "ITALY: STRIKE")
    _vtag(drw, x, y, w, "CONFIRMED", "CONFIRMED")


def pic_japan(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(250, 250, 250))
    drw.ellipse([x + 10, y + 6, x + 42, y + 38], fill=RED)
    for i, bh in enumerate((14, 20, 26, 32)):
        drw.rectangle([x + 58 + i * 26, y + 48 - bh,
                       x + 76 + i * 26, y + 48], fill=(140, 140, 140))
    drw.line([(x + 56, y + 12), (x + 172, y + 2)], fill=RED, width=3)
    drw.polygon([(x + 172, y + 2), (x + 160, y + 0), (x + 162, y + 10)],
                fill=RED)
    _label(drw, x, y, "JAPAN: +2.2%")
    _vtag(drw, x, y, w, "CONFIRMED", "CONFIRMED")


def pic_seoul(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(235, 235, 240))
    drw.polygon([(x + 16, y + 12), (x + 82, y + 12), (x + 49, y + 2)],
                fill=(90, 90, 110))
    for cx in (x + 26, x + 49, x + 72):
        drw.rectangle([cx - 3, y + 12, cx + 3, y + 44],
                      fill=(200, 200, 210))
    drw.rectangle([x + 14, y + 44, x + 84, y + 50], fill=(120, 120, 140))
    drw.line([(x + 120, y + 20), (x + 160, y + 34)], fill=(120, 80, 40),
             width=5)
    drw.rectangle([x + 150, y + 34, x + 176, y + 42], fill=(120, 80, 40))
    _label(drw, x, y, "SEOUL: IMPEACH")
    _vtag(drw, x, y, w, "REPORTED", "REPORTED")


def pic_kenya(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(255, 190, 90))
    drw.ellipse([x + 152, y + 4, x + 184, y + 36], fill=(255, 220, 120))
    drw.line([(x + 40, y + 54), (x + 58, y + 10)], fill=(60, 60, 60),
             width=4)
    drw.line([(x + 76, y + 54), (x + 58, y + 10)], fill=(60, 60, 60),
             width=4)
    for yy in (y + 20, y + 30, y + 40):
        drw.line([(x + 46, yy), (x + 70, yy)], fill=(60, 60, 60), width=3)
    drw.rectangle([x + 100, y + 40, x + 140, y + 54], fill=(90, 90, 90))
    _label(drw, x, y, "KENYA: OIL")
    _vtag(drw, x, y, w, "OFFICIAL", "OFFICIAL")


def pic_bukele(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(0, 60, 140))
    drw.text((x + 10, y + 22), "VOTE", font=SANS_B(18),
             fill=(255, 255, 255))
    drw.rectangle([x + 84, y + 22, x + 132, y + 50], fill=(255, 255, 255))
    drw.rectangle([x + 88, y + 26, x + 128, y + 34], fill=(220, 220, 220))
    drw.line([(x + 138, y + 30), (x + 148, y + 42), (x + 168, y + 14)],
             fill=(255, 255, 255), width=5)
    _label(drw, x, y, "BUKELE: 3RD BID")
    _vtag(drw, x, y, w, "REPORTED", "REPORTED")


def pic_phillips(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(40, 140, 60))
    drw.rectangle([x + 60, y + 8, x + 132, y + 46], fill=(220, 190, 130))
    for sx in (x + 68, x + 94, x + 120):
        drw.rectangle([sx, y + 12, sx + 4, y + 42], fill=(245, 245, 245))
    drw.line([(x + 20, y + 48), (x + 170, y + 26)], fill=(245, 245, 245),
             width=3)
    drw.ellipse([x + 148, y + 30, x + 158, y + 40], fill=RED)
    drw.rectangle([x + 8, y + 28, x + 52, y + 46], fill=(0, 0, 0))
    drw.text((x + 12, y + 31), "118", font=SANS_B(12),
             fill=(255, 255, 255))
    _label(drw, x, y, "PHILLIPS: 118")
    _vtag(drw, x, y, w, "CONFIRMED", "CONFIRMED")


BIG_PICS = {1: pic_kyiv, 2: pic_akvan, 3: pic_markets}
SMALL_PICS = {4: pic_ukeu, 5: pic_cop31, 6: pic_poland, 7: pic_iraq,
              8: pic_italy, 9: pic_japan, 10: pic_seoul, 11: pic_kenya,
              12: pic_bukele, 13: pic_phillips}


# ---------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-75, 39), (-80, 32),
     (-85, 30), (-90, 21), (-95, 19), (-105, 23), (-115, 30), (-125, 40),
     (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 9), (-75, 11), (-62, 11), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -38), (-68, -52), (-73, -50),
     (-73, -37), (-70, -20), (-80, -5)],
    [(-17, 15), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -10), (35, -20),
     (32, -29), (25, -34), (18, -35), (12, -18), (9, 4), (-8, 5),
     (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 56),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (32, 68), (40, 68),
     (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 70),
     (170, 67), (178, 65), (178, 62), (170, 60), (162, 60), (158, 53),
     (150, 59), (142, 55), (140, 50), (135, 43), (130, 42), (127, 40),
     (122, 39), (120, 35), (115, 32), (110, 30), (108, 22), (105, 20),
     (100, 15), (98, 10), (100, 7), (103, 2), (105, -5), (110, -7),
     (115, -10), (120, -15), (125, -10), (130, -5), (135, -3), (140, -5),
     (145, -10), (150, -15), (153, -25), (150, -35), (145, -38),
     (140, -40), (135, -35), (130, -32), (125, -32), (120, -35),
     (115, -35), (110, -22), (105, -15), (100, -10), (95, 5), (90, 8),
     (85, 10), (80, 13), (77, 8), (75, 15), (72, 20), (70, 23),
     (66, 25), (62, 25), (58, 26), (55, 26), (52, 28), (50, 30),
     (48, 30), (44, 29), (40, 28), (36, 27), (35, 30), (33, 31),
     (30, 36), (26, 38), (23, 36), (20, 40), (18, 42), (15, 44),
     (12, 44), (8, 44), (3, 43), (-2, 43), (-5, 40), (-9, 38), (-10, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -30),
     (150, -22), (146, -19), (142, -15), (140, -12), (135, -12),
     (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)],
]

PINS = {
    1: (204, 833), 2: (247, 866), 3: (279, 860), 4: (170, 832),
    5: (202, 848), 6: (186, 822), 7: (216, 854), 8: (172, 846),
    9: (298, 851), 10: (282, 842), 11: (204, 886), 12: (95, 873),
    13: (322, 936),
}
PIN_REGION = {1: "Europe", 2: "Asia", 3: "Asia", 4: "Europe",
              5: "Global", 6: "Europe", 7: "Middle East", 8: "Europe",
              9: "Asia", 10: "Asia", 11: "Africa", 12: "Americas",
              13: "Oceania"}
REGION_COLOUR = dict(REGIONS)

ALSO_REGION = {14: "Americas", 15: "Asia", 16: "Americas", 17: "Americas",
               18: "Europe", 19: "Oceania", 20: "Africa", 21: "Americas",
               22: "Americas", 23: "Americas", 24: "Global",
               25: "Middle East", 26: "Europe", 27: "Global",
               28: "Americas", 29: "Middle East", 30: "Americas",
               31: "Americas", 32: "Americas", 33: "Oceania",
               34: "Global", 35: "Europe", 36: "Europe", 37: "Europe",
               38: "Middle East", 39: "Middle East", 40: "Africa"}


def draw_map(drw, mx, my, mw, mh):
    drw.rectangle([mx, my, mx + mw, my + mh], fill=SEA,
                  outline=(150, 150, 150), width=1)
    for poly in CONTINENTS:
        pts = [(mx + (lon + 180) / 360.0 * mw,
                my + (85 - lat) / 145.0 * mh) for lon, lat in poly]
        drw.polygon(pts, fill=LAND, outline=(180, 165, 120))
    for num, (px, py) in sorted(PINS.items()):
        col = REGION_COLOUR[PIN_REGION[num]]
        drw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                    outline=(255, 255, 255), width=1)
        fnt = SANS_B(8 if num >= 10 else 9)
        label = str(num)
        tw = fnt.getlength(label)
        drw.text((px - tw / 2, py - 5), label, font=fnt,
                 fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    drw = ImageDraw.Draw(img)
    mx = 16
    cx = W // 2

    # kicker line
    drw.text((mx, 6), "THE WORLD IN ONE DAY", font=SANS_B(11), fill=RED)
    right = "40 STORIES · 7 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    fnt = SANS(10)
    drw.text((W - mx - fnt.getlength(right), 7), right, font=fnt, fill=INK)
    rule(drw, mx, W - mx, 22, width=2)

    # masthead, shrunk until it fits
    title = "Friday 20 November 2026"
    size = 58
    while SERIF_B(size).getlength(title) > W - 2 * mx and size > 40:
        size -= 1
    draw_centred(drw, title, SERIF_B(size), cx, 24, INK)

    # sub-headline
    sub = ("Russian missiles hit Kyiv's bridges · Cyclone Akvan strikes "
           "India · An AI sell-off sinks Asia's markets · UK and EU seal "
           "a deal")
    draw_centred(drw, sub, SERIF(14), cx, 96, INK)
    rule(drw, mx, W - mx, 114, width=1)

    # THE DAY IN UTC timeline
    drw.rectangle([mx, 118, 100, 160], fill=RED)
    draw_centred(drw, "THE DAY", SANS_B(12), 58, 126, (255, 255, 255))
    draw_centred(drw, "IN UTC", SANS_B(12), 58, 142, (255, 255, 255))
    drw.line([(112, 140), (1000, 140)], fill=(150, 150, 150), width=2)
    xs = [175, 303, 431, 559, 687, 815, 940]
    for (t, lab), px in zip(TIMELINE, xs):
        drw.ellipse([px - 4, 136, px + 4, 144], fill=RED,
                    outline=(255, 255, 255), width=1)
        draw_centred(drw, t, SANS_B(11), px, 122, RED)
        draw_centred(drw, lab, SANS(9), px, 147, INK)

    # THE DAY IN NUMBERS strip
    drw.rectangle([mx, 164, 150, 204], fill=RED)
    draw_centred(drw, "THE DAY", SANS_B(12), 83, 172, (255, 255, 255))
    draw_centred(drw, "IN NUMBERS", SANS_B(12), 83, 188, (255, 255, 255))
    cell = 850 / 6
    for i, (num, cap) in enumerate(STATS):
        x0 = 158 + i * cell
        if i:
            drw.line([(int(x0), 168), (int(x0), 200)], fill=RED, width=2)
        draw_centred(drw, num, SANS_B(22), x0 + cell / 2, 170,
                     RED if num.startswith("-") else INK)
        draw_centred(drw, cap, SANS(9), x0 + cell / 2, 196, GREY)

    # region bar: segments sized by story count
    counts = {}
    for _, _, _, region, *_ in LEADS + NUMBERED:
        counts[region] = counts.get(region, 0) + 1
    for _, _, region in [(n, t, ALSO_REGION[n]) for n, t, _ in ALSO]:
        counts[region] = counts.get(region, 0) + 1
    total = sum(counts.values())
    bx = mx
    names = [n for n, _ in REGIONS if counts.get(n, 0)]
    for k, (name, col) in enumerate(REGIONS):
        n = counts.get(name, 0)
        if n == 0:
            continue
        seg = (W - mx - bx) if k == len(names) - 1 else \
            int(round((W - 2 * mx) * n / total))
        drw.rectangle([bx, 210, bx + seg - 1, 228], fill=col)
        lab = "%s %d" % (name, n)
        fnt = SANS_B(10)
        if fnt.getlength(lab) <= seg - 6:
            draw_centred(drw, lab, fnt, bx + seg // 2, 214,
                         (255, 255, 255))
        bx += seg

    # three lead stories
    lead_w, lead_x = 320, [16, 344, 672]
    for (num, place, topic, region, _lab, head, body, src), lx in zip(
            LEADS, lead_x):
        BIG_PICS[num](drw, lx, 234, lead_w, 128)
        drw.ellipse([lx, 366, lx + 15, 381], fill=RED)
        nf = SANS_B(9)
        drw.text((lx + 8 - nf.getlength(str(num)) / 2, 368), str(num),
                 font=nf, fill=(255, 255, 255))
        drw.text((lx + 20, 367), "%s · %s" % (place, topic), font=SANS_B(10),
                 fill=RED)
        draw_wrapped(drw, head, SERIF_B(19), lx, 384, lead_w, 3, lh=22)
        draw_wrapped(drw, body + " (%s)" % src, SANS(11), lx, 454, lead_w,
                     3, fill=INK, lh=15)

    # ten numbered stories, two rows of five
    col_w, col_x = 192, [16, 216, 416, 616, 816]
    for row in range(2):
        y0 = 507 + row * 132
        for col in range(5):
            num, place, topic, region, label, head, body, src = \
                NUMBERED[row * 5 + col]
            lx = col_x[col]
            SMALL_PICS[num](drw, lx, y0, col_w, 54)
            drw.text((lx, y0 + 58), "%d %s · %s" % (num, place, topic),
                     font=SANS_B(10), fill=RED)
            draw_wrapped(drw, head, SERIF_B(12), lx, y0 + 72, col_w, 2,
                         lh=14)
            draw_wrapped(drw, body + " (%s)" % src, SANS(10), lx, y0 + 102,
                         col_w, 2, fill=INK, lh=11)

    # map + also-list headers
    drw.text((mx, 771), "WHERE IT HAPPENED", font=SANS_B(11), fill=RED)
    drw.text((340, 771), "ALSO ON FRIDAY 20 NOVEMBER — 27 MORE STORIES",
             font=SANS_B(11), fill=RED)
    draw_map(drw, mx, 789, 314, 171)
    for i, (num, text, src) in enumerate(ALSO):
        col = i // 14
        row = i % 14
        lx = 340 + col * 336
        ry = 792 + row * 12
        nf = SANS_B(9)
        drw.text((lx, ry), str(num), font=nf, fill=RED)
        tx = lx + nf.getlength(str(num)) + 4
        drw.text((tx, ry), text, font=SANS(9), fill=INK)
        tw = SANS(9).getlength(text)
        drw.text((tx + tw + 3, ry), "(%s)" % src, font=SANS(9), fill=GREY)
        if tx + tw + 3 + SANS(9).getlength("(%s)" % src) > lx + 324:
            WARNED.append("ALSO %d too wide" % num)

    # DATE CHECK strip
    drw.rectangle([mx, 966, W - mx, 998], outline=RED, width=2)
    drw.rectangle([mx + 2, 968, mx + 108, 996], fill=RED)
    drw.text((mx + 8, 977), "DATE CHECK", font=SANS_B(11),
             fill=(255, 255, 255))
    draw_wrapped(drw, DATE_CHECK, SANS(10), mx + 116, 970, W - mx - 124, 2,
                 lh=12)

    # footer
    drw.text((mx, 1004), FOOTER_L, font=SANS(9), fill=GREY)
    rf = SANS(9)
    drw.text((W - mx - rf.getlength(FOOTER_R), 1004), FOOTER_R, font=rf,
             fill=GREY)

    img.save(OUT, "PNG")
    return img


def main():
    build()
    if WARNED:
        for w in WARNED:
            print("WARN:", w)
        sys.exit(1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

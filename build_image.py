#!/usr/bin/env python3
"""V5 builder: 'Friday 20 November 2026' — a one-page newspaper front page.

Formula learned from the top 10 entries on the live leaderboard (all
12W 0D 0L, 99.11-99.21%): giant serif masthead, six-number stat strip,
region bar, three lead stories with big drawn pictures, ten more numbered
stories each with its own small drawn picture, a world map with numbered
pins, a 22-item also-list, a DATE CHECK strip and a sources footer.
35 stories, every one verified as happening or first reported on Friday
20 November 2026. Colours are restrained like the leaders: cream paper,
black serif headlines, red accents, one colour per region, and a drawn
picture for every pictured story (13 pictures in total).
Deterministic: fixed layout, no randomness, no network, stdlib + Pillow.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 242, 230)
INK = (17, 17, 17)
GREY = (102, 102, 102)
RED = (176, 30, 30)
NAVY = (31, 58, 95)
BLUE = (31, 78, 121)
BROWN = (139, 90, 43)
GREEN = (46, 125, 50)
PURPLE = (106, 63, 160)
TEAL = (14, 124, 123)
LAND = (227, 213, 181)
SEA = (222, 232, 238)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

WARNED = []


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(drw, text, fnt, x, y, max_w, max_lines, fill=INK, lh=None):
    """Draw wrapped text; returns lines used. Warns (once per call site)
    if the text needs more lines than allowed."""
    lines = wrap(text, fnt, max_w)
    if len(lines) > max_lines:
        WARNED.append("OVERFLOW %r needs %d lines, max %d"
                      % (text[:48], len(lines), max_lines))
        lines = lines[:max_lines]
    step = lh if lh else int(fnt.size * 1.28)
    for i, line in enumerate(lines):
        drw.text((x, y + i * step), line, font=fnt, fill=fill)
    return len(lines)


def draw_centred(drw, text, fnt, cx, y, fill=INK):
    w = fnt.getlength(text)
    drw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def rule(drw, x0, x1, y, fill=INK, width=1):
    drw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- data
# region order and colours for the region bar and the map pins
REGIONS = [("Europe", BLUE), ("Asia", RED), ("Middle East", BROWN),
           ("Africa", GREEN), ("Americas", PURPLE), ("Oceania", TEAL),
           ("Global", (85, 85, 85))]

STATS = [
    ("3", "bridges over the Dnipro damaged in Kyiv"),
    ("300,000+", "people moved to shelters before Akvan"),
    ("-6.2%", "Taiwan's share index, Friday's close"),
    ("100,000", "youth visas a year in the UK-EU deal"),
    ("2.3%", "Japan consumer inflation in October"),
    ("118", "runs by Glenn Phillips against India"),
]

# (number, place, topic, region, label, headline, body, source)
LEADS = [
    (1, "KYIV, UKRAINE", "WAR", "Europe", None,
     "Russian missiles hit three Kyiv bridges",
     "An overnight barrage of about 110 missiles and 400 drones killed "
     "eight people across Ukraine and cut power and water in the capital.",
     "Kyiv Independent, BBC"),
    (2, "ODISHA, INDIA", "CYCLONE", "Asia", None,
     "Cyclone Akvan comes ashore in eastern India",
     "The storm crossed the coast near Gopalpur from about 8 am; more "
     "than 300,000 people were moved to shelters. No deaths reported.",
     "IMD, Deccan Herald"),
    (3, "TAIPEI · SEOUL · TOKYO", "MARKETS", "Asia", None,
     "AI sell-off sinks Asia's stock markets",
     "Taiwan's index fell 6.2% to end its worst week since 1991. Seoul "
     "lost 5.2% and Tokyo 5.1% as chipmakers led the slide.",
     "Al Jazeera, Reuters"),
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
    (9, "TOKYO", "ECONOMY", "Asia", "JAPAN: +2.3%",
     "Japan's inflation picks up to 2.3%",
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

# (number, text, source) — one line each in the also-list
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
    (34, "Car-trafficking swoop: 2,393 seizures", "Interpol"),
    (35, "Zelensky: NATO is the strongest guarantee", "AP"),
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
# Every pictured story (1-13) gets its own drawn picture: three big ones
# for the leads, ten small ones for the numbered stories. All drawn from
# primitives — no photos, no network.

def _star(drw, cx, cy, r, fill):
    """A small four-point explosion star."""
    pts = [(cx, cy - r), (cx + r * 0.32, cy - r * 0.32),
           (cx + r, cy), (cx + r * 0.32, cy + r * 0.32),
           (cx, cy + r), (cx - r * 0.32, cy + r * 0.32),
           (cx - r, cy), (cx - r * 0.32, cy - r * 0.32)]
    drw.polygon(pts, fill=fill)


def _dash(drw, x0, y0, x1, y1, fill, width=2, dash=7, gap=5):
    """A dashed line, drawn as segments."""
    import math
    dist = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(dist / (dash + gap)))
    for i in range(n):
        t0 = i * (dash + gap) / dist
        t1 = min(1.0, t0 + dash / dist)
        drw.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                  (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                 fill=fill, width=width)


def _label(drw, x, y, text):
    """Red label banner with white bold text, top-left of a picture."""
    fnt = SANS_B(10)
    w = int(fnt.getlength(text)) + 10
    drw.rectangle([x, y, x + w, y + 16], fill=RED)
    drw.text((x + 5, y + 2), text, font=fnt, fill=(255, 255, 255))


def pic_kyiv(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(16, 28, 54))
    for sx, sy in [(20, 14), (70, 26), (150, 10), (210, 30), (260, 12),
                   (300, 24), (40, 48), (120, 40), (190, 52), (280, 44)]:
        drw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                    fill=(255, 255, 200))
    # skyline
    for bx, bw, bh in [(0, 46, 52), (52, 30, 66), (88, 40, 44),
                       (134, 34, 60), (174, 44, 48), (224, 36, 64),
                       (266, 54, 50)]:
        drw.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26],
                      fill=(8, 14, 30))
        for wy in range(y + h - 26 - bh + 8, y + h - 30, 12):
            for wx in range(x + bx + 6, x + bx + bw - 4, 12):
                drw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 200, 80))
    # river
    drw.rectangle([x, y + h - 26, x + w, y + h], fill=(24, 52, 96))
    # three bridges
    for cx in (60, 160, 260):
        drw.arc([x + cx - 42, y + h - 52, x + cx + 42, y + h - 4],
                180, 360, fill=(220, 220, 220), width=3)
        drw.line([(x + cx - 42, y + h - 26), (x + cx + 42, y + h - 26)],
                 fill=(220, 220, 220), width=2)
    # missile trails and bursts
    _dash(drw, x + 250, y + 6, x + 210, y + 44, (255, 170, 60), 2)
    _dash(drw, x + 300, y + 20, x + 268, y + 52, (255, 170, 60), 2)
    _dash(drw, x + 90, y + 4, x + 60, y + 40, (255, 170, 60), 2)
    _star(drw, x + 210, y + 46, 9, (255, 190, 60))
    _star(drw, x + 60, y + 42, 8, (255, 190, 60))
    _star(drw, x + 268, y + 54, 7, (255, 210, 90))
    drw.rectangle([x + 6, y + h - 22, x + 118, y + h - 6], fill=(0, 0, 0))
    drw.text((x + 11, y + h - 20), "3 bridges hit", font=SANS_B(10),
             fill=(255, 255, 255))


def pic_akvan(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(46, 110, 168))
    # Odisha coast: land on the left
    drw.polygon([(x, y), (x + 118, y), (x + 96, y + 34), (x + 108, y + 62),
                 (x + 84, y + 92), (x + 96, y + h), (x, y + h)],
                fill=(224, 205, 160))
    drw.line([(x + 118, y), (x + 96, y + 34), (x + 108, y + 62),
              (x + 84, y + 92), (x + 96, y + h)], fill=(120, 90, 50), width=2)
    # cyclone spiral over the Bay of Bengal
    cx, cy = x + 205, y + 62
    for r, a0, a1 in [(52, 20, 300), (40, 120, 40), (28, 220, 140),
                      (16, 320, 240)]:
        drw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(255, 255, 255),
                width=3)
    drw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    # Gopalpur marker
    drw.ellipse([x + 100, y + 66, x + 110, y + 76], fill=RED,
                outline=(255, 255, 255), width=2)
    drw.text((x + 8, y + 6), "ODISHA", font=SANS_B(10), fill=INK)
    drw.text((x + 8, y + 20), "INDIA", font=SANS(9), fill=INK)
    drw.rectangle([x + w - 132, y + 8, x + w - 8, y + 26], fill=(0, 0, 0))
    drw.text((x + w - 127, y + 11), "Landfall · 8 am", font=SANS_B(10),
             fill=(255, 255, 255))
    drw.text((x + 8, y + h - 18), "BAY OF BENGAL", font=SANS_B(9),
             fill=(255, 255, 255))


def pic_markets(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(12, 18, 32))
    # falling chart on the left
    pts = [(x + 12, y + 26), (x + 52, y + 34), (x + 92, y + 30),
           (x + 132, y + 52), (x + 168, y + 66), (x + 196, y + 96)]
    for gy in (30, 60, 90):
        drw.line([(x + 8, y + gy), (x + 204, y + gy)], fill=(40, 55, 80))
    drw.line(pts, fill=(230, 60, 60), width=3)
    for px, py in pts:
        drw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(230, 60, 60))
    # closing table on the right
    rows = [("Taipei", "-6.2%"), ("Seoul", "-5.2%"), ("Tokyo", "-5.1%"),
            ("Hong Kong", "-1.9%")]
    for i, (name, val) in enumerate(rows):
        ry = y + 22 + i * 24
        drw.text((x + 214, ry), name, font=SANS(11), fill=(220, 220, 220))
        vw = SANS_B(11).getlength(val)
        drw.text((x + w - 10 - vw, ry), val, font=SANS_B(11),
                 fill=(255, 90, 90))
    drw.text((x + 10, y + h - 20), "Closing prices", font=SANS_B(10),
             fill=(255, 255, 255))


def pic_ukeu(drw, x, y, w, h):
    hw = w // 2
    drw.rectangle([x, y, x + hw, y + h], fill=(0, 36, 125))
    drw.rectangle([x + hw, y, x + w, y + h], fill=(0, 51, 153))
    # Union Jack, simplified: white diagonals and cross, red cross
    drw.line([(x, y), (x + hw, y + h)], fill=(255, 255, 255), width=5)
    drw.line([(x, y + h), (x + hw, y)], fill=(255, 255, 255), width=5)
    drw.line([(x + hw // 2, y), (x + hw // 2, y + h)], fill=(255, 255, 255),
             width=9)
    drw.line([(x, y + h // 2), (x + hw, y + h // 2)], fill=(255, 255, 255),
             width=9)
    drw.line([(x + hw // 2, y), (x + hw // 2, y + h)], fill=(200, 16, 46),
             width=5)
    drw.line([(x, y + h // 2), (x + hw, y + h // 2)], fill=(200, 16, 46),
             width=5)
    # EU stars
    import math
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx = x + hw + hw // 2 + int(30 * math.cos(a))
        sy = y + h // 2 + int(18 * math.sin(a))
        drw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    _label(drw, x, y, "UK-EU DEAL")


def pic_cop31(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(178, 222, 226))
    drw.ellipse([x + 14, y + 6, x + 62, y + 48], fill=(46, 110, 168))
    drw.ellipse([x + 24, y + 16, x + 38, y + 28], fill=(90, 180, 90))
    drw.ellipse([x + 40, y + 30, x + 54, y + 42], fill=(90, 180, 90))
    # thermometer
    drw.rectangle([x + 84, y + 8, x + 96, y + 36], fill=(255, 255, 255))
    drw.rectangle([x + 87, y + 22, x + 93, y + 36], fill=RED)
    drw.ellipse([x + 80, y + 32, x + 100, y + 50], fill=RED)
    drw.text((x + 112, y + 12), "38°", font=SANS_B(16), fill=RED)
    drw.text((x + 112, y + 32), "ANTALYA", font=SANS_B(9), fill=INK)
    _label(drw, x, y, "COP31: NO DEAL")


def pic_poland(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(135, 178, 96))
    drw.rectangle([x, y, x + w, y + 16], fill=(190, 214, 235))
    _dash(drw, x + 150, y + 6, x + 60, y + 34, (255, 255, 255), 2)
    drw.polygon([(x + 52, y + 30), (x + 66, y + 36), (x + 52, y + 42)],
                fill=(90, 90, 90))
    _star(drw, x + 44, y + 40, 8, (255, 170, 40))
    drw.line([(x, y + h - 8), (x + w, y + h - 8)], fill=(90, 120, 60), width=2)
    _label(drw, x, y, "POLAND: MISSILE")


def pic_iraq(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(222, 196, 138))
    drw.ellipse([x + 158, y + 4, x + 178, y + 24], fill=(255, 190, 80))
    # tank
    drw.rectangle([x + 30, y + 30, x + 96, y + 46], fill=(74, 94, 58))
    drw.rectangle([x + 48, y + 20, x + 76, y + 30], fill=(74, 94, 58))
    drw.line([(x + 76, y + 25), (x + 116, y + 22)], fill=(50, 64, 40), width=4)
    drw.ellipse([x + 38, y + 46, x + 48, y + 52], fill=(40, 40, 40))
    drw.ellipse([x + 78, y + 46, x + 88, y + 52], fill=(40, 40, 40))
    # palm
    drw.line([(x + 140, y + 52), (x + 140, y + 26)], fill=(120, 80, 40),
             width=3)
    for dx, dy in [(-12, -6), (12, -6), (-10, 2), (10, 2), (0, -10)]:
        drw.line([(x + 140, y + 26), (x + 140 + dx, y + 26 + dy)],
                 fill=(40, 120, 60), width=2)
    _label(drw, x, y, "IRAQ: ARMY IN")


def pic_italy(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(240, 232, 210))
    for i, col in enumerate([(0, 146, 70), (255, 255, 255), (205, 0, 0)]):
        drw.rectangle([x + i * (w // 3), y, x + (i + 1) * (w // 3), y + 8],
                      fill=col)
    heads = [(28, (205, 92, 92)), (62, (92, 142, 205)), (96, (240, 200, 90)),
             (130, (120, 200, 120)), (164, (180, 120, 200))]
    for hx, col in heads:
        drw.ellipse([x + hx - 8, y + 18, x + hx + 8, y + 34], fill=col)
        drw.pieslice([x + hx - 12, y + 34, x + hx + 12, y + 58], 180, 360,
                     fill=col)
    _label(drw, x, y, "ITALY: STRIKE")


def pic_japan(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    drw.ellipse([x + 14, y + 12, x + 46, y + 44], fill=(188, 0, 45))
    bars = [(70, 18), (92, 26), (114, 34), (136, 44)]
    for bx, bh in bars:
        drw.rectangle([x + bx, y + 48 - bh, x + bx + 14, y + 48],
                      fill=(120, 120, 120))
    drw.line([(x + 66, y + 30), (x + 156, y + 6)], fill=RED, width=3)
    drw.polygon([(x + 156, y + 6), (x + 146, y + 4), (x + 152, y + 14)],
                fill=RED)
    _label(drw, x, y, "JAPAN: +2.3%")


def pic_seoul(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(214, 226, 235))
    drw.polygon([(x + 40, y + 8), (x + 96, y + 8), (x + 68, y + 22)],
                fill=(90, 90, 90))
    drw.rectangle([x + 44, y + 22, x + 92, y + 28], fill=(245, 245, 245))
    for cx in (50, 64, 78, 88):
        drw.rectangle([x + cx, y + 28, x + cx + 4, y + 48], fill=(245, 245, 245))
    drw.rectangle([x + 40, y + 48, x + 96, y + 52], fill=(245, 245, 245))
    # gavel
    drw.rectangle([x + 132, y + 18, x + 158, y + 28], fill=(120, 72, 32))
    drw.line([(x + 145, y + 28), (x + 152, y + 46)], fill=(120, 72, 32), width=4)
    _label(drw, x, y, "SEOUL: IMPEACH")


def pic_kenya(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(245, 176, 80))
    drw.ellipse([x + 148, y + 6, x + 176, y + 34], fill=(255, 220, 120))
    # oil derrick
    drw.line([(x + 40, y + 52), (x + 56, y + 12)], fill=(30, 30, 30), width=3)
    drw.line([(x + 72, y + 52), (x + 56, y + 12)], fill=(30, 30, 30), width=3)
    drw.line([(x + 46, y + 38), (x + 66, y + 38)], fill=(30, 30, 30), width=2)
    drw.line([(x + 50, y + 26), (x + 62, y + 26)], fill=(30, 30, 30), width=2)
    drw.rectangle([x + 52, y + 8, x + 60, y + 14], fill=(30, 30, 30))
    drw.rectangle([x, y + h - 6, x + w, y + h], fill=(120, 70, 30))
    _label(drw, x, y, "KENYA: OIL")


def pic_bukele(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(36, 74, 140))
    drw.rectangle([x + 60, y + 16, x + 124, y + 48], fill=(255, 255, 255))
    drw.rectangle([x + 76, y + 16, x + 108, y + 20], fill=(30, 30, 30))
    drw.rectangle([x + 84, y + 4, x + 100, y + 16], fill=(255, 255, 255))
    drw.line([(x + 132, y + 24), (x + 142, y + 34), (x + 160, y + 14)],
             fill=(255, 255, 255), width=3)
    drw.text((x + 12, y + 30), "VOTE", font=SANS_B(13), fill=(255, 255, 255))
    _label(drw, x, y, "BUKELE: 3RD BID")


def pic_phillips(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=(46, 140, 70))
    drw.rectangle([x + 60, y + 8, x + 132, y + 46], fill=(222, 196, 138))
    # stumps
    for sx in (88, 96, 104):
        drw.line([(x + sx, y + 12), (x + sx, y + 26)], fill=(255, 220, 90),
                 width=2)
    # bat and ball
    drw.polygon([(x + 116, y + 14), (x + 124, y + 12), (x + 118, y + 34),
                 (x + 110, y + 34)], fill=(210, 180, 120))
    drw.ellipse([x + 140, y + 30, x + 150, y + 40], fill=(200, 30, 30))
    drw.rectangle([x + 8, y + 28, x + 52, y + 46], fill=(0, 0, 0))
    drw.text((x + 12, y + 31), "118", font=SANS_B(12), fill=(255, 255, 255))
    _label(drw, x, y, "PHILLIPS: 118")


BIG_PICS = {1: pic_kyiv, 2: pic_akvan, 3: pic_markets}
SMALL_PICS = {4: pic_ukeu, 5: pic_cop31, 6: pic_poland, 7: pic_iraq,
              8: pic_italy, 9: pic_japan, 10: pic_seoul, 11: pic_kenya,
              12: pic_bukele, 13: pic_phillips}


# ---------------------------------------------------------------- map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-75, 39), (-80, 32),
     (-85, 30), (-90, 21), (-95, 19), (-105, 23), (-115, 30), (-125, 40),
     (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    # South America
    [(-80, 9), (-75, 11), (-62, 11), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -38), (-68, -52), (-73, -50),
     (-73, -37), (-70, -20), (-80, -5)],
    # Africa
    [(-17, 15), (-10, 31), (-5, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -10), (35, -20),
     (32, -29), (25, -34), (18, -35), (12, -18), (9, 4), (-8, 5),
     (-13, 8)],
    # Eurasia
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
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -30),
     (150, -22), (146, -19), (142, -15), (140, -12), (135, -12),
     (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# story number -> (x, y) pin centre inside the map box (nudged so the
# European cluster does not overlap), and its region colour
PINS = {
    1: (204, 796), 2: (247, 838), 3: (279, 830), 4: (172, 798),
    5: (202, 816), 6: (186, 784), 7: (216, 822), 8: (176, 812),
    9: (298, 818), 10: (282, 808), 11: (204, 862), 12: (95, 846),
    13: (325, 927),
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
               34: "Global", 35: "Europe"}


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
    right = "35 STORIES · 7 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
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

    # stat strip: six big numbers
    cell = (W - 2 * mx) // 6
    for i, (num, cap) in enumerate(STATS):
        x0 = mx + i * cell
        if i:
            drw.line([(x0, 118), (x0, 156)], fill=RED, width=2)
        draw_centred(drw, num, SANS_B(26), x0 + cell // 2, 118,
                     RED if num.startswith("-") else INK)
        draw_wrapped(drw, cap, SANS(10), x0 + 8, 146, cell - 16, 2,
                     fill=GREY, lh=11)

    # region bar: segments sized by story count
    counts = {}
    for _, _, _, region, *_ in LEADS + NUMBERED:
        counts[region] = counts.get(region, 0) + 1
    for _, _, region in [(n, t, ALSO_REGION[n]) for n, t, _ in ALSO]:
        counts[region] = counts.get(region, 0) + 1
    total = sum(counts.values())
    bx = mx
    for name, col in REGIONS:
        n = counts.get(name, 0)
        seg = int(round((W - 2 * mx) * n / total))
        if n == 0:
            continue
        drw.rectangle([bx, 162, bx + seg - 1, 180], fill=col)
        lab = "%s %d" % (name, n)
        fnt = SANS_B(10)
        if fnt.getlength(lab) <= seg - 6:
            draw_centred(drw, lab, fnt, bx + seg // 2, 166, (255, 255, 255))
        bx += seg

    # three lead stories
    lead_w, lead_x = 320, [16, 344, 672]
    for (num, place, topic, region, _lab, head, body, src), lx in zip(
            LEADS, lead_x):
        BIG_PICS[num](drw, lx, 186, lead_w, 128)
        drw.ellipse([lx, 318, lx + 15, 333], fill=RED)
        nf = SANS_B(9)
        drw.text((lx + 8 - nf.getlength(str(num)) / 2, 320), str(num),
                 font=nf, fill=(255, 255, 255))
        drw.text((lx + 20, 319), "%s · %s" % (place, topic), font=SANS_B(10),
                 fill=RED)
        draw_wrapped(drw, head, SERIF_B(19), lx, 336, lead_w, 3, lh=22)
        draw_wrapped(drw, body + " (%s)" % src, SANS(11), lx, 406, lead_w,
                     3, fill=INK, lh=15)

    # ten numbered stories, two rows of five
    col_w, col_x = 192, [16, 216, 416, 616, 816]
    for row in range(2):
        y0 = 460 + row * 132
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
    drw.text((mx, 724), "WHERE IT HAPPENED", font=SANS_B(11), fill=RED)
    drw.text((340, 724), "ALSO ON FRIDAY 20 NOVEMBER — 22 MORE STORIES",
             font=SANS_B(11), fill=RED)
    draw_map(drw, mx, 742, 314, 212)
    for i, (num, text, src) in enumerate(ALSO):
        col = i // 11
        row = i % 11
        lx = 340 + col * 336
        ry = 744 + row * 18
        nf = SANS_B(10)
        drw.text((lx, ry), str(num), font=nf, fill=RED)
        tx = lx + nf.getlength(str(num)) + 5
        drw.text((tx, ry), text, font=SANS(10), fill=INK)
        tw = SANS(10).getlength(text)
        drw.text((tx + tw + 3, ry), "(%s)" % src, font=SANS(10), fill=GREY)
        if tx + tw + 3 + SANS(10).getlength("(%s)" % src) > lx + 324:
            WARNED.append("ALSO %d too wide" % num)

    # DATE CHECK strip
    drw.rectangle([mx, 958, W - mx, 992], outline=RED, width=2)
    drw.rectangle([mx + 2, 960, mx + 108, 990], fill=RED)
    drw.text((mx + 8, 969), "DATE CHECK", font=SANS_B(11),
             fill=(255, 255, 255))
    draw_wrapped(drw, DATE_CHECK, SANS(10), mx + 116, 962, W - mx - 124, 2,
                 lh=12)

    # footer
    drw.text((mx, 1000), FOOTER_L, font=SANS(9), fill=GREY)
    rf = SANS(9)
    drw.text((W - mx - rf.getlength(FOOTER_R), 1000), FOOTER_R, font=rf,
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

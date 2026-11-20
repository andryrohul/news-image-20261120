#!/usr/bin/env python3
"""Build the v2 entry image: 'The World in One Day' as a 24-hour clock.

Unique concept: the day is told by the hour. A 24-hour dial shows when
each of the twelve biggest stories broke (WIB, UTC+7), three lead stories
sit beside it with a small drawn picture each, then the rest of the day
follows as numbered briefs and a one-line list. A DATE CHECK strip names
the big stories that were reported BEFORE Friday, so they are not shown
as Friday news.

Everything is drawn with PIL from scratch. No network, no photos, no
external assets. Deterministic: same bytes every run.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (26, 26, 26)
RED = (160, 30, 34)
NAVY = (31, 58, 95)
TEAL = (18, 90, 86)
GOLD = (176, 124, 30)
FAINT = (120, 110, 92)
CARD = (255, 253, 245)
RULE = (196, 182, 150)

FDIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FDIR + name, size)


SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF_R = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS_R = lambda s: font("DejaVuSans.ttf", s)
ITALIC = lambda s: font("DejaVuSerif-Italic.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None, max_lines=None):
    """Draw lines of text; returns y after the last line."""
    lh = leading or int(fnt.size * 1.22)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def headline(draw, x, y, text, fnt, width, fill=INK, max_lines=2):
    lines = wrap(draw, text, fnt, width)
    return text_block(draw, x, y, lines, fnt, fill=fill, max_lines=max_lines)


def rule(draw, x, y, w, fill=INK, width=2):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- masthead
d.text((16, 10), "THE WORLD IN ONE DAY", font=SERIF(46), fill=INK)
d.text((16, 60), "FRIDAY 20 NOVEMBER 2026", font=SANS(15), fill=RED)
d.text((16, 80), "ONE DAY, EVERY TIME ZONE  \u2022  36 STORIES  \u2022  TOLD BY THE HOUR",
       font=SANS_R(12), fill=INK)
d.text((W - 16, 60), "ALL TIMES WIB (UTC+7)", font=SANS(11), fill=FAINT, anchor="ra")
d.text((W - 16, 80), "WHEN EACH STORY BROKE", font=SANS_R(10), fill=FAINT, anchor="ra")
rule(d, 16, 100, W - 32, width=3)
rule(d, 16, 104, W - 32, fill=RULE, width=1)

# --------------------------------------------------------------- stat strip
stats = [
    ("300,000", "evacuated ahead of Cyclone Akvan"),
    ("$97.17", "Anthropic's first close, +17%"),
    ("118", "Phillips' historic century"),
    ("51\u201348", "Senate rejects Iran war-powers bid"),
    ("$2.36bn", "GTA VI's first-day sales"),
    ("99", "GTA VI's Metacritic score"),
]
sx, sw = 16, (W - 32) / 6
for i, (num, label) in enumerate(stats):
    cx = sx + i * sw
    d.text((cx + 4, 112), num, font=SERIF(24), fill=RED)
    headline(d, cx + 4, 142, label, SANS_R(10), sw - 10, max_lines=2)
rule(d, 16, 172, W - 32, width=2)

# ------------------------------------------------------------- clock section
# 24-hour dial: hour h sits at angle (h/24)*360 - 90 degrees.
CX, CY, R = 218, 352, 168
d.ellipse([CX - R - 8, CY - R - 8, CX + R + 8, CY + R + 8], fill=CARD,
          outline=INK, width=3)
d.ellipse([CX - R + 26, CY - R + 26, CX + R - 26, CY + R - 26],
          outline=RULE, width=1)
for h in range(24):
    a = math.radians((h / 24) * 360 - 90)
    inner = R - 8 if h % 6 == 0 else R - 4
    d.line([(CX + inner * math.cos(a), CY + inner * math.sin(a)),
            (CX + R * math.cos(a), CY + R * math.sin(a))],
           fill=INK, width=3 if h % 6 == 0 else 1)
for h, lab in ((0, "00"), (6, "06"), (12, "12"), (18, "18")):
    a = math.radians((h / 24) * 360 - 90)
    d.text((CX + (R - 24) * math.cos(a), CY + (R - 24) * math.sin(a) - 7),
           lab, font=SANS(11), fill=FAINT, anchor="mm")
d.text((CX, CY - 52), "20 NOV", font=SERIF(26), fill=INK, anchor="mm")
d.text((CX, CY - 26), "ONE DAY", font=SANS(12), fill=RED, anchor="mm")
d.text((CX, CY + 44), "WHEN THE DAY BROKE", font=SANS(10), fill=FAINT,
       anchor="mm")
d.text((CX, CY + 58), "EACH NUMBER = ONE STORY", font=SANS(10), fill=FAINT,
       anchor="mm")

CLOCK = [
    # (story no, hour WIB)
    (1, 9), (2, 13), (3, 4), (4, 10), (5, 3), (6, 7),
    (7, 15), (8, 11), (9, 8), (10, 17), (11, 6), (12, 12),
]
for num, hour in CLOCK:
    a = math.radians((hour / 24) * 360 - 90)
    rr = R - 46
    px, py = CX + rr * math.cos(a), CY + rr * math.sin(a)
    d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=RED, outline=PAPER,
              width=2)
    d.text((px, py - 1), str(num), font=SANS(12), fill=(255, 255, 255),
           anchor="mm")
d.text((16, 530), "THE DIAL SHOWS WHEN EACH OF THE TWELVE BIGGEST STORIES "
       "BROKE, WESTERN INDONESIA TIME.", font=SANS_R(10), fill=FAINT)

# ------------------------------------------------- lead cards (stories 1-3)
# Each lead gets a small drawn picture on the left: a cyclone spiral,
# an Antalya coast, and a candlestick chart.
LX = 448
LW = W - 16 - LX


def lead_card(y, h, num, kicker, title, body, art):
    d.rectangle([LX, y, LX + LW, y + h], fill=CARD, outline=INK, width=2)
    ax, ay, aw, ah = LX + 10, y + 10, 120, h - 20
    art(ax, ay, aw, ah)
    d.rectangle([ax, ay, ax + aw, ay + ah], outline=INK, width=1)
    tx = ax + aw + 12
    d.text((tx, y + 8), f"{num}  \u2022  {kicker}", font=SANS(11), fill=RED)
    headline(d, tx, y + 26, title, SERIF(19), LW - aw - 24, max_lines=2)
    headline(d, tx, y + 68, body, SANS_R(11), LW - aw - 24, max_lines=3)


def art_cyclone(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx, cy = x + w // 2, y + h // 2 + 8
    for r in range(8, 52, 9):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=470,
              fill=(255, 255, 255), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 214, 90))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(222, 196, 130))
    d.text((x + 6, y + h - 13), "GOPALPUR", font=SANS(8), fill=INK)


def art_coast(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(135, 190, 220))
    d.ellipse([x + w - 34, y + 8, x + w - 10, y + 32], fill=(255, 196, 66))
    d.polygon([(x, y + h), (x + 34, y + 38), (x + 62, y + h)], fill=(96, 128, 84))
    d.polygon([(x + 44, y + h), (x + 82, y + 30), (x + w, y + h)],
              fill=(70, 100, 66))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(58, 110, 150))
    d.text((x + 6, y + h - 16), "ANTALYA", font=SANS(8), fill=(255, 255, 255))


def art_chart(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 44, 32))
    closes = [30, 44, 38, 52, 46, 62, 58, 72]
    bw = w // 9
    for i, c in enumerate(closes):
        bx = x + 6 + i * bw
        top = y + h - 12 - c
        col = (46, 204, 113) if i % 2 == 0 else (231, 76, 60)
        d.rectangle([bx + 2, top, bx + bw - 3, y + h - 12], fill=col)
        d.line([(bx + bw // 2, top - 6), (bx + bw // 2, y + h - 8)],
               fill=col, width=2)
    d.text((x + 6, y + 4), "ANT  $97.17", font=SANS(10), fill=(255, 214, 90))


lead_card(182, 108, 1, "ODISHA \u2022 STORM",
          "Akvan comes ashore in India",
          "Severe Cyclone Akvan crosses the Andhra\u2013Odisha coast near "
          "Gopalpur in the morning; winds 70\u201380, gusting 90 kmph. "
          "More than 300,000 people were moved to 9,341 shelters.",
          art_cyclone)
lead_card(298, 108, 2, "ANTALYA \u2022 CLIMATE",
          "COP31 reaches its final day",
          "Negotiators face a Friday deadline in Antalya. The draft drops "
          "the $120bn adaptation figure and the fossil-fuel phase-out "
          "language; the money fight stays open.",
          art_coast)
lead_card(414, 108, 3, "NEW YORK \u2022 MARKETS",
          "Anthropic ends first day up 17%",
          "The Claude maker opens at $111.50 and closes at $97.17, up 17% "
          "on its $83 offer, after raising $81.3bn in the biggest IPO "
          "ever, as the S&P 500 falls 2.02%.",
          art_chart)

# ------------------------------------------- briefs grid (stories 4 to 12)
# One small drawn icon per card, kept abstract on purpose.
GRID = [
    (4, "SHENZHEN \u2022 DIPLOMACY", "Leaders issue peace declaration",
     "Hours after the trilateral, Trump, Xi and Putin publish a joint "
     "declaration: UN reform, more fuel supply, ICC limits, and a pledge "
     "that nuclear war must never be fought.",
     "flags"),
    (5, "WASHINGTON \u2022 POLITICS", "Senate rejects Iran war-powers bid",
     "The resolution fails 51\u201348, with three Republicans in favour. "
     "It would have ordered an end to the war in Iran without "
     "Congress's approval.",
     "dome"),
    (6, "WELLINGTON \u2022 SPORT", "Phillips makes history with 118",
     "The first batter to score centuries in all three formats against "
     "India in one calendar year. New Zealand reach 317\u20136 at lunch "
     "on day two.",
     "bat"),
    (7, "WORLD \u2022 GAMES", "GTA VI passes $2bn in a day",
     "Sensor Tower counts about $2.36bn and 24.6m copies sold. Metacritic "
     "gives it 99, joint-highest ever. Players watched 132m hours of "
     "streams.",
     "sunset"),
    (8, "CALIFORNIA \u2022 TECH", "State subpoenas Nvidia over China chips",
     "California opens a probe days after ex-CEO Jensen Huang's "
     "resignation, asking whether chips or secrets reached China and "
     "whether investors were misled.",
     "chip"),
    (9, "KYIV \u2022 WAR", "Strikes hit Kyiv embassies",
     "One person is killed as Russian strikes damage the Dutch and "
     "Austrian embassies and a cathedral. The Netherlands summons "
     "Russia's ambassador.",
     "house"),
    (10, "BERLIN \u2022 EUROPE", "Europe ready for Ukraine talks",
     "Allies from 37 nations present a united position on talks with "
     "Russia. Kushner says Moscow is \u201ccomfortable\u201d with "
     "NATO-like guarantees for Kyiv.",
     "gate"),
    (11, "TONGA \u2022 PACIFIC", "Drought emergency in Tonga",
     "The Pacific kingdom declares a 27-day emergency as El Ni\u00f1o "
     "drought bites. Schools close early on Friday; water is rationed "
     "across the islands.",
     "sun"),
    (12, "SENEGAL \u2022 MIGRATION", "Migrant boat sinks off Senegal",
     "Four bodies are recovered from a boat carrying about 100 people "
     "that capsized off Yenne. Dozens are missing as the search goes on.",
     "boat"),
]


def icon(kind, x, y, s=34):
    if kind == "flags":
        for i, col in enumerate(((178, 34, 34), (255, 255, 255), (31, 58, 95))):
            d.rectangle([x + i * 12, y + 6, x + i * 12 + 10, y + 22], fill=col,
                        outline=INK, width=1)
        d.line([(x, y + 30), (x + 36, y + 30)], fill=INK, width=2)
    elif kind == "dome":
        d.polygon([(x + 4, y + 26), (x + 30, y + 26), (x + 30, y + 18),
                   (x + 17, y + 6), (x + 4, y + 18)], fill=NAVY)
        d.rectangle([x, y + 26, x + 34, y + 30], fill=INK)
    elif kind == "bat":
        d.polygon([(x + 6, y + 28), (x + 12, y + 4), (x + 18, y + 6),
                   (x + 12, y + 30)], fill=(222, 196, 130), outline=INK)
        d.ellipse([x + 22, y + 18, x + 32, y + 28], fill=RED)
    elif kind == "sunset":
        d.ellipse([x + 8, y + 4, x + 26, y + 22], fill=(255, 196, 66))
        for yy in range(24, 31, 3):
            d.line([(x, y + yy), (x + 34, y + yy)], fill=(214, 90, 40), width=2)
    elif kind == "chip":
        d.rectangle([x + 6, y + 6, x + 28, y + 28], fill=TEAL, outline=INK,
                    width=1)
        d.rectangle([x + 13, y + 13, x + 21, y + 21], fill=PAPER)
        for xx in (10, 17, 24):
            d.line([(x + xx, y + 2), (x + xx, y + 6)], fill=INK, width=2)
            d.line([(x + xx, y + 28), (x + xx, y + 32)], fill=INK, width=2)
    elif kind == "house":
        d.polygon([(x + 2, y + 18), (x + 17, y + 6), (x + 32, y + 18)],
                  fill=NAVY)
        d.rectangle([x + 5, y + 18, x + 29, y + 30], fill=(222, 196, 130),
                    outline=INK, width=1)
        d.rectangle([x + 14, y + 22, x + 20, y + 30], fill=INK)
    elif kind == "gate":
        for xx in (4, 14, 24):
            d.rectangle([x + xx, y + 10, x + xx + 6, y + 30], fill=INK)
        d.rectangle([x, y + 6, x + 34, y + 10], fill=INK)
    elif kind == "sun":
        d.ellipse([x + 9, y + 4, x + 25, y + 20], fill=(255, 196, 66))
        for xx in (6, 14, 22, 30):
            d.line([(x + xx, y + 26), (x + xx + 4, y + 30)], fill=INK, width=1)
    elif kind == "boat":
        d.polygon([(x + 4, y + 22), (x + 30, y + 22), (x + 25, y + 29),
                   (x + 9, y + 29)], fill=(122, 74, 40))
        d.line([(x + 17, y + 22), (x + 17, y + 8)], fill=INK, width=2)
        d.polygon([(x + 17, y + 8), (x + 17, y + 20), (x + 28, y + 20)],
                  fill=(255, 255, 255), outline=INK)


gx0, gy0 = 16, 556
gw, gh = 320, 78
for i, (num, kicker, title, body, kind) in enumerate(GRID):
    col, row = i % 3, i // 3
    x = gx0 + col * (gw + 8)
    y = gy0 + row * (gh + 5)
    d.rectangle([x, y, x + gw, y + gh], fill=CARD, outline=RULE, width=1)
    icon(kind, x + 8, y + 8)
    d.text((x + 48, y + 6), f"{num} \u2022 {kicker}", font=SANS(9), fill=RED)
    headline(d, x + 48, y + 20, title, SERIF(13), gw - 56, max_lines=1)
    headline(d, x + 48, y + 38, body, SANS_R(9), gw - 56, max_lines=3)

# --------------------------------------- also on Friday (stories 13 to 36)
ALSO = [
    (13, "WASHINGTON", "Trump pardons Pete Rose",
     "The late slugger, banned for life for betting, is pardoned after his death. His 4,256 hits remain the record."),
    (14, "LONDON", "UK and Norway fund \u00a3100m-plus for two Ukrainian naval craft",
     "Two 30-metre fast attack boats, built in Britain, will guard Black Sea trade routes."),
    (15, "JAKARTA", "Indonesia's parliament passes an asset-forfeiture bill",
     "After 18 years, the state may seize assets tied to crime without a conviction first, for assets of Rp1bn or more."),
    (16, "TOKYO", "Japan core inflation 2.2%",
     "Prices stay above target as the Bank of Japan weighs its next move."),
    (17, "PARIS", "IEA counts $3.9tn for AI data centres",
     "The energy agency says data centres will need trillions in power and cooling by the next decade."),
    (18, "NEW YORK", "S&P 500 falls 2.02%; Nasdaq down 2.2%",
     "Tech slides on Thursday even as Anthropic's debut lifts the IPO market."),
    (19, "HORMUZ", "Fourteen attacks on ships in November",
     "UKMTO counts 14 incidents this month; an LPG carrier was abandoned after being hit twice."),
    (20, "GAZA", "Aid groups score the peace plan's implementation 4 out of 26",
     "Agencies say almost none of the plan's promises have been kept."),
    (21, "KINSHASA", "DR Congo Ebola passes 10,600 cases",
     "The outbreak keeps growing as vaccines reach the worst-hit districts."),
    (22, "LILONGWE", "Malawi fuel crisis turns violent",
     "Queues and shortages spill into street protests in the capital."),
    (23, "SHENZHEN", "APEC pact links Mexico, Chile and Peru",
     "The three Pacific economies agree a trade pact on the summit's sidelines."),
    (24, "DOHA", "Rising Stars Asia Cup opens",
     "Asia's young cricketers begin the tournament in Qatar."),
    (25, "SAN SALVADOR", "Bukele begins a third term",
     "The president is sworn in again after a landslide re-election."),
    (26, "GENOA", "Airport shut by a drone sighting",
     "Flights are halted for hours after a drone is seen near the runway."),
    (27, "COPENHAGEN", "Denmark approves a Greenland defence agreement",
     "Parliament backs a deal to strengthen the Arctic island's defences."),
    (28, "GAZA", "Israel ends its Gaza tank raid",
     "Armoured units pull back after a brief incursion, the army says."),
    (29, "NEW YORK", "Dow slips below 50,000",
     "The index gives up the milestone in the broad sell-off."),
    (30, "WORLD", "GTA VI streams draw 132m hours watched",
     "Nearly 8m people watch at once, a record for a game launch."),
    (31, "NEW YORK", "Nvidia shares 40% below their October peak",
     "The chipmaker's stock keeps sliding as the probes widen."),
    (32, "CINCINNATI", "Fiona the hippo dies at 9",
     "The internet-famous hippo dies after swallowing a visitor's hat."),
    (33, "WASHINGTON", "Venezuela TPS ruling due to take effect on Friday",
     "A stay expires, so protections could return for hundreds of thousands; about 1,800 may be freed."),
    (34, "NEW YORK", "Anthropic's $81bn offering closes on Friday",
     "A separate $26bn private placement is set to close right after."),
    (35, "DAKAR", "Senegal navy rescues 1,400 migrants in 48 hours",
     "Crews pull people from pirogues bound for the Canary Islands."),
    (36, "DUBLIN", "Harris seeks border-poll criteria talks with London",
     "Ireland's deputy premier wants a shared understanding of when a vote could be called."),
]

ay = 806
d.text((16, ay), "ALSO ON FRIDAY 20 NOVEMBER \u2014 24 MORE STORIES",
       font=SANS(12), fill=RED)
rule(d, 16, ay + 18, W - 32, width=2)
col_w = (W - 32) // 2
ly = ay + 26
for i, (num, place, title, body) in enumerate(ALSO):
    col = i // 12
    row = i % 12
    x = 16 + col * col_w
    y = ly + row * 10
    d.text((x, y), f"{num} {place} \u2014 ", font=SANS(9), fill=INK)
    tw = d.textlength(f"{num} {place} \u2014 ", font=SANS(9))
    line = f"{title}. {body}"
    # shrink the line to fit the column, cutting at a word boundary
    fnt = SANS_R(9)
    if d.textlength(line, font=fnt) > col_w - tw - 8:
        words, acc = line.split(), ""
        for w in words:
            trial = (acc + " " + w).strip()
            if d.textlength(trial, font=fnt) > col_w - tw - 14:
                break
            acc = trial
        line = acc + "\u2026"
    d.text((x + tw, y), line, font=fnt, fill=INK)

# ---------------------------------------------------------------- date check
dy = 964
d.rectangle([16, dy - 6, W - 16, dy + 38], outline=RED, width=2)
d.text((24, dy), "DATE CHECK", font=SANS(11), fill=RED)
excluded = ("NOT ON THIS PAGE \u2014 first reported before Friday: the "
            "Trump\u2013Xi\u2013Putin meeting itself \u2022 Anthropic's $83 IPO "
            "pricing \u2022 GTA VI's midnight unlock \u2022 the ICJ's Rohingya "
            "judgment \u2022 the Houthi strike on Riyadh's PIF tower \u2022 "
            "the US\u2013Venezuela military deal \u2022 the EU's \u20ac45bn "
            "Ukraine loan proposal \u2022 Fiji's drought declaration \u2022 "
            "Han Duck-soo's acquittal \u2022 the Crimean Bridge attack \u2022 "
            "the Van Gogh $190.4m sale \u2022 Australia's West Bank sanctions.")
headline(d, 24, dy + 14, excluded, SANS_R(9), W - 48, max_lines=2)

# --------------------------------------------------------------------- footer
d.text((16, 1006), "Every story here happened, or was first reported, on "
       "Friday 20 November 2026. Disputed claims are attributed, not stated "
       "as fact. Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, UNEP, "
       "UKMTO. Original drawings.", font=SANS_R(8), fill=FAINT)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size)

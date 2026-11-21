#!/usr/bin/env python3
"""V3 builder: THE WORLD ON ONE MAP.

Friday 20 November 2026 as a world map: 12 numbered pins mark where the
day's biggest stories happened, a legend says what each one is, then 12
briefs and 12 more headlines. Flat colours, one focal point, nothing
truncated. Draws entry.png at 1024x1024 with PIL.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 16  # outer margin

PAPER = (247, 241, 222)
INK = (26, 26, 26)
RED = (160, 30, 34)
NAVY = (31, 58, 95)
TEAL = (18, 90, 86)
GOLD = (176, 124, 30)
SEA = (216, 230, 236)
LAND = (233, 223, 199)
LAND_LINE = (150, 128, 92)
GRID = (196, 208, 216)
SOFT = (120, 112, 96)
WHITE = (255, 255, 255)
CARD = (255, 252, 244)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_TITLE = font("DejaVuSans-Bold.ttf", 44)
F_SUB = font("DejaVuSans.ttf", 14)
F_SECT = font("DejaVuSans-Bold.ttf", 19)
F_SECT_R = font("DejaVuSans.ttf", 11)
F_STAT_N = font("DejaVuSans-Bold.ttf", 24)
F_STAT_L = font("DejaVuSans-Bold.ttf", 9)
F_PIN = font("DejaVuSans-Bold.ttf", 12)
F_LEG_H = font("DejaVuSans-Bold.ttf", 10)
F_LEG_C = font("DejaVuSans.ttf", 10)
F_LINE = font("DejaVuSans.ttf", 11)
F_LINE_B = font("DejaVuSans-Bold.ttf", 11)
F_DC = font("DejaVuSans.ttf", 10)
F_DC_B = font("DejaVuSans-Bold.ttf", 10)
F_FOOT = font("DejaVuSans.ttf", 9)
F_MAP_LBL = font("DejaVuSans-Bold.ttf", 9)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- continents
# Simplified lon/lat outlines, equirectangular. Schematic, not survey-grade.

NORTH_AMERICA = [
    (-168, 66), (-160, 71), (-150, 70), (-140, 70), (-130, 70), (-120, 69),
    (-110, 68), (-100, 68), (-90, 66), (-85, 66), (-80, 63), (-76, 62),
    (-70, 62), (-65, 60), (-60, 55), (-55, 52), (-55, 47), (-60, 47),
    (-66, 45), (-70, 42), (-74, 40), (-76, 35), (-80, 32), (-81, 26),
    (-84, 30), (-89, 30), (-93, 30), (-97, 26), (-97, 22), (-94, 19),
    (-91, 19), (-90, 21), (-87, 21), (-88, 16), (-86, 12), (-83, 9),
    (-80, 8), (-83, 10), (-86, 12), (-90, 14), (-94, 16), (-97, 16),
    (-102, 18), (-105, 20), (-108, 22), (-111, 24), (-114, 28), (-117, 33),
    (-121, 37), (-124, 42), (-124, 48), (-127, 50), (-130, 54), (-135, 58),
    (-140, 60), (-145, 60), (-152, 60), (-158, 58), (-165, 60),
]

GREENLAND = [
    (-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70),
    (-20, 74), (-25, 78), (-35, 80), (-45, 80), (-55, 78), (-60, 74),
    (-58, 70),
]

SOUTH_AMERICA = [
    (-79, 9), (-77, 7), (-75, 10), (-72, 11), (-70, 12), (-66, 11),
    (-64, 10), (-62, 9), (-60, 8), (-57, 6), (-54, 4), (-52, 5),
    (-50, 2), (-50, 0), (-48, -3), (-44, -3), (-40, -5), (-37, -7),
    (-35, -9), (-35, -12), (-38, -15), (-40, -20), (-41, -23), (-46, -26),
    (-50, -30), (-54, -34), (-58, -38), (-62, -41), (-66, -45), (-68, -50),
    (-70, -54), (-72, -54), (-74, -50), (-74, -45), (-73, -40), (-72, -35),
    (-71, -30), (-70, -25), (-70, -20), (-72, -18), (-75, -15), (-78, -10),
    (-80, -6), (-81, -3), (-80, 0), (-79, 3), (-79, 7),
]

AFRICA = [
    (-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
    (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (12, 2),
    (13, -1), (12, -5), (13, -10), (12, -15), (13, -18), (14, -22),
    (16, -26), (18, -30), (20, -35), (26, -34), (31, -30), (33, -26),
    (35, -22), (36, -18), (40, -15), (41, -11), (40, -5), (42, 0),
    (44, 2), (46, 5), (48, 10), (51, 11), (50, 12), (46, 11), (43, 12),
    (40, 15), (38, 18), (36, 22), (34, 27), (32, 31), (30, 32), (25, 32),
    (20, 32), (15, 32), (10, 33), (5, 35),
]

EURASIA = [
    (-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
    (0, 51), (3, 53), (5, 53), (8, 55), (8, 57), (10, 59), (12, 61),
    (15, 63), (18, 66), (21, 69), (25, 71), (30, 70), (35, 68), (40, 67),
    (45, 68), (50, 69), (55, 69), (60, 69), (65, 70), (70, 71), (75, 72),
    (80, 73), (85, 74), (90, 75), (95, 76), (100, 77), (105, 78),
    (110, 76), (115, 73), (120, 72), (125, 71), (130, 72), (135, 71),
    (140, 72), (145, 72), (150, 70), (155, 69), (160, 68), (165, 66),
    (170, 66), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
    (156, 50), (150, 48), (145, 45), (142, 44), (140, 40), (138, 38),
    (135, 35), (132, 35), (130, 38), (127, 40), (124, 40), (122, 38),
    (120, 35), (122, 32), (120, 28), (118, 25), (115, 23), (112, 22),
    (109, 20), (108, 18), (106, 16), (105, 10), (103, 8), (101, 6),
    (100, 5), (99, 7), (98, 10), (97, 14), (94, 17), (92, 20), (90, 22),
    (88, 22), (86, 20), (84, 19), (82, 17), (80, 15), (78, 13), (76, 10),
    (74, 8), (73, 15), (70, 20), (68, 22), (66, 24), (64, 25), (62, 25),
    (60, 25), (58, 26), (56, 27), (54, 27), (52, 26), (50, 27), (48, 29),
    (48, 30), (44, 30), (42, 29), (40, 28), (38, 28), (36, 26), (35, 28),
    (34, 29), (32, 31), (30, 31), (28, 32), (26, 34), (24, 35), (22, 36),
    (20, 37), (18, 38), (16, 39), (14, 40), (12, 41), (10, 42), (8, 42),
    (6, 41), (4, 40), (2, 39), (0, 38), (-2, 37), (-4, 36), (-6, 36),
    (-8, 36),
]

AUSTRALIA = [
    (113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
    (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
    (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
    (140, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14),
    (122, -17), (118, -20), (114, -22),
]

UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-3, 50)]

JAPAN = [
    (130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
    (141, 39), (141, 41), (142, 43), (140, 44), (138, 42), (136, 39),
    (133, 36), (131, 33),
]

NEW_ZEALAND = [
    (167, -45), (170, -43), (173, -41), (175, -39), (177, -38), (175, -37),
    (173, -35), (172, -37), (169, -40), (167, -44),
]

MADAGASCAR = [
    (44, -16), (47, -15), (50, -17), (49, -20), (47, -24), (45, -25),
    (43, -22), (43, -18),
]

CONTINENTS = [
    NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
    AUSTRALIA, UK, JAPAN, NEW_ZEALAND, MADAGASCAR,
]

# Map frame (equirectangular, lon -180..180, lat 85..-60)
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 16, 196, 1008, 556


def project(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (85.0 - lat) / 145.0 * (MAP_Y1 - MAP_Y0)
    return x, y


# ------------------------------------------------------------------- stories
# (number, headline, short clause, lon, lat, badge offset dx, dy)
PINS = [
    (1, "Akvan hits Odisha", "300,000+ evacuated to shelters", 84.9, 19.3, 0, 0),
    (2, "COP31 reaches final day", "draft drops the $120bn figure", 30.7, 36.9, 0, 0),
    (3, "Anthropic ends day one up 17%", "closes $97.17 on an $83 offer", -74.0, 40.7, 0, 0),
    (4, "Leaders issue peace declaration", "Trump, Xi, Putin; no Ukraine mention", 114.1, 22.5, 0, 0),
    (5, "Senate rejects Iran war-powers bid", "fails 51-48, three Republicans yes", -77.0, 38.9, 24, 18),
    (6, "Phillips makes history with 118", "centuries in all formats vs India", 174.8, -41.3, 0, 0),
    (7, "GTA VI passes $2bn in a day", "$2.36bn, 24.6m copies, Metacritic 99", -80.2, 25.8, 0, 0),
    (8, "State subpoenas Nvidia over China chips", "days after Huang's exit", -122.0, 37.4, 0, 0),
    (9, "Russia's barrage hits Kyiv, spills into Poland", "400+ drones, 110 missiles, 8 killed", 30.5, 50.5, 0, 0),
    (10, "Europe agrees binding Ukraine guarantees", "after a ceasefire, US to monitor", 13.4, 52.5, 0, 0),
    (11, "Drought emergency in Tonga", "schools close early on Friday", -175.2, -21.1, 0, 0),
    (12, "Somalia orders UAE envoy out", "ambassador told to leave in three days", 45.3, 2.0, 0, 0),
]

BRIEFS = [
    (13, "Pete Rose pardoned", "banned for life for betting; pardoned after his death."),
    (14, "Japan inflation 2.2%", "core CPI stays above target; Nikkei plunges 4%."),
    (15, "S&P 500 -2.02%", "Nasdaq falls 2.2% as tech slides on Thursday."),
    (16, "Dow below 50,000", "the index gives up the milestone in the sell-off."),
    (17, "IEA warning", "the Iran conflict is a historic energy-security threat."),
    (18, "US blockade holds", "Navy blockade of Iranian shipping persists."),
    (19, "Hungary lifts veto", "EU accession talks with Ukraine can open at last."),
    (20, "Trump AI penalties", "president floats penalties for AI centres abroad."),
    (21, "Humans oversee military AI", "US and China agree people stay in charge."),
    (22, "Bukele registers", "El Salvador's president files to seek a third term."),
    (23, "Colombia strike warning", "president warns of state intervention."),
    (24, "Chinese chemicals fuel cartel", "US embassy says precursors feed Sinaloa."),
]

ALSO = [
    (25, "Saudi coalition intercepts 5 Houthi ballistic missiles and 1 cruise missile."),
    (26, "Venezuela TPS ruling takes effect Friday; about 1,800 could be freed."),
    (27, "Anthropic's $81bn offering closes Friday, plus a $26bn private placement."),
    (28, "Anthropic shares slide on day two after the record debut."),
    (29, "US charges a Russian over surveillance targeting Palantir staff."),
    (30, "New Zealand court: pay-equity reform violated women's rights."),
    (31, "Worldwide car-trafficking crackdown: 2,393 seizures, 688 arrests."),
    (32, "SpaceX chief denies throttling Starlink for Ukraine."),
    (33, "West urges Iran at IAEA to restart nuclear inspections."),
    (34, "GTA VI streams draw 132m hours watched."),
    (35, "Zelensky: NATO membership is Ukraine's strongest guarantee."),
    (36, "Trump keeps China limited to older AI chips."),
]

STATS = [
    ("300,000+", "AKVAN EVACUATED"),
    ("$97.17", "ANTHROPIC CLOSE, +17%"),
    ("118", "PHILLIPS, WELLINGTON"),
    ("51-48", "SENATE WAR-POWERS VOTE"),
    ("400+", "DRONES OVER KYIV"),
    ("$2.36bn", "GTA VI, DAY ONE"),
]

DATE_CHECK = (
    "DATE CHECK - reported before Friday, so not shown as Friday news: "
    "the Trump-Xi-Putin meeting itself \u00b7 Anthropic's $83 IPO pricing \u00b7 "
    "GTA VI's midnight unlock \u00b7 the ICJ's Rohingya judgment \u00b7 the Houthi "
    "strike on Riyadh's PIF tower \u00b7 the US-Venezuela military deal \u00b7 "
    "the EU's \u20ac45bn Ukraine loan proposal \u00b7 Fiji's drought declaration "
    "\u00b7 Han Duck-soo's acquittal \u00b7 the Crimean Bridge attack \u00b7 the Van "
    "Gogh $190.4m sale \u00b7 Australia's West Bank sanctions \u00b7 the "
    "Denmark-Greenland vote \u00b7 the Gaza tank raid ending \u00b7 the Genoa drone "
    "shutdown \u00b7 the Malawi protests \u00b7 the Hormuz 14-attacks count \u00b7 "
    "the Gaza peace-plan scorecard."
)

FOOTER = (
    "Sources: Reuters \u00b7 AP \u00b7 Bloomberg \u00b7 AFP \u00b7 BBC \u00b7 "
    "Al Jazeera \u00b7 UKMTO \u00b7 IEA \u00b7 Sensor Tower \u00b7 Metacritic "
    "\u2014 checked against Friday 20 November 2026."
)


# ------------------------------------------------------------------- drawing

def draw_masthead(d):
    d.rectangle([M, 10, W - M, 14], fill=RED)
    title = "THE WORLD IN ONE DAY"
    tw = text_w(d, title, F_TITLE)
    d.text(((W - tw) / 2, 22), title, font=F_TITLE, fill=INK)
    sub = "FRIDAY 20 NOVEMBER 2026  \u00b7  EVERY BIG STORY \u2014 AND WHERE IT HAPPENED"
    sw = text_w(d, sub, F_SUB)
    d.text(((W - sw) / 2, 74), sub, font=F_SUB, fill=NAVY)
    d.line([M, 98, W - M, 98], fill=INK, width=2)


def draw_stats(d):
    y0, y1 = 106, 162
    n = len(STATS)
    gap = 10
    bw = (W - 2 * M - (n - 1) * gap) // n
    for i, (num, label) in enumerate(STATS):
        x0 = M + i * (bw + gap)
        x1 = x0 + bw
        d.rectangle([x0, y0, x1, y1], fill=CARD, outline=INK, width=1)
        d.rectangle([x0, y0, x1, y0 + 3], fill=RED)
        nw = text_w(d, num, F_STAT_N)
        d.text(((x0 + x1 - nw) / 2, y0 + 10), num, font=F_STAT_N, fill=RED)
        lw = text_w(d, label, F_STAT_L)
        d.text(((x0 + x1 - lw) / 2, y0 + 40), label, font=F_STAT_L, fill=INK)


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=SEA, outline=INK, width=2)
    # graticule every 30 degrees
    for lon in range(-180, 181, 30):
        x, _ = project(lon, 85)
        d.line([x, MAP_Y0, x, MAP_Y1], fill=GRID, width=1)
    for lat in range(-60, 86, 30):
        _, y = project(-180, lat)
        d.line([MAP_X0, y, MAP_X1, y], fill=GRID, width=1)
    # continents
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    # ocean labels
    d.text(project(-150, 10), "PACIFIC", font=F_MAP_LBL, fill=(150, 168, 178))
    d.text(project(-38, -28), "ATLANTIC", font=F_MAP_LBL, fill=(150, 168, 178))
    d.text(project(88, -38), "INDIAN", font=F_MAP_LBL, fill=(150, 168, 178))
    # pins
    for num, _h, _c, lon, lat, dx, dy in PINS:
        px, py = project(lon, lat)
        bx, by = px + dx, py + dy
        if dx or dy:
            d.line([px, py, bx, by], fill=RED, width=2)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=RED, outline=WHITE, width=2)
        label = str(num)
        lw = text_w(d, label, F_PIN)
        d.text((bx - lw / 2, by - 8), label, font=F_PIN, fill=WHITE)


def draw_section_head(d, y, title, right):
    d.text((M, y), title, font=F_SECT, fill=INK)
    rw = text_w(d, right, F_SECT_R)
    d.text((W - M - rw, y + 4), right, font=F_SECT_R, fill=SOFT)
    d.line([M, y + 24, W - M, y + 24], fill=INK, width=1)
    return y + 30


def draw_legend(d, y0):
    col_w, gap, row_h = 322, 13, 24
    for i, (num, head, clause, _lon, _lat, _dx, _dy) in enumerate(PINS):
        col, row = i % 3, i // 3
        x = M + col * (col_w + gap)
        y = y0 + row * row_h
        d.text((x, y), str(num), font=F_LEG_H, fill=RED)
        text = head + " \u2014 " + clause
        lines = wrap(d, text, F_LEG_C, col_w - 20)
        for j, line in enumerate(lines[:2]):
            d.text((x + 20, y + j * 12), line, font=F_LEG_C, fill=INK)
        if len(lines) > 2:
            print("LEGEND OVERFLOW", num, lines)


def draw_numbered_line(d, x, y, num, head, clause, max_w, bold_head=True):
    num_s = str(num) + " "
    nw = text_w(d, num_s, F_LINE_B)
    d.text((x, y), num_s, font=F_LINE_B, fill=RED)
    hw = text_w(d, head, F_LINE_B)
    d.text((x + nw, y), head, font=F_LINE_B, fill=INK)
    rest = " \u2014 " + clause if clause else ""
    d.text((x + nw + hw, y), rest, font=F_LINE, fill=INK)
    total = nw + hw + text_w(d, rest, F_LINE)
    if total > max_w:
        print("LINE OVERFLOW", num, round(total), "max", max_w)


def draw_briefs(d, y0):
    col_w, gap, row_h = 480, 32, 12
    for i, (num, head, clause) in enumerate(BRIEFS):
        col, row = i % 2, i // 2
        x = M + col * (col_w + gap)
        draw_numbered_line(d, x, y0 + row * row_h, num, head, clause, col_w)


def draw_also(d, y0):
    col_w, gap, row_h = 480, 32, 12
    for i, (num, head) in enumerate(ALSO):
        col, row = i % 2, i // 2
        x = M + col * (col_w + gap)
        draw_numbered_line(d, x, y0 + row * row_h, num, head, "", col_w)


def draw_date_check(d, y0, y1):
    d.rectangle([M, y0, W - M, y1], fill=(238, 228, 205), outline=RED, width=1)
    d.text((M + 12, y0 + 6), "DATE CHECK", font=F_DC_B, fill=RED)
    lines = wrap(d, DATE_CHECK, F_DC, W - 2 * M - 24)
    for j, line in enumerate(lines):
        d.text((M + 12, y0 + 24 + j * 13), line, font=F_DC, fill=INK)
    if len(lines) > 4:
        print("DATE CHECK LINES:", len(lines))


def draw_footer(d, y0):
    lines = wrap(d, FOOTER, F_FOOT, W - 2 * M)
    for j, line in enumerate(lines):
        d.text((M, y0 + j * 11), line, font=F_FOOT, fill=SOFT)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_section_head(d, 168, "THE WORLD ON ONE MAP", "12 STORIES \u00b7 12 PLACES")
    draw_map(d)
    draw_section_head(d, 564, "WHERE EACH PIN POINTS", "THE 12 BIGGEST STORIES")
    draw_legend(d, 594)
    draw_section_head(d, 698, "THE DAY IN BRIEF", "13\u201324")
    draw_briefs(d, 728)
    draw_section_head(d, 808, "ALSO ON FRIDAY", "25\u201336")
    draw_also(d, 838)
    draw_date_check(d, 918, 992)
    draw_footer(d, 1000)
    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build()

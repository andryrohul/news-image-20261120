#!/usr/bin/env python3
"""Build entry.png for news-image-20261120.

A one-page newspaper front page: "THE WORLD IN ONE DAY" for Friday
20 November 2026. Lead story: the Shenzhen trilateral summit. Below it,
eight region panels carry 27 more date-checked stories, one per country
or market, each with a short headline and one factual line.

Run:  python3 build_image.py   (writes entry.png, 1024x1024, < 1 MiB)
The submitted program (main.py) only copies entry.png; it never runs
this builder, so Pillow is needed here on the build machine only.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (24, 24, 24)
GREY = (84, 84, 84)
RED = (178, 34, 34)
NAVY = (18, 42, 76)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 52)
F_DATE = font("DejaVuSans-Bold.ttf", 21)
F_KICKER = font("DejaVuSans-Bold.ttf", 16)
F_LEAD = font("DejaVuSerif-Bold.ttf", 33)
F_LEAD_SUB = font("DejaVuSans.ttf", 17)
F_ALSO = font("DejaVuSans-Bold.ttf", 16)
F_REGION = font("DejaVuSans-Bold.ttf", 17)
F_HEAD = font("DejaVuSans-Bold.ttf", 16)
F_DETAIL = font("DejaVuSans.ttf", 13)
F_FOOT = font("DejaVuSans.ttf", 13)

LEAD_KICKER = "THE SUMMIT  •  SHENZHEN, CHINA"
LEAD_HEAD = "TRUMP, XI & PUTIN SIGN\nPEACE DECLARATION"
LEAD_SUB = ("First-ever trilateral summit ends with a four-point pact: "
            "UN reform, energy cooperation, official immunity and a "
            "nuclear-risk dialogue. Ukraine topped the agenda.")
ALSO_HEAD = "ALSO: UN court finds Myanmar guilty of Rohingya genocide"
ALSO_SUB = "The Hague, 9–6: the first genocide finding against a state."

# (region, colour, [(country, headline, detail), ...])
REGIONS = [
    ("NORTH AMERICA", (31, 78, 121), [
        ("USA", "Anthropic soars on Nasdaq debut",
         "Shares close +17% at ~$97 after an $81bn IPO."),
        ("USA", "Trump pardons baseball legend Pete Rose",
         "Posthumous pardon for the late hits leader."),
        ("USA", "Senate rejects Iran war-powers vote",
         "Resolution fails 51–48; three Republicans back it."),
    ]),
    ("LATIN AMERICA", (46, 125, 50), [
        ("VENEZUELA", "Caracas signs military deal with US",
         "Pact months after Maduro's removal from power."),
        ("EL SALVADOR", "Bukele to seek a third term",
         "President registers for the 2027 election."),
        ("APEC", "Mexico, Chile, Peru join trade pact",
         "Shenzhen declaration backs open Pacific trade."),
    ]),
    ("EUROPE", (106, 27, 154), [
        ("GERMANY", "Europe ready for Russia talks",
         "Berlin allies agree a united Ukraine position."),
        ("UK & NORWAY", "£100m for Ukraine naval craft",
         "Joint programme via the Maritime Capability Coalition."),
        ("ITALY", "Genoa airport halted by drones",
         "Flights suspended after unidentified drones seen."),
    ]),
    ("MIDDLE EAST", (183, 28, 28), [
        ("SAUDI ARABIA", "Houthi missiles hit Riyadh tower",
         "PIF tower windows blown out; airport targeted too."),
        ("SAUDI ARABIA", "New Houthi missile intercepted",
         "Friday strike on the south stopped; Sanaa hit."),
        ("GAZA", "Israel ends Gaza tank raid",
         "Tunnel operation beyond the ceasefire line done."),
    ]),
    ("AFRICA", (230, 81, 0), [
        ("SENEGAL", "Dozens missing as migrant boat sinks",
         "Capsize off Yenne, on the route to the Canaries."),
        ("MALAWI", "Fuel crisis turns violent",
         "Shortages bring chaotic queues and clashes."),
        ("DR CONGO", "Ebola outbreak tops 10,600 cases",
         "5,198 dead; contact tracing falls short."),
    ]),
    ("ASIA–PACIFIC", (0, 105, 92), [
        ("CHINA", "APEC adopts Shenzhen Outlook",
         "Trade, data and AI-risk agenda agreed."),
        ("JAPAN", "Core inflation hits 2.2% high",
         "Highest this year as energy costs climb."),
        ("INDONESIA", "Parliament passes asset-seizure bill",
         "Forfeiture without a prior conviction approved."),
    ]),
    ("SOUTH ASIA", (141, 110, 0), [
        ("INDIA", "80,000 evacuated as Cyclone Dana nears",
         "Storm approaches the east coast."),
        ("NEW ZEALAND", "Nicholls 113* rescues NZ vs India",
         "Black Caps 243/5 on day one in Wellington."),
        ("QATAR", "Rising Stars Asia Cup begins",
         "Eight teams open the tournament in Doha."),
    ]),
    ("MARKETS, TECH & SPORT", (55, 71, 79), [
        ("MARKETS", "Stocks slide in global AI sell-off",
         "S&P 500 −2.0%, Dow under 50,000, Nikkei −4.7%."),
        ("CLIMATE", "COP31 closes without fossil phase-out",
         "Antalya draft drops the phase-out call."),
        ("ENERGY", "AI data centres need $3.9 trillion",
         "IEA: power, not chips, is the bottleneck to 2030."),
    ]),
]


def wrap(draw, text, fnt, width):
    """Wrap text to fit width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
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


def draw_flag_stripes(draw, x, y, w, h):
    """Three flag stripes for the lead illustration: US, China, Russia."""
    third = w // 3
    # USA: red/white stripes with blue canton
    for i in range(7):
        draw.rectangle([x, y + i * h // 7, x + third, y + (i + 1) * h // 7],
                       fill=(178, 34, 34) if i % 2 == 0 else (255, 255, 255))
    draw.rectangle([x, y, x + third * 2 // 3, y + h * 4 // 7], fill=(18, 42, 76))
    # China: red field, yellow stars (kept inside the stripe)
    cx = x + third
    draw.rectangle([cx, y, cx + third, y + h], fill=(222, 41, 16))
    for sx, sy, r in [(cx + 22, y + 11, 6), (cx + 42, y + 8, 4),
                      (cx + 48, y + 20, 4), (cx + 42, y + 30, 4),
                      (cx + 26, y + 29, 4)]:
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 215, 0))
    # Russia: white / blue / red horizontal
    rx = x + 2 * third
    for i, col in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([rx, y + i * h // 3, rx + third, y + (i + 1) * h // 3],
                       fill=col)


def draw_lead_art(draw, x, y, w, h):
    """Skyline + globe + flag stripes for the summit story."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 42, 76))
    # skyline
    base = y + h
    buildings = [(0, 0.55), (0.12, 0.72), (0.24, 0.48), (0.38, 0.66),
                 (0.52, 0.42), (0.66, 0.60), (0.78, 0.50), (0.90, 0.68)]
    for bx, bh in buildings:
        bw = w * 0.11
        draw.rectangle([x + w * bx, base - h * bh, x + w * bx + bw, base],
                       fill=(38, 68, 110))
        for wy in range(3):
            for wx in range(2):
                draw.rectangle(
                    [x + w * bx + 6 + wx * 14, base - h * bh + 8 + wy * 16,
                     x + w * bx + 14 + wx * 14, base - h * bh + 18 + wy * 16],
                    fill=(255, 214, 90))
    # globe
    gx, gy, gr = x + w - 78, y + 52, 34
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 140, 190),
                 outline=(255, 255, 255), width=2)
    draw.ellipse([gx - gr // 2, gy - gr, gx + gr // 2, gy + gr],
                 outline=(255, 255, 255), width=1)
    draw.line([gx - gr, gy, gx + gr, gy], fill=(255, 255, 255), width=1)
    draw_flag_stripes(draw, x + 14, y + h - 52, w - 28, 38)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.text((24, 14), "THE WORLD IN ONE DAY", font=F_TITLE, fill=INK)
    d.rectangle([24, 84, W - 24, 88], fill=RED)
    d.text((24, 94), "FRIDAY  20  NOVEMBER  2026", font=F_DATE, fill=RED)
    right = "26 STORIES  •  8 REGIONS  •  EVERY CONTINENT"
    d.text((W - 24 - d.textlength(right, font=F_DATE), 94), right,
           font=F_DATE, fill=INK)

    # ---- lead story ----
    ly, lh = 126, 172
    d.rectangle([24, ly, W - 24, ly + lh], outline=INK, width=2)
    d.text((40, ly + 10), LEAD_KICKER, font=F_KICKER, fill=RED)
    d.multiline_text((40, ly + 34), LEAD_HEAD, font=F_LEAD, fill=INK,
                     spacing=2)
    sub = wrap(d, LEAD_SUB, F_LEAD_SUB, 580)
    sy = ly + 110
    for line in sub[:3]:
        d.text((40, sy), line, font=F_LEAD_SUB, fill=GREY)
        sy += 20
    # lead art on the right
    draw_lead_art(d, 636, ly + 8, 352, lh - 16)
    # also line under lead
    ay = ly + lh + 8
    d.text((40, ay), ALSO_HEAD, font=F_ALSO, fill=INK)
    d.text((40, ay + 22), ALSO_SUB, font=F_LEAD_SUB, fill=GREY)

    # ---- region grid: 2 columns x 4 rows, 3 stories per box ----
    gx, gy = 24, 356
    bw, bh, gap = 488, 152, 8
    for i, (name, colour, stories) in enumerate(REGIONS):
        col, row = i % 2, i // 2
        x = gx + col * (bw + gap)
        y = gy + row * (bh + gap)
        d.rectangle([x, y, x + bw, y + bh], outline=(180, 172, 156), width=1)
        d.rectangle([x, y, x + bw, y + 28], fill=colour)
        d.text((x + 10, y + 5), name, font=F_REGION, fill=(255, 255, 255))
        n = str(len(stories))
        d.text((x + bw - 10 - d.textlength(n, font=F_REGION), y + 5), n,
               font=F_REGION, fill=(255, 255, 255))
        sy = y + 36
        for country, head, detail in stories:
            line = country + " — " + head
            while d.textlength(line, font=F_HEAD) > bw - 20 and len(line) > 10:
                line = line[:-4].rstrip() + "…"
            d.text((x + 10, sy), line, font=F_HEAD, fill=INK)
            sy += 19
            d.text((x + 10, sy), detail, font=F_DETAIL, fill=GREY)
            sy += 18

    # ---- footer ----
    fy = 356 + 4 * bh + 3 * gap + 8
    d.rectangle([24, fy, W - 24, fy + 1], fill=(180, 172, 156))
    foot = ("Sources: Reuters, BBC, AP, Le Monde, APEC, IEA, ICJ  •  "
            "Events of 20 Nov 2026, or first reported that day.")
    d.text((24, fy + 8), foot, font=F_FOOT, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()

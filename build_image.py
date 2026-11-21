#!/usr/bin/env python3
"""Build V4 of the news-image-20261120 entry: 'The World in One Day' as a
24-hour clock. V2's winning clock structure + V3's date-verified stories,
now more colourful and with a drawn picture for every lead story.

Layout (1024x1024): colourful header + six stat pills, big clock dial with
12 colour-coded story dots, six drawn picture cards, six mini-cards for the
other six leads, 24 one-line stories, a DATE CHECK strip, sources footer.
Deterministic: no randomness, no timestamps, no network. Writes entry.png
next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

WARNINGS = []


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fnt, max_w, where):
    """Return lines that fit max_w; warn if the text had to be cut."""
    lines = wrap(draw, text, fnt, max_w)
    if draw.textlength(text, font=fnt) > max_w and len(lines) > 1:
        pass
    return lines


def mix(hexcol, white_frac):
    """Lighten a hex colour toward white; returns an (r, g, b) tuple."""
    c = hexcol.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return (int(r + (255 - r) * white_frac),
            int(g + (255 - g) * white_frac),
            int(b + (255 - b) * white_frac))


def check_fit(draw, text, fnt, max_w, where):
    if draw.textlength(text, font=fnt) > max_w:
        WARNINGS.append("%s overflow: %r" % (where, text))


# ---------------------------------------------------------------- palette
INK = (26, 32, 54)
NAVY = (22, 34, 77)
PAPER = (255, 249, 236)
GREY = (90, 96, 112)
LIGHT_LINE = (226, 220, 205)
GREEN_STRIP = (27, 122, 67)

# 12 lead stories: (number, colour, clock hour, title, body)
LEADS = [
    (1, "#0E7C7B", 1, "Siklon Akvan hantam Odisha",
     "300.000+ warga dievakuasi di Odisha"),
    (2, "#2E9E44", 3, "Hari terakhir COP31 di Antalya",
     "Draf akhir hapus angka $120 miliar"),
    (3, "#E8590C", 5, "Anthropic +17% di hari pertama",
     "Tutup $97,17 dari tawaran $83"),
    (4, "#E67700", 7, "Deklarasi damai Shenzhen",
     "Trump, Xi, Putin sepakati deklarasi"),
    (5, "#1864AB", 9, "Senat tolak perang Iran 51-48",
     "Resolusi batasi perang Iran ditolak"),
    (6, "#7048E8", 11, "Phillips 118, Wellington",
     "Century bersejarah di Wellington"),
    (7, "#E64980", 13, "GTA VI: $2,36 miliar sehari",
     "Rekor peluncuran game terbesar"),
    (8, "#5C940D", 15, "Nvidia disomasi California",
     "Jaksa persoalkan chip untuk Tiongkok"),
    (9, "#C92A2A", 17, "Rusia gempur Kyiv: 400+ drone",
     "110 rudal, 8 tewas, 2 jatuh di Polandia"),
    (10, "#1971C2", 19, "Jaminan keamanan Ukraina",
     "Eropa sepakati jaminan mengikat Kyiv"),
    (11, "#1098AD", 21, "Tonga darurat kekeringan",
     "Kekeringan parah, sekolah tutup Jumat"),
    (12, "#F08C00", 23, "Somalia usir duta besar UEA",
     "Duta besar UEA diberi 3 hari pergi"),
]

# which leads get a drawn picture card (number -> picture fn name)
PICTURE_LEADS = {1: "cyclone", 2: "coast", 3: "chart",
                 5: "dome", 7: "skyline", 9: "barrage"}

# the other six leads become mini-cards (number -> two-line body)
MINI_BODIES = {
    4: "Trump, Xi dan Putin sepakati deklarasi damai tanpa menyebut Ukraina.",
    6: "Century bersejarah untuk Selandia Baru di Wellington.",
    8: "Jaksa California persoalkan penjualan chip untuk Tiongkok.",
    10: "Eropa sepakati jaminan keamanan yang mengikat untuk Kyiv.",
    11: "Kekeringan parah melanda, sekolah-sekolah tutup hari Jumat.",
    12: "Duta besar Uni Emirat Arab diberi tiga hari untuk pergi.",
}

# stories 13-36, headline only
ALSO = [
    "Pete Rose resmi diampuni",
    "Inflasi inti Jepang 2,2%; Nikkei anjlok 4% di bawah 57.000",
    "S&P 500 turun 2,02%",
    "Dow Jones jatuh di bawah 50.000",
    "IEA: konflik Iran ancaman energi bersejarah",
    "Blokade AS atas kapal Iran berlanjut",
    "Hongaria cabut veto Ukraina masuk UE",
    "Trump ancam denda pusat data AI",
    "AS-Tiongkok: manusia awasi AI militer",
    "Bukele daftar cari masa jabatan ketiga",
    "Peringatan mogok meluas di Kolombia",
    "Kedubes AS: bahan kimia Tiongkok danai kartel Sinaloa",
    "Koalisi Saudi cegat 5 rudal balistik + 1 rudal jelajah Houthi",
    "Putusan TPS Venezuela berlaku hari Jumat",
    "Penawaran $81 miliar Anthropic tutup Jumat + penempatan $26 miliar",
    "Saham Anthropic merosot di hari kedua",
    "AS dakwa warga Rusia soal pengawasan Palantir",
    "Pengadilan NZ: reformasi upah langgar hak perempuan",
    "Razia mobil curian sedunia: 2.393 sitaan, 688 ditangkap",
    "Bos SpaceX bantah perlambat Starlink",
    "Barat desak Iran di inspeksi IAEA",
    "GTA VI ditonton 132 juta jam",
    "Zelensky: NATO jaminan terkuat",
    "Trump batasi Tiongkok ke chip AI lama",
]

STATS = [
    ("300rb+ dievakuasi", "#0E7C7B"),
    ("$97,17  +17%", "#E8590C"),
    ("118 Phillips", "#7048E8"),
    ("51-48 Senat", "#1864AB"),
    ("400+ drone Kyiv", "#C92A2A"),
    ("$2,36 M GTA VI", "#E64980"),
]

DATE_CHECK = ("DATE CHECK - Bukan berita Jumat 20 Nov: Bukele mulai masa jabatan "
              "ketiga (baru daftar, 19 Nov) - pemungutan suara Denmark-Greenland "
              "(19 Nov) - berakhirnya serangan tank Gaza (19 Nov) - penutupan "
              "drone Genoa (19 Nov) - protes Malawi (17 Nov) - 14 serangan "
              "Hormuz (dilaporkan 19 Nov) - skor perdamaian Gaza 4/26 (19 Nov) - "
              "hitung mundur Ebola Kenya (12 Nov).")


# ------------------------------------------------------------ drawn pictures
def pic_cyclone(d, x0, y0, w, h):
    """Spiral storm over the sea."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(214, 235, 245))
    d.rectangle([x0, y0 + int(h * 0.62), x0 + w, y0 + h], fill=(42, 157, 143))
    cx, cy = x0 + w // 2, y0 + int(h * 0.45)
    for r, col in ((34, (14, 124, 123)), (26, (25, 90, 130)),
                   (18, (42, 157, 143)), (10, (255, 255, 255))):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=4)
    for i in range(6):
        rx = x0 + 14 + i * 40
        d.line([rx, y0 + 8, rx - 8, y0 + 20], fill=(255, 255, 255), width=2)
    d.ellipse([x0 + 10, y0 + 6, x0 + 46, y0 + 20], fill=(255, 255, 255))
    d.ellipse([x0 + w - 52, y0 + 12, x0 + w - 12, y0 + 24],
              fill=(255, 255, 255))


def pic_coast(d, x0, y0, w, h):
    """Antalya coast at sunset."""
    d.rectangle([x0, y0, x0 + w, y0 + int(h * 0.55)], fill=(255, 214, 130))
    d.ellipse([x0 + w - 78, y0 + 6, x0 + w - 38, y0 + 46], fill=(232, 89, 12))
    d.rectangle([x0, y0 + int(h * 0.55), x0 + w, y0 + h], fill=(25, 113, 194))
    d.polygon([(x0, y0 + int(h * 0.55)), (x0 + 70, y0 + int(h * 0.30)),
               (x0 + 150, y0 + int(h * 0.55))], fill=(46, 158, 68))
    for yy in (int(h * 0.66), int(h * 0.80)):
        for xx in range(0, w, 34):
            d.arc([x0 + xx, y0 + yy, x0 + xx + 26, y0 + yy + 12],
                  180, 360, fill=(255, 255, 255), width=3)


def pic_chart(d, x0, y0, w, h):
    """Rising candlestick chart, +17%."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(255, 255, 255))
    for gy in range(1, 4):
        yy = y0 + gy * h // 4
        d.line([x0 + 8, yy, x0 + w - 8, yy], fill=(233, 236, 239), width=1)
    candles = [(22, 46, 30), (62, 40, 26), (102, 34, 22),
               (142, 28, 18), (182, 20, 14)]
    for cx, top, body in candles:
        d.line([x0 + cx + 9, y0 + top - 6, x0 + cx + 9, y0 + top + body + 6],
               fill=(27, 122, 67), width=2)
        d.rectangle([x0 + cx, y0 + top, x0 + cx + 18, y0 + top + body],
                    fill=(46, 158, 68))
    d.line([x0 + 16, y0 + h - 12, x0 + w - 30, y0 + 10],
           fill=(232, 89, 12), width=3)
    d.polygon([(x0 + w - 30, y0 + 10), (x0 + w - 44, y0 + 12),
               (x0 + w - 32, y0 + 24)], fill=(232, 89, 12))
    d.text((x0 + w - 62, y0 + h - 22), "+17%", font=font(13, True),
           fill=(27, 122, 67))


def pic_skyline(d, x0, y0, w, h):
    """Vice City style sunset skyline with palms."""
    bands = [(255, 159, 67), (230, 73, 128), (112, 72, 232)]
    for i, col in enumerate(bands):
        d.rectangle([x0, y0 + i * h // 3, x0 + w, y0 + (i + 1) * h // 3],
                    fill=col)
    d.ellipse([x0 + w // 2 - 16, y0 + 6, x0 + w // 2 + 16, y0 + 38],
              fill=(255, 224, 102))
    base = y0 + h
    for bx, bw, bh in ((0, 34, 26), (40, 26, 38), (72, 40, 22),
                       (118, 30, 42), (154, 36, 28), (196, 30, 36),
                       (232, 40, 24)):
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(26, 32, 54))
    for px in (108, 216):
        d.line([x0 + px, base - 34, x0 + px, base - 52],
               fill=(26, 32, 54), width=3)
        for ang in (200, 250, 290, 330):
            import math
            ex = x0 + px + int(14 * math.cos(math.radians(ang)))
            ey = base - 52 + int(10 * math.sin(math.radians(ang)))
            d.line([x0 + px, base - 52, ex, ey], fill=(26, 32, 54), width=2)


def pic_barrage(d, x0, y0, w, h):
    """Night sky, explosions and drone trails over Kyiv."""
    import math
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(27, 42, 74))
    for sx, sy in ((30, 12), (90, 22), (170, 10), (230, 26), (130, 30)):
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2],
                  fill=(255, 255, 255))
    for ex, ey, r in ((70, 34, 16), (200, 28, 20)):
        for k in range(8):
            ang = math.radians(k * 45 + 10)
            d.line([x0 + ex, y0 + ey,
                    x0 + ex + int(r * math.cos(ang)),
                    y0 + ey + int(r * math.sin(ang))],
                   fill=(255, 159, 67), width=3)
        d.ellipse([x0 + ex - 6, y0 + ey - 6, x0 + ex + 6, y0 + ey + 6],
                  fill=(255, 224, 102))
    for dx in (40, 120, 190, 250):
        d.line([x0 + dx, y0 + h - 8, x0 + dx + 12, y0 + h - 20],
               fill=(255, 255, 255), width=1)
        d.ellipse([x0 + dx + 10, y0 + h - 22, x0 + dx + 14, y0 + h - 18],
                  fill=(255, 255, 255))
    d.rectangle([x0, y0 + h - 6, x0 + w, y0 + h], fill=(16, 24, 46))


def pic_dome(d, x0, y0, w, h):
    """US Capitol dome with the 51-48 vote bars."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(208, 235, 255))
    cx = x0 + w // 2
    d.rectangle([cx - 52, y0 + h - 26, cx + 52, y0 + h - 14],
                fill=(255, 255, 255))
    for colx in range(cx - 44, cx + 45, 16):
        d.rectangle([colx, y0 + h - 26, colx + 6, y0 + h - 14],
                    fill=(186, 205, 224))
    d.pieslice([cx - 34, y0 + 8, cx + 34, y0 + h - 20], 180, 360,
               fill=(255, 255, 255))
    d.rectangle([cx - 3, y0 + 2, cx + 3, y0 + 12], fill=(90, 96, 112))
    d.rectangle([cx + 3, y0 + 2, cx + 15, y0 + 9], fill=(201, 42, 42))
    d.rectangle([x0 + 10, y0 + h - 12, x0 + 10 + 104, y0 + h - 6],
                fill=(24, 100, 171))
    d.rectangle([x0 + 10, y0 + h - 5, x0 + 10 + 98, y0 + h - 1],
                fill=(201, 42, 42))
    d.text((x0 + 118, y0 + h - 13), "51-48", font=font(11, True),
           fill=(26, 32, 54))


PICTURES = {"cyclone": pic_cyclone, "coast": pic_coast, "chart": pic_chart,
            "skyline": pic_skyline, "barrage": pic_barrage, "dome": pic_dome}


# ------------------------------------------------------------------- layout
import math


def draw_header(d):
    d.rectangle([0, 0, W, 58], fill=NAVY)
    d.text((16, 12), "THE WORLD IN ONE DAY", font=font(30, True),
           fill=(255, 255, 255))
    d.text((1008, 20), "JUMAT, 20 NOVEMBER 2026", font=font(14, True),
           fill=(255, 212, 59), anchor="ra")
    rainbow = [(201, 42, 42), (232, 89, 12), (247, 183, 0),
               (46, 158, 68), (25, 113, 194), (112, 72, 232)]
    seg = W // 6
    for i, col in enumerate(rainbow):
        d.rectangle([i * seg, 58, (i + 1) * seg, 64], fill=col)


def draw_stats(d):
    x = 16
    pw, gap = 158, 8
    for label, col in STATS:
        d.rounded_rectangle([x, 70, x + pw, 96], radius=13, fill=col)
        check_fit(d, label, font(12, True), pw - 12, "stat %r" % label)
        d.text((x + pw // 2, 83), label, font=font(12, True),
               fill=(255, 255, 255), anchor="mm")
        x += pw + gap


def draw_clock(d):
    cx, cy, r_out, r_in = 219, 275, 172, 138
    for num, col, hour, _t, _b in LEADS:
        start = 30 * ((hour - 1) // 2) - 90
        d.pieslice([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
                   start, start + 30, fill=mix(col, 0.72))
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
              outline=NAVY, width=3)
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              fill=(255, 255, 255), outline=NAVY, width=2)
    for num, col, hour, _t, _b in LEADS:
        ang = math.radians(hour / 24.0 * 360 - 90)
        dx = cx + int(155 * math.cos(ang))
        dy = cy + int(155 * math.sin(ang))
        d.ellipse([dx - 16, dy - 16, dx + 16, dy + 16], fill=col,
                  outline=(255, 255, 255), width=2)
        d.text((dx, dy), str(num), font=font(13, True),
               fill=(255, 255, 255), anchor="mm")
    d.ellipse([cx - 86, cy - 86, cx + 86, cy + 86], fill=(255, 255, 255),
              outline=NAVY, width=2)
    d.text((cx, cy - 26), "JUMAT", font=font(12, True), fill=NAVY, anchor="mm")
    d.text((cx, cy - 2), "20 NOV", font=font(19, True), fill=NAVY, anchor="mm")
    d.text((cx, cy + 24), "2026 - WIB", font=font(10), fill=GREY, anchor="mm")


def draw_picture_cards(d):
    leads = {n: (c, h, t, b) for n, c, h, t, b in LEADS}
    order = [1, 2, 3, 5, 7, 9]
    x0, y0, cw, ch, gx, gy = 446, 102, 277, 110, 8, 8
    for i, num in enumerate(order):
        col, _h, title, body = leads[num]
        x = x0 + (i % 2) * (cw + gx)
        y = y0 + (i // 2) * (ch + gy)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=8,
                            fill=(255, 255, 255), outline=LIGHT_LINE, width=1)
        PICTURES[PICTURE_LEADS[num]](d, x + 1, y + 1, cw - 2, 58)
        d.ellipse([x + 6, y + 68, x + 24, y + 86], fill=col)
        d.text((x + 15, y + 77), str(num), font=font(11, True),
               fill=(255, 255, 255), anchor="mm")
        check_fit(d, title, font(13, True), cw - 40, "card title %d" % num)
        d.text((x + 30, y + 70), title, font=font(13, True), fill=INK)
        check_fit(d, body, font(11), cw - 16, "card body %d" % num)
        d.text((x + 8, y + 90), body, font=font(11), fill=GREY)
        d.rectangle([x + 8, y + ch - 4, x + cw - 8, y + ch - 1], fill=col)


def draw_mini_cards(d):
    d.text((16, 456), "ENAM LAGI DARI 12 BESAR", font=font(11, True), fill=GREY)
    leads = {n: (c, h, t, b) for n, c, h, t, b in LEADS}
    order = [4, 6, 8, 10, 11, 12]
    x0, y0, cw, ch, gx, gy = 16, 474, 325, 66, 8, 6
    for i, num in enumerate(order):
        col, _h, title, _b = leads[num]
        x = x0 + (i % 3) * (cw + gx)
        y = y0 + (i // 3) * (ch + gy)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=6,
                            fill=(255, 255, 255), outline=LIGHT_LINE, width=1)
        d.rectangle([x + 6, y, x + cw - 6, y + 5], fill=col)
        d.ellipse([x + 9, y + 23, x + 31, y + 45], fill=col)
        d.text((x + 20, y + 34), str(num), font=font(12, True),
               fill=(255, 255, 255), anchor="mm")
        check_fit(d, title, font(12, True), cw - 48, "mini title %d" % num)
        d.text((x + 38, y + 10), title, font=font(12, True), fill=INK)
        lines = wrap(d, MINI_BODIES[num], font(10), cw - 48)
        for j, line in enumerate(lines[:2]):
            d.text((x + 38, y + 30 + j * 13), line, font=font(10), fill=GREY)


def draw_also(d):
    d.text((16, 620), "JUGA HARI INI - 24 CERITA", font=font(11, True),
           fill=GREY)
    cycle = ["#C92A2A", "#1864AB", "#2E9E44", "#E8590C", "#7048E8", "#0E7C7B"]
    for i, headline in enumerate(ALSO):
        col = cycle[i % len(cycle)]
        x = 16 if i < 12 else 524
        y = 640 + (i % 12) * 22
        d.text((x, y), str(13 + i), font=font(11, True), fill=col)
        check_fit(d, headline, font(11), 452, "also %d" % (13 + i))
        d.text((x + 28, y), headline, font=font(11), fill=INK)


def draw_date_check(d):
    d.rounded_rectangle([16, 910, 1008, 944], radius=6, fill=GREEN_STRIP)
    lines = wrap(d, DATE_CHECK, font(11), 960)
    for j, line in enumerate(lines[:2]):
        d.text((28, 915 + j * 13), line, font=font(11),
               fill=(255, 255, 255))


def draw_footer(d):
    d.text((16, 952), "Sumber: Reuters - AP - AFP - Bloomberg - BBC",
           font=font(11), fill=GREY)
    d.text((1008, 952), "36 cerita - Jumat, 20 November 2026",
           font=font(11), fill=GREY, anchor="ra")
    d.text((16, 970), "Semua waktu WIB - Semua gambar digambar dari data "
           "berita, bukan foto asli.", font=font(11), fill=GREY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_stats(d)
    draw_clock(d)
    draw_picture_cards(d)
    draw_mini_cards(d)
    draw_also(d)
    draw_date_check(d)
    draw_footer(d)
    img.save(OUT, optimize=True)
    print("wrote %s" % OUT)
    if WARNINGS:
        print("WARNINGS (%d):" % len(WARNINGS))
        for w in WARNINGS:
            print("  " + w)
    else:
        print("no overflow warnings")


if __name__ == "__main__":
    main()

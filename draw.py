#!/usr/bin/env python3
"""news-image-20261121 — front page, all art drawn in code (PIL).

35 stories from Saturday 21 November 2026: 3 leads with drawn diagrams,
10 mids with drawn icons, 22 numbered briefs, a world map with pins, a
UTC timeline, a big-number strip, a 9-region bar, a DATE CHECK box and a
verification legend. Zero photographs, zero AI images. Every picture on
the page is built from PIL primitives (rects, ellipses, polygons, arcs).
Deterministic: no randomness, no clock, no network, no external files.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 242, 230)
PAPER2 = (238, 232, 214)
INK = (25, 25, 40)
SOFT = (96, 94, 84)
RULE = (180, 172, 148)
RED = (178, 32, 38)
RED_DK = (138, 20, 26)
NAVY = (24, 38, 68)
GOLD = (176, 128, 0)
TEAL = (46, 111, 158)
GREEN = (61, 122, 61)
AFGREEN = (34, 110, 60)
ORANGE = (180, 90, 27)
PURPLE = (122, 74, 158)
GREY = (107, 107, 107)
SEA = (205, 222, 232)
LAND = (214, 201, 158)
LAND_EDGE = (168, 154, 109)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


def wlen(s, f):
    return f.getlength(s)


def wrap(text, f, maxw):
    """Greedy word wrap by pixel width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if wlen(trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, lines, f, fill, lh):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f, fill=fill)
    return y + len(lines) * lh


def fit(text, path, maxw, start, minimum=9):
    """Largest size (<= start) at which text fits maxw."""
    size = start
    while size > minimum:
        f = F(path, size)
        if f.getlength(text) <= maxw:
            return f
        size -= 1
    return F(path, minimum)


def badge(d, x, y, text, fill, fg=(255, 255, 255), size=8):
    """Small rounded-ish tag; returns its width."""
    f = F(SANS_B, size)
    w = int(f.getlength(text)) + 10
    d.rectangle([x, y, x + w, y + 13], fill=fill)
    d.text((x + 5, y + 2), text, font=f, fill=fg)
    return w


def hline(d, x, y, w, fill=RULE, width=1):
    d.line([(x, y), (x + w, y)], fill=fill, width=width)


# ------------------------------------------------------------------ data
STATS = [
    ("6.7", "magnitude of the Peru quake, 108 km deep"),
    ("2", "tankers hit in the Strait of Hormuz"),
    ("128", "nations back Geneva killer-robot talks"),
    ("90.4%", "of Indonesia tariff lines go to zero, day one"),
    ("82,500", "march in France over living costs"),
    ("37-12", "England's record win over the All Blacks"),
]

REGIONS = [  # label, count, colour
    ("MIDDLE EAST", 7, ORANGE),
    ("AMERICAS", 5, PURPLE),
    ("EUROPE", 8, RED),
    ("EAST ASIA", 2, TEAL),
    ("SE ASIA", 2, GREEN),
    ("AFRICA", 2, AFGREEN),
    ("SCIENCE", 1, NAVY),
    ("SPORT", 5, GOLD),
    ("GLOBAL", 3, GREY),
]

UTC_POINTS = [
    ("00:09", "Peru quake strikes"),
    ("05:00", "Verstappen Vegas pole"),
    ("10:00", "Gaza food-vehicle strike"),
    ("17:30", "Newcastle v Arsenal"),
    ("18:24", "BepiColombo orbits Mercury"),
    ("EVE", "Sparta II ablaze"),
]

LEADS = [
    dict(num=1, kicker="IRAN STRIKES BAHRAIN", place="BAHRAIN \u00b7 GULF",
         head="Iran hits US bases in Bahrain; two tankers struck in Hormuz",
         deck="Revolutionary Guards fire missiles and drones at US positions "
              "in al-Riffa and Awali; UKMTO reports two tankers hit off "
              "Khasab. A Bahrain industrial site burns; no one is hurt.",
         tag="CONFIRMED", src="REUTERS \u00b7 AFP \u00b7 FARS \u00b7 UKMTO",
         art="gulf"),
    dict(num=2, kicker="PERU QUAKE", place="JUN\u00cdN \u00b7 PERU",
         head="Deep M6.7 quake shakes Peru; felt in Lima, no deaths reported",
         deck="Struck 00:09 UTC, 9 km NE of Carhuamayo, 108 km deep (USGS; "
              "129 km, IGP). Tremors reach Lima; first reports list no "
              "deaths and no major damage.",
         tag="CONFIRMED", src="USGS \u00b7 IGP \u00b7 AP \u00b7 AFP",
         art="quake"),
    dict(num=3, kicker="COP31: DAY 13", place="ANTALYA \u00b7 CLIMATE",
         head="Climate talks run into a second day of overtime with no deal",
         deck="A 12-day summit enters day 13. A revised text is ready; "
              "objections close 03:00 GMT Sunday, approval set for 06:00. "
              "The EU threatens to walk out; fossil-fuel text is dropped.",
         tag="CONFIRMED", src="REUTERS \u00b7 AFP \u00b7 UNFCCC",
         art="cop31"),
]

MIDS = [
    dict(num=4, kicker="MEXICO", place="SINALOA \u00b7 CARTEL",
         head="'El Chapo Isidro' captured in Sinaloa raid",
         deck="FBI Top 10 fugitive taken Friday night; 11 dead in the raid.",
         tag="CONFIRMED", src="AP \u00b7 REUTERS", art="cartel"),
    dict(num=5, kicker="BALTIC SEA", place="GULF OF FINLAND",
         head="Drone-hit Russian ship burns; crew evacuated",
         deck="Sparta II ablaze after two drones; Finland suspects Ukraine.",
         tag="CONFIRMED", src="REUTERS \u00b7 AP", art="ship"),
    dict(num=6, kicker="RUGBY", place="TWICKENHAM \u00b7 SPORT",
         head="England 37-12 All Blacks, a record margin",
         deck="Five tries; a 25-point win, the biggest ever over New Zealand.",
         tag="CONFIRMED", src="BBC \u00b7 REUTERS", art="rugby"),
    dict(num=7, kicker="TRADE", place="BRUSSELS \u00b7 EU-INDONESIA",
         head="EU and Indonesia sign free-trade pact",
         deck="90.4% of tariff lines go to zero on day one; in force 2027.",
         tag="CONFIRMED", src="REUTERS \u00b7 ANTARA", art="trade"),
    dict(num=8, kicker="GENEVA", place="UN \u00b7 ARMS",
         head="128 nations agree two years of killer-robot talks",
         deck="States will 'elaborate' rules by 2028; no binding deal yet.",
         tag="CONFIRMED", src="REUTERS \u00b7 AP", art="robot"),
    dict(num=9, kicker="MARKETS", place="CRYPTO \u00b7 BITCOIN",
         head="Bitcoin falls to $55,130, lowest since Sep 2024",
         deck="Intraday low $55,130; closes $57,884 after a $59,248 high.",
         tag="CONFIRMED", src="FINNHUB \u00b7 REUTERS", art="bitcoin"),
    dict(num=10, kicker="PROTESTS", place="FRANCE \u00b7 PORTUGAL \u00b7 SPAIN",
         head="Cost-of-living marches across three countries",
         deck="France 82,500 on a sixth Saturday; thousands march in Lisbon.",
         tag="CONFIRMED", src="REUTERS \u00b7 AFP", art="march"),
    dict(num=11, kicker="TAIWAN", place="TAIPEI \u00b7 MARKETS",
         head="Taiwan bans short-selling below the last close",
         deck="Curbs from Monday; margin 130% to 150% after a 17.5% week.",
         tag="OFFICIAL", src="FSC \u00b7 TAIPEI TIMES", art="chart"),
    dict(num=12, kicker="SPACE", place="MERCURY \u00b7 ESA + JAXA",
         head="BepiColombo enters Mercury orbit after 8 years",
         deck="A 37-minute burn at 18:24 UTC; science starts in April 2027.",
         tag="CONFIRMED", src="ESA \u00b7 REUTERS", art="planet"),
    dict(num=13, kicker="FOOTBALL", place="NEWCASTLE \u00b7 PREMIER LEAGUE",
         head="Newcastle 2-2 Arsenal; Gunners stay top",
         deck="Eze, Barnes, Thiaw, Madueke 78'; Raya hurt in the draw.",
         tag="CONFIRMED", src="BBC \u00b7 REUTERS", art="ball"),
]

BRIEFS = [
    (14, "GAZA", "Strike kills 3 in a food-delivery vehicle in Tel al-Hawa; "
     "IDF says militants, WCK says it was not theirs.", "REPORTED \u00b7 REUTERS"),
    (15, "HALIFAX", "Canada sees no shift in US military ties, minister "
     "says; he has not seen the reported memo.", "REPORTED \u00b7 REUTERS"),
    (16, "WARSAW", "NATO's Rutte in Warsaw: 'We will defend every inch of "
     "Polish territory.'", "REPORTED \u00b7 PAP"),
    (17, "BEIRUT", "Lebanon's president demands Israel withdraw and decries "
     "Iran's interference.", "REPORTED \u00b7 AJ"),
    (18, "TEHRAN", "Iran urges the US to accept its conditions; Qatari "
     "mediators are in Tehran.", "REPORTED \u00b7 AJ"),
    (19, "TEHRAN", "Iran calls the US blockade an 'act of war' and vows "
     "to break it.", "REPORTED \u00b7 IRNA"),
    (20, "SUDAN", "Displaced elderly face hardship and heartbreak in camps "
     "as the war drags on.", "REPORTED \u00b7 AJ"),
    (21, "GULF", "US Central Command denies Iran's claim that its missile "
     "damaged an F-16 over the Gulf.", "REPORTED \u00b7 REUTERS"),
    (22, "BAYELSA", "Boat toll rises to 24; Tinubu orders a rescue push "
     "after Friday's capsize.", "REPORTED \u00b7 AP"),
    (23, "BRAS\u00cdLIA", "Bolsonaro in intensive care with a bowel "
     "obstruction.", "REPORTED \u00b7 AJ"),
    (24, "BASRA", "Fire at the Hartha power station kills at least 4 and "
     "injures 35.", "REPORTED \u00b7 REUTERS"),
    (25, "ZAGREB", "Thousands protest over the death of Kristian Josip "
     "Peris in a psychiatric hospital.", "REPORTED \u00b7 REUTERS"),
    (26, "WASHINGTON", "Trump posts a 'Great Powers 1945, 2026' graphic "
     "after the Nov 19 Xi-Putin summit.", "OFFICIAL \u00b7 TRUTH SOCIAL"),
    (27, "MADRID", "Real Madrid beat Celta Vigo 2-1 at the Bernabeu.",
     "REPORTED \u00b7 LIVESCORE"),
    (28, "SEOUL", "Lee clarifies the 100m-won cheating reward is a minimum "
     "per report, not a cap.", "REPORTED \u00b7 KOREA JOONGANG"),
    (29, "LAS VEGAS", "Verstappen on pole; Antonelli fastest at 1:33.893 "
     "but takes a 5-place penalty.", "CONFIRMED \u00b7 F1"),
    (30, "KYIV", "Zelensky open to a Ukraine-US-Russia meeting at the G20 "
     "if invited.", "REPORTED \u00b7 UKRINFORM"),
    (31, "LONDON", "BBC apologises after lewd audio is heard on live "
     "Saturday Strictly from Blackpool.", "REPORTED \u00b7 BBC"),
    (32, "GLADBACH", "Dortmund go top of the Bundesliga after Nmecha's "
     "80th-minute winner.", "CONFIRMED \u00b7 DPA"),
    (33, "HANOI", "Vietnam passes a law to speed up land expropriation for "
     "priority projects.", "REPORTED \u00b7 REUTERS"),
    (34, "KYIV", "Zelensky: Russia has attacked Ukrainian bridges 109 "
     "times.", "REPORTED \u00b7 UKRINFORM"),
    (35, "BRUSSELS", "EU chair Costa proposes deeper cuts to the 2028-34 "
     "budget and a digital tax.", "REPORTED \u00b7 REUTERS"),
]

DATE_CHECK = [
    "Houthi missiles toward Riyadh: fired late Fri 20 Nov, 23:43 UTC",
    "Zelensky NBC interview: 20 Nov; Crimea bridge strike: 17 Nov",
    "Russian missiles in Poland: Fri 20 Nov, ~05:30 GMT (Kh-101)",
    "Kryvyi Rih strike: date disputed \u2014 left out",
    "Denmark expels Russian attach\u00e9: action pre-dates 21 Nov",
    "TAIEX -6.23% Friday fall: 20 Nov (the curbs are 21 Nov)",
    "Nasdaq -5.3% / Nvidia -14%: Fri 20 Nov",
    "Anthropic IPO: Thu 19 Nov",
    "Shenzhen Xi-Putin-Trump summit: Thu 19 Nov",
    "Bayelsa boat capsized: Fri 20 Nov, 11:00 WAT (toll updates Sat)",
    "COP31 final vote: Sun 22 Nov, 06:00 GMT \u2014 not yet held",
    "Las Vegas GP race: Sun 22 Nov, 04:00 UTC",
    "Liverpool v Man Utd: Sun 22 Nov",
    "S. Korea education minister resigns: Sun 22 Nov",
    "Manipur alcohol deaths: incident pre-dates 21 Nov",
]

# map pins for the 13 drawn stories: num -> (lon, lat, region colour)
PIN_COL = {"ME": ORANGE, "AM": PURPLE, "EU": RED, "EA": TEAL,
           "SE": GREEN, "AF": AFGREEN, "SC": NAVY, "SP": GOLD, "GL": GREY}
PINS = {
    1: (50.5, 26.2, "ME"), 2: (-75.5, -11.0, "AM"), 3: (30.7, 36.9, "GL"),
    4: (-107.0, 25.0, "AM"), 5: (24.0, 59.5, "EU"), 6: (-0.3, 51.5, "SP"),
    7: (4.4, 50.8, "SE"), 8: (6.1, 46.2, "GL"), 9: (-121.0, 37.5, "GL"),
    10: (2.3, 48.9, "EU"), 11: (121.0, 25.0, "EA"), 12: (-150.0, -50.0, "SC"),
    13: (-1.6, 54.98, "SP"),
}


# ------------------------------------------------------------------ art
# Every scene is flat vector art from PIL primitives, drawn inside the
# box (x, y, w, h) handed in by the layout code.

def burst(d, cx, cy, r, colour=(255, 140, 40)):
    for k in range(8):
        a = k * math.pi / 4
        x2 = cx + r * math.cos(a)
        y2 = cy + r * 0.7 * math.sin(a)
        d.line([(cx, cy), (x2, y2)], fill=colour, width=3)
    d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
              fill=(255, 214, 90))


def art_gulf(d, x, y, w, h):
    """Stylised Gulf: sea, Arabian peninsula, Bahrain, Hormuz, tankers."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # Arabian peninsula (lower right landmass)
    d.polygon([(x + w * 0.42, y + h), (x + w * 0.55, y + h * 0.52),
               (x + w * 0.78, y + h * 0.28), (x + w, y + h * 0.30),
               (x + w, y + h), (x + w * 0.42, y + h)], fill=LAND)
    # Iran coast (upper left landmass)
    d.polygon([(x, y), (x + w * 0.52, y), (x + w * 0.48, y + h * 0.22),
               (x + w * 0.30, y + h * 0.30), (x, y + h * 0.26)],
              fill=(198, 186, 140))
    # Bahrain island dot
    bx, by = x + w * 0.47, y + h * 0.52
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=RED)
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], outline=RED, width=2)
    d.text((bx - 28, by + 12), "BAHRAIN", font=F(SANS_B, 10), fill=INK)
    # Hormuz strait marker
    hx, hy = x + w * 0.84, y + h * 0.26
    d.line([(hx - 8, hy - 8), (hx + 8, hy + 8)], fill=RED, width=3)
    d.line([(hx - 8, hy + 8), (hx + 8, hy - 8)], fill=RED, width=3)
    d.text((hx - 96, hy - 12), "HORMUZ", font=F(SANS_B, 10), fill=INK)
    # two tanker markers in the Gulf
    for tx, ty in [(x + w * 0.60, y + h * 0.62), (x + w * 0.72, y + h * 0.50)]:
        d.rectangle([tx - 9, ty - 3, tx + 9, ty + 3], fill=NAVY)
        d.rectangle([tx - 2, ty - 9, tx + 2, ty - 3], fill=NAVY)
        burst(d, tx, ty - 12, 7)
    # missile tracks from Iran toward Bahrain
    d.line([(x + w * 0.30, y + h * 0.16), (bx - 8, by - 6)], fill=RED, width=2)
    d.line([(x + w * 0.22, y + h * 0.08), (bx - 12, by - 12)], fill=RED, width=2)
    d.text((x + 8, y + h - 18), "2 TANKERS HIT", font=F(SANS_B, 11),
           fill=RED_DK)
    d.text((x + 8, y + 6), "IRAN", font=F(SANS_B, 10), fill=SOFT)


def art_quake(d, x, y, w, h):
    """Cross-section: surface towns, hypocentre star, depth arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 205))
    gy = y + int(h * 0.30)
    d.rectangle([x, gy, x + w, y + h], fill=(196, 172, 128))
    d.line([(x, gy), (x + w, gy)], fill=(120, 100, 60), width=3)
    # strata lines
    for k, sy in enumerate([0.48, 0.64, 0.80]):
        d.line([(x, y + h * sy), (x + w, y + h * sy)],
               fill=(150, 128, 88), width=1)
    # towns on the surface
    for tx, label in [(0.18, "CARHUAMAYO"), (0.62, "JUN\u00cdN"), (0.88, "LIMA")]:
        px = x + w * tx
        d.polygon([(px - 5, gy), (px + 5, gy), (px, gy - 10)], fill=INK)
        d.text((px - 26, gy - 22), label, font=F(SANS_B, 8), fill=INK)
    # hypocentre star at depth
    cx, cy = x + w * 0.55, y + h * 0.78
    burst(d, cx, cy, 12, RED)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    # depth arrow from surface to hypocentre
    ax = x + w * 0.55
    d.line([(ax, gy + 4), (ax, cy - 16)], fill=RED, width=2)
    d.polygon([(ax - 4, cy - 18), (ax + 4, cy - 18), (ax, cy - 10)],
              fill=RED)
    d.text((ax + 8, gy + 14), "108 km", font=F(SANS_B, 12), fill=RED_DK)
    d.text((x + 8, y + h - 18), "M6.7 \u00b7 00:09 UTC", font=F(SANS_B, 11),
           fill=INK)
    d.text((x + w - 96, y + h - 18), "IGP: 129 km", font=F(SANS_B, 10),
           fill=SOFT)


def art_cop31(d, x, y, w, h):
    """Calendar strip 9-21 Nov with Day 13 flagged, plus a thermometer."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 228))
    d.text((x + 8, y + 4), "ANTALYA \u00b7 9\u201321 NOV", font=F(SANS_B, 11),
           fill=INK)
    # calendar cells
    cw = (w - 16) / 13
    for i in range(13):
        cx0 = x + 8 + i * cw
        day = 9 + i
        if i == 12:
            d.rectangle([cx0 + 1, y + 20, cx0 + cw - 1, y + 42], fill=RED)
            d.text((cx0 + cw / 2 - 4, y + 26), "21", font=F(SANS_B, 11),
                   fill=(255, 255, 255))
        else:
            d.rectangle([cx0 + 1, y + 20, cx0 + cw - 1, y + 42],
                        fill=(255, 255, 255), outline=RULE)
            d.text((cx0 + cw / 2 - 4, y + 26), str(day),
                   font=F(SANS, 10), fill=INK)
    d.text((x + 8, y + 46), "DAY 13 OF A 12-DAY SUMMIT",
           font=F(SANS_B, 11), fill=RED_DK)
    d.text((x + 8, y + 60), "FOSSIL-FUEL TEXT DROPPED",
           font=F(SANS_B, 10), fill=INK)


def icon_cartel(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=PURPLE)
    d.ellipse([x + s * 0.22, y + s * 0.14, x + s * 0.78, y + s * 0.70],
              outline=(255, 255, 255), width=3)
    d.line([(x + s * 0.68, y + s * 0.62), (x + s * 0.86, y + s * 0.80)],
           fill=(255, 255, 255), width=3)
    tf = F(SANS_B, 14)
    tw = tf.getlength("10")
    d.text((x + s * 0.5 - tw / 2, y + s * 0.30), "10", font=tf,
           fill=(255, 255, 255))


def icon_ship(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=NAVY)
    d.polygon([(x + 4, y + s * 0.62), (x + s - 4, y + s * 0.62),
               (x + s - 9, y + s * 0.82), (x + 9, y + s * 0.82)], fill=(255, 255, 255))
    d.rectangle([x + s * 0.44, y + s * 0.22, x + s * 0.48, y + s * 0.62],
                fill=(255, 255, 255))
    burst(d, x + s * 0.68, y + s * 0.30, 6)


def icon_rugby(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=GOLD)
    d.ellipse([x + 4, y + s * 0.32, x + s - 4, y + s * 0.68], fill=(255, 255, 255))
    d.line([(x + s * 0.30, y + s * 0.50), (x + s * 0.70, y + s * 0.50)],
           fill=GOLD, width=2)


def icon_trade(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=GREEN)
    d.polygon([(x + s * 0.20, y + s * 0.62), (x + s * 0.50, y + s * 0.38),
               (x + s * 0.80, y + s * 0.62)], outline=(255, 255, 255), width=3)
    d.text((x + s * 0.30, y + s * 0.52), "%", font=F(SANS_B, 11),
           fill=(255, 255, 255))


def icon_robot(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=TEAL)
    d.rectangle([x + s * 0.24, y + s * 0.30, x + s * 0.76, y + s * 0.72],
                outline=(255, 255, 255), width=3)
    d.ellipse([x + s * 0.34, y + s * 0.44, x + s * 0.44, y + s * 0.54],
              fill=(255, 255, 255))
    d.ellipse([x + s * 0.56, y + s * 0.44, x + s * 0.66, y + s * 0.54],
              fill=(255, 255, 255))
    d.line([(x + s * 0.50, y + s * 0.30), (x + s * 0.50, y + s * 0.14)],
           fill=(255, 255, 255), width=2)
    d.ellipse([x + s * 0.45, y + s * 0.08, x + s * 0.55, y + s * 0.18],
              fill=(255, 255, 255))


def icon_bitcoin(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=ORANGE)
    d.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], fill=(255, 255, 255))
    d.text((x + s * 0.32, y + s * 0.22), "B", font=F(SANS_B, 17), fill=ORANGE)


def icon_march(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=RED)
    for k in range(3):
        px = x + 6 + k * 9
        d.ellipse([px, y + s * 0.30, px + 6, y + s * 0.36], fill=(255, 255, 255))
        d.rectangle([px + 1, y + s * 0.38, px + 4, y + s * 0.62],
                    fill=(255, 255, 255))
    d.rectangle([x + 4, y + s * 0.68, x + s - 4, y + s * 0.74],
                fill=(255, 255, 255))


def icon_chart(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=TEAL)
    d.line([(x + 5, y + s * 0.78), (x + s - 5, y + s * 0.78)],
           fill=(255, 255, 255), width=2)
    d.line([(x + 6, y + s * 0.70), (x + s * 0.40, y + s * 0.34),
            (x + s * 0.62, y + s * 0.52), (x + s - 6, y + s * 0.20)],
           fill=(255, 120, 90), width=3)


def icon_planet(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=NAVY)
    d.ellipse([x + s * 0.24, y + s * 0.24, x + s * 0.76, y + s * 0.76],
              fill=(200, 190, 170))
    d.ellipse([x + s * 0.36, y + s * 0.34, x + s * 0.46, y + s * 0.44],
              fill=(150, 140, 120))
    d.ellipse([x + s * 0.55, y + s * 0.52, x + s * 0.64, y + s * 0.61],
              fill=(150, 140, 120))
    d.ellipse([x + s * 0.10, y + s * 0.12, x + s * 0.15, y + s * 0.17],
              fill=(255, 255, 255))
    d.ellipse([x + s * 0.80, y + s * 0.78, x + s * 0.84, y + s * 0.82],
              fill=(255, 255, 255))


def icon_ball(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=GREEN)
    d.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], fill=(255, 255, 255))
    d.polygon([(x + s * 0.50, y + s * 0.30), (x + s * 0.68, y + s * 0.46),
               (x + s * 0.60, y + s * 0.68), (x + s * 0.40, y + s * 0.68),
               (x + s * 0.32, y + s * 0.46)], fill=INK)


ICONS = {"cartel": icon_cartel, "ship": icon_ship, "rugby": icon_rugby,
         "trade": icon_trade, "robot": icon_robot, "bitcoin": icon_bitcoin,
         "march": icon_march, "chart": icon_chart, "planet": icon_planet,
         "ball": icon_ball}

LEAD_ART = {"gulf": art_gulf, "quake": art_quake, "cop31": art_cop31}


# ------------------------------------------------------------------ map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-80, 45), (-75, 35), (-80, 25), (-90, 20), (-97, 16), (-105, 20),
     (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-155, 58)],
    # South America
    [(-80, 10), (-75, 0), (-80, -5), (-81, -20), (-70, -30), (-70, -40),
     (-65, -55), (-60, -45), (-50, -30), (-40, -20), (-35, -8), (-50, 0),
     (-60, 5), (-70, 10)],
    # Africa
    [(-18, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -27), (12, -18), (9, -5), (9, 4), (0, 5), (-8, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (23, 65), (18, 69),
     (12, 70), (5, 60), (0, 55), (-5, 50), (-10, 43)],
    # Asia
    [(30, 62), (40, 68), (60, 70), (80, 73), (100, 76), (120, 73),
     (140, 72), (160, 70), (178, 66), (170, 60), (160, 55), (150, 50),
     (140, 45), (135, 40), (130, 35), (127, 33), (122, 30), (120, 25),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (75, 10), (72, 20), (65, 25), (60, 25), (55, 26), (50, 29),
     (48, 30), (44, 29), (40, 35), (35, 36), (30, 36), (30, 42)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]


# leader-line offsets (map px) for the crowded Western-Europe cluster:
# the pin is drawn at the offset point, with a thin line to its true spot.
PIN_OFF = {6: (-16, -2), 13: (16, -12), 10: (-14, 12), 7: (16, 4),
           8: (14, 12)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    d.rectangle([x, y, x + w, y + h], outline=RULE)
    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (75.0 - lat) / 135.0 * h
        return (px, py)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # graticule
    for lon in (-120, -60, 0, 60, 120):
        px = x + (lon + 180.0) / 360.0 * w
        d.line([(px, y), (px, y + h)], fill=(190, 208, 220), width=1)
    for lat in (0, 30, 60, -30):
        py = y + (75.0 - lat) / 135.0 * h
        d.line([(x, py), (x + w, py)], fill=(190, 208, 220), width=1)
    # numbered pins for the 13 drawn stories
    for num in sorted(PINS):
        lon, lat, reg = PINS[num]
        px, py = proj(lon, lat)
        dx, dy = PIN_OFF.get(num, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([(px, py), (px + dx, py + dy)], fill=INK, width=1)
            px, py = px + dx, py + dy
        col = PIN_COL[reg]
        r = 6
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=2)
        tf = F(SANS_B, 8)
        tw = tf.getlength(str(num))
        d.text((px - tw / 2, py - 4), str(num), font=tf,
               fill=(255, 255, 255))
    d.text((x + w - 138, y + 4), "PINS 1-13 = LEADS + MIDS",
           font=F(SANS_B, 8), fill=SOFT)


# ------------------------------------------------------------------ layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)
    MX = 16
    CW = W - 2 * MX  # 992

    # top strip
    d.text((MX, 16), "THE WORLD IN ONE DAY", font=F(SANS_B, 13), fill=RED)
    rt = "35 STORIES \u00b7 9 REGIONS \u00b7 14 FIELDS"
    d.text((W - MX - F(SANS_B, 11).getlength(rt), 18), rt,
           font=F(SANS_B, 11), fill=INK)
    hline(d, MX, 36, CW, width=2)

    # masthead
    mast = "SATURDAY 21 NOVEMBER 2026"
    mf = fit(mast, SERIF_B, CW, 40)
    d.text(((W - mf.getlength(mast)) / 2, 42), mast, font=mf, fill=INK)
    sub = ("Iran strikes US bases in Bahrain  \u00b7  Peru M6.7 quake  "
           "\u00b7  COP31 talks run into overtime")
    sf = F(SERIF, 13)
    d.text(((W - sf.getlength(sub)) / 2, 82), sub, font=sf, fill=SOFT)
    hline(d, MX, 100, CW, width=2)

    # UTC timeline
    d.text((MX, 106), "THE DAY IN UTC", font=F(SANS_B, 10), fill=RED)
    tseg = (CW - 122) / 6
    for i, (t, label) in enumerate(UTC_POINTS):
        cx = MX + 122 + i * tseg
        d.text((cx, 106), t, font=F(SANS_B, 11), fill=RED_DK)
        d.text((cx, 120), label, font=F(SANS, 9), fill=INK)
    hline(d, MX, 136, CW)

    # big-number stat strip
    seg = CW / 6
    for i, (num, label) in enumerate(STATS):
        cx = MX + i * seg + 6
        d.text((cx, 142), num, font=F(SERIF_B, 21), fill=INK)
        ll = wrap(label, F(SANS, 9), seg - 12)
        para(d, cx, 166, ll[:2], F(SANS, 9), SOFT, 11)
    hline(d, MX, 192, CW, width=2)

    # region chips
    d.text((MX, 198), "REGIONS", font=F(SANS_B, 10), fill=RED)
    rx = MX + 62
    for label, count, col in REGIONS:
        txt = "%s %d" % (label, count)
        f = F(SANS_B, 9)
        tw = int(f.getlength(txt)) + 16
        d.ellipse([rx, 199, rx + 9, 208], fill=col)
        d.text((rx + 12, 198), txt, font=f, fill=INK)
        rx += tw + 12
    hline(d, MX, 216, CW)

    # ---- 3 lead panels
    lw = (CW - 18) // 3
    ly = 222
    art_h = 76
    for i, lead in enumerate(LEADS):
        x = MX + i * (lw + 9)
        LEAD_ART[lead["art"]](d, x, ly, lw, art_h)
        d.rectangle([x, ly + art_h, x + lw, ly + art_h + 15], fill=RED)
        d.text((x + 6, ly + art_h + 2), lead["kicker"],
               font=F(SANS_B, 10), fill=(255, 255, 255))
        bw = badge(d, x + lw - 78, ly + art_h + 1, lead["tag"], NAVY)
        hy = ly + art_h + 19
        hl = wrap(lead["head"], F(SERIF_B, 14), lw)
        hy = para(d, x, hy, hl[:2], F(SERIF_B, 14), INK, 17)
        dl = wrap(lead["deck"], F(SANS, 10), lw)
        hy = para(d, x, hy + 3, dl[:3], F(SANS, 10), INK, 12)
        d.text((x, hy + 3), lead["place"], font=F(SANS_B, 8), fill=RED_DK)
        src = lead["src"]
        sf2 = F(SANS, 8)
        d.text((x + lw - sf2.getlength(src), hy + 3), src, font=sf2,
               fill=SOFT)
    hline(d, MX, 404, CW)

    # ---- 10 mids: 5 columns x 2 rows
    mw = (CW - 24) // 5
    my = 412
    mh = 74
    for i, mid in enumerate(MIDS):
        row, col = divmod(i, 5)
        x = MX + col * (mw + 6)
        y = my + row * (mh + 4)
        ICONS[mid["art"]](d, x, y + 2, 30)
        hx = x + 36
        d.text((hx, y), mid["kicker"], font=F(SANS_B, 9), fill=RED_DK)
        hl = wrap(mid["head"], F(SERIF_B, 11), mw - 36)
        para(d, hx, y + 11, hl[:2], F(SERIF_B, 11), INK, 13)
        dl = wrap(mid["deck"], F(SANS, 9), mw)
        para(d, x, y + 40, dl[:2], F(SANS, 9), INK, 11)
        d.text((x, y + 64), mid["tag"] + " \u00b7 " + mid["src"],
               font=F(SANS, 8), fill=SOFT)
    hline(d, MX, 566, CW, width=2)

    # ---- bottom: map + DATE CHECK (left), briefs (right)
    by = 574
    left_w = 452
    right_x = MX + left_w + 12
    right_w = W - MX - right_x
    d.text((MX, by), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=RED)
    draw_map(d, MX, by + 16, left_w, 186)
    d.text((MX, by + 210), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
           font=F(SANS_B, 11), fill=RED)
    dy = by + 228
    for item in DATE_CHECK:
        d.text((MX + 10, dy), "\u00b7", font=F(SANS_B, 9), fill=RED)
        il = wrap(item, F(SANS, 9), left_w - 16)
        dy = para(d, MX + 20, dy, il[:1], F(SANS, 9), INK, 11)

    d.text((right_x, by), "ALSO ON SATURDAY 21 NOVEMBER 2026 \u2014 22 MORE",
           font=F(SANS_B, 11), fill=RED)
    bw2 = (right_w - 10) // 2
    for i, (num, place, text, tag) in enumerate(BRIEFS):
        row, col = divmod(i, 2)
        x = right_x + col * (bw2 + 10)
        y = by + 18 + row * 37
        d.text((x, y), "%d \u00b7 %s" % (num, place), font=F(SANS_B, 9),
               fill=RED_DK)
        tf7 = F(SANS, 7)
        d.text((x + bw2 - tf7.getlength(tag), y + 1), tag, font=tf7,
               fill=SOFT)
        f9 = F(SANS, 9)
        tl = wrap(text, f9, bw2)
        if len(tl) > 2:
            tl = wrap(text, F(SANS, 8), bw2)
        para(d, x, y + 11, tl[:2], F(SANS, 9) if len(tl) <= 2 else F(SANS, 8),
             INK, 11)
    hline(d, MX, 996, CW)

    # footer legend
    foot = ("HOW WE CHECKED \u2014 CONFIRMED = 2+ major outlets \u00b7 "
            "OFFICIAL = on the record \u00b7 REPORTED = one major outlet \u00b7 "
            "All art drawn in code \u00b7 Sources named beside every story")
    ff = F(SANS, 9)
    d.text(((W - ff.getlength(foot)) / 2, 1000), foot, font=ff, fill=SOFT)

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()

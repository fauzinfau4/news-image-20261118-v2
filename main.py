"""THE WORLD TODAY - one image summing up world news of 18 November 2026.

Pure-stdlib Python 3.13 program. Draws a dense newspaper front page:
masthead, lead story, a world map with numbered story locations, and
32 short real stories from 18 November 2026 in three columns.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
Deterministic: no time, no randomness, no network, fixed palette.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (178, 28, 28)
BLUE = (29, 78, 160)
OCEAN = (214, 231, 244)
LAND = (226, 214, 178)
LAND_EDGE = (150, 135, 100)
GREY = (110, 105, 95)
LIGHT = (235, 229, 214)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, written as strings. Uppercase, digits
# and punctuation only; all text is uppercased before drawing.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                for xx in range(x, x + w):
                    if 0 <= xx < self.w:
                        i = (yy * self.w + xx) * 3
                        self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for a in range(360):
            import math
            x = cx + int(r * math.cos(math.radians(a)))
            y = cy + int(r * math.sin(math.radians(a)))
            self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s.upper()) * 6 * scale - scale

    def text_center(self, y, s, scale, c, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = self.text_w(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines."""
        max_chars = max(1, (max_w + scale) // (6 * scale))
        words = s.upper().split(" ")
        lines, cur = [], ""
        for word in words:
            if not cur:
                cur = word
            elif len(cur) + 1 + len(word) <= max_chars:
                cur += " " + word
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def save_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", comp)
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------- world map
# Rough continent outlines as (lon, lat) polygons, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 73), (-95, 80),
     (-85, 76), (-75, 73), (-65, 62), (-55, 52), (-65, 44), (-75, 38),
     (-80, 32), (-81, 26), (-90, 21), (-97, 16), (-92, 15), (-105, 20),
     (-110, 24), (-117, 33), (-124, 40), (-125, 49), (-135, 58),
     (-150, 60), (-158, 58), (-168, 66)],
    # Greenland
    [(-58, 64), (-45, 66), (-32, 68), (-25, 74), (-32, 78), (-55, 80),
     (-62, 76), (-58, 64)],
    # South America
    [(-80, 9), (-72, 12), (-62, 9), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-39, -15), (-40, -22), (-48, -27), (-55, -34),
     (-62, -38), (-66, -45), (-70, -52), (-73, -54), (-73, -44),
     (-72, -30), (-70, -20), (-77, -12), (-81, -5), (-80, 9)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 70), (25, 71),
     (18, 69), (12, 65), (5, 60), (5, 58), (-2, 57), (-6, 53), (-10, 48),
     (-10, 36)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 30), (-5, 35), (10, 37), (20, 33),
     (30, 31), (35, 28), (43, 12), (51, 11), (46, 5), (41, -2), (40, -10),
     (36, -18), (33, -26), (26, -34), (19, -35), (15, -30), (12, -18),
     (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 15)],
    # Asia
    [(30, 36), (36, 36), (43, 40), (48, 38), (52, 37), (57, 26), (61, 25),
     (66, 25), (72, 20), (77, 8), (80, 13), (85, 19), (89, 22), (92, 21),
     (98, 10), (100, 8), (104, 2), (108, 11), (109, 18), (113, 22),
     (120, 28), (122, 32), (126, 38), (130, 42), (135, 44), (140, 46),
     (142, 52), (142, 59), (156, 59), (162, 60), (170, 66), (178, 65),
     (170, 60), (158, 52), (145, 60), (135, 72), (120, 73), (105, 76),
     (90, 75), (75, 73), (68, 70), (60, 69), (50, 68), (40, 68), (32, 70),
     (30, 66), (30, 60), (28, 55), (30, 45), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32), (135, -35),
     (140, -38), (146, -39), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (130, -13), (122, -14), (114, -21), (113, -22)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (1, 51), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
     (143, 42), (145, 44), (141, 39), (137, 36), (133, 34), (130, 31)],
    # Indonesia / SE Asia islands
    [(95, 5), (100, 0), (106, -6), (112, -7), (118, -9), (122, -4),
     (120, 1), (115, 4), (105, 5), (100, 6), (95, 5)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (178, -38), (175, -41), (171, -44),
     (167, -45)],
]


def draw_map(cv, x0, y0, mw, mh):
    cv.rect(x0, y0, mw, mh, OCEAN)
    # graticule
    for lon in range(-150, 181, 30):
        gx = x0 + int((lon + 180) / 360.0 * mw)
        for yy in range(y0, y0 + mh):
            if (yy - y0) % 4 < 2:
                cv.set(gx, yy, (190, 210, 228))
    for lat in (-30, 0, 30, 60):
        gy = y0 + int((75 - lat) / 135.0 * mh)
        for xx in range(x0, x0 + mw):
            if (xx - x0) % 4 < 2:
                cv.set(xx, gy, (190, 210, 228))
    # continents: scanline fill
    for poly in CONTINENTS:
        pts = [(x0 + int((lon + 180) / 360.0 * mw),
                y0 + int((75 - lat) / 135.0 * mh)) for lon, lat in poly]
        ys = [p[1] for p in pts]
        for yy in range(max(y0, min(ys)), min(y0 + mh, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= yy < y2) or (y2 <= yy < y1):
                    t = (yy - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[k]), int(xs[k + 1])
                for xx in range(max(x0, xa), min(x0 + mw, xb + 1)):
                    cv.set(xx, yy, LAND)
    cv.rect(x0, y0, mw, 2, INK)
    cv.rect(x0, y0 + mh - 2, mw, 2, INK)
    cv.rect(x0, y0, 2, mh, INK)
    cv.rect(x0 + mw - 2, y0, 2, mh, INK)


def map_xy(x0, y0, mw, mh, lon, lat):
    return (x0 + int((lon + 180) / 360.0 * mw),
            y0 + int((75 - lat) / 135.0 * mh))

# ---------------------------------------------------------------- stories
# (number, headline, summary, map lon/lat or None)
# All events happened or were first reported on 18 November 2026.
STORIES = [
    (1, "UKRAINE HITS CRIMEA BRIDGE AGAIN",
     "Second-day missile and drone strike on the Kerch link; Russia pounds Kyiv bridges.",
     (33.0, 45.0)),
    (2, "TRUMP LANDS IN MANILA FOR QUAD",
     "US president opens Asia trip at Quad talks; bloc unveils maritime exercise.",
     (121.0, 14.6)),
    (3, "IRAN DRONE STRIKE HITS US RADAR",
     "IRGC claims attack on US radar at Bahrain's Sheikh Isa base; third strike in 5 days.",
     (50.6, 26.2)),
    (4, "EU READIES 45BN EURO UKRAINE LOAN",
     "Brussels to propose joint borrowing; approves historic 8bn euro payout to Kyiv.",
     (4.4, 50.8)),
    (5, "GERMANY PLEDGES 11.6BN EUROS",
     "Berlin to fund Ukraine in 2027; with Norway, 300m dollars each for US arms.",
     (13.4, 52.5)),
    (6, "SIX KILLED IN GAZA AS STRIKES GO ON",
     "Child among dead; UN warns of hypothermia deaths as winter nears.",
     (34.5, 31.5)),
    (7, "US LOSES MEASLES-FREE STATUS",
     "Health agency confirms loss as cases and deaths mount across America.",
     (-77.0, 38.9)),
    (8, "NVIDIA BEATS AFTER HUANG EXIT",
     "Revenue 115.8bn dollars, up 103%; first results since CEO resigned.",
     (-122.0, 37.4)),
    (9, "CYCLONE AKVAN NEARS ANDHRA COAST",
     "Storm to hit 20 Nov at 120 km/h; three killed as it batters eastern India.",
     (80.3, 15.9)),
    (10, "MONGOLIA PRESIDENT RESIGNS",
     "Head of state quits amid graft charges, AFP reports from Ulaanbaatar.",
     (106.9, 47.9)),
    (11, "JAPAN PROTESTS RUSSIAN AIRSPACE BREACH",
     "Tokyo summons Moscow envoy over suspected violation in southwest.",
     (139.7, 35.7)),
    (12, "BRITAIN SANCTIONS SETTLER FIRMS",
     "London acts against Israeli settlement companies to defend two-state path.",
     (-0.1, 51.5)),
    (13, "CANADA AND CHINA EXTEND TRADE DEALS",
     "Xi meets Carney ahead of APEC summit in Shenzhen.",
     None),
    (14, "MODI OFFERS FREE E-VISAS TO ASEAN",
     "India PM in Manila pitches maritime plan and closer ties with bloc.",
     None),
    (15, "ANTHROPIC IPO TO PRICE TODAY",
     "AI firm eyes up to 1.4tn dollar value as shares price on 18 Nov.",
     None),
    (16, "GTA VI LAUNCHES TOMORROW",
     "Game out 19 Nov after 13 years; pre-orders near 15m copies, 1.45bn dollars.",
     None),
    (17, "TAIWAN AWAITS 14BN DOLLAR ARMS CALL",
     "Taipei says deal 'up to' Trump; US presses UN body over flight curbs.",
     None),
    (18, "PENTAGON FAILS NINTH AUDIT IN A ROW",
     "US defence department again cannot pass financial audit.",
     None),
    (19, "UK TELLS HOMES: STOCKPILE 3 DAYS",
     "Cabinet Office 'Be Ready' drive urges food, water and essentials.",
     None),
    (20, "DHONI RETIRES FROM IPL",
     "Chennai great ends playing career; returns as mentor for next season.",
     None),
    (21, "INDIA BEAT PAKISTAN FOR SAFF CROWN",
     "2-1 win seals record 10th South Asian football title.",
     None),
    (22, "AMAZON PUTS 7BN DOLLARS IN INDIA GREEN ENERGY",
     "Renewables push announced as Delhi growth seen at 7.5%.",
     None),
    (23, "BANGLADESH GARMENT UNREST SPREADS",
     "Workers clash with police; bomb blasts near Dhaka airport injure three.",
     None),
    (24, "IMRAN KHAN: 'I MAY DIE IN JAIL'",
     "Ex-Pakistan PM's letter from prison warns of his failing health.",
     None),
    (25, "US JUDGE BLOCKS STUDENT VISA RULES",
     "Court halts new restrictions on foreign students.",
     None),
    (26, "SUDAN WAR DEATH TOLL PASSES 2,230",
     "UN rights office: most killed by drone strikes in past 10 months.",
     None),
    (27, "AUSTRALIA EASES BACKPACKER VISAS",
     "Canberra loosens working-holiday curbs to fill farm and resort jobs.",
     None),
    (28, "ITALY APPROVES ANTISEMITISM LAW",
     "Rome passes bill amid debate over criticism of Israel.",
     None),
    (29, "RUSSIAN PLANE CRASH KILLS 19",
     "Military aircraft goes down in Siberia, officials confirm.",
     None),
    (30, "MOLDOVA SHUTS SIX BORDER POINTS",
     "Russian drones violated airspace during strikes on Ukraine.",
     None),
    (31, "KIM TOURS RESORT BEFORE TRUMP TRIP",
     "North Korea leader visits tourism site as US president heads to Asia.",
     None),
    (32, "MARKETS REBOUND ON NVIDIA",
     "Asian shares rise after chip forecast; S&P 500 at lowest since June.",
     None),
]


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    M = 22
    CW = W - 2 * M

    # masthead
    y = 16
    cv.text_center(y, "THE WORLD TODAY", 5, INK)
    y += 5 * 7 + 8
    cv.text_center(y, "WEDNESDAY, 18 NOVEMBER 2026", 2, RED)
    y += 2 * 7 + 6
    cv.text_center(y, "ONE DAY - THE WHOLE WORLD - 32 STORIES", 1, GREY)
    y += 7 + 10
    cv.hline(M, y, CW, INK, 3)
    y += 5
    cv.hline(M, y, CW, INK, 1)
    y += 10

    # lead story
    cv.text_center(y, "UKRAINE STRIKES CRIMEA BRIDGE", 3, INK)
    y += 3 * 7 + 3
    cv.text_center(y, "AS RUSSIA POUNDS KYIV BRIDGES", 3, INK)
    y += 3 * 7 + 6
    cv.text_center(y,
                   "KYIV SAYS SECOND-DAY ATTACK HIT THE KERCH LINK; MOSCOW OPENS TERROR PROBE",
                   1, GREY)
    y += 7 + 8
    cv.hline(M, y, CW, INK, 1)
    y += 8

    # world map
    map_x, map_y, map_w, map_h = M, y, CW, 168
    draw_map(cv, map_x, map_y, map_w, map_h)
    cv.text(map_x + 8, map_y + 6, "WHERE THE NEWS HAPPENED", 1, BLUE)
    for num, _h, _s, loc in STORIES:
        if loc is None:
            continue
        mx, my = map_xy(map_x, map_y, map_w, map_h, loc[0], loc[1])
        cv.disc(mx, my, 8, RED)
        cv.ring(mx, my, 8, (255, 255, 255))
        label = str(num)
        tw = cv.text_w(label, 1)
        cv.text(mx - tw // 2, my - 3, label, 1, (255, 255, 255))
    y += map_h + 10
    cv.hline(M, y, CW, INK, 1)
    y += 8

    # section header
    cv.text_center(y, "THE DAY IN FULL", 2, RED)
    y += 2 * 7 + 8
    cv.hline(M, y, CW, GREY, 1)
    y += 8

    # three columns of stories
    col_w = 304
    col_xs = [M, M + col_w + 22, M + 2 * (col_w + 22)]
    per_col = 11
    for ci in range(3):
        cx = col_xs[ci]
        cy = y
        for story in STORIES[ci * per_col:(ci + 1) * per_col]:
            num, head, summ, _loc = story
            # number badge
            cv.rect(cx, cy, 16, 14, RED)
            nlab = str(num)
            cv.text(cx + (16 - cv.text_w(nlab, 1)) // 2, cy + 3, nlab, 1,
                    (255, 255, 255))
            # headline, up to 2 lines
            hl = cv.wrap(head, 2, col_w - 22)
            hx = cx + 22
            hy = cy
            for line in hl[:2]:
                cv.text(hx, hy, line, 2, INK)
                hy += 2 * 7 + 1
            # summary, up to 2 lines
            sl = cv.wrap(summ, 1, col_w - 22)
            sy = hy + 1
            for line in sl[:2]:
                cv.text(hx, sy, line, 1, GREY)
                sy += 7 + 1
            cy = max(sy, cy + 36) + 4
            cv.hline(cx, cy - 3, col_w, LIGHT, 1)
        if ci < 2:
            cv.vline(cx + col_w + 11, y, 552, LIGHT, 1)

    # footer
    fy = H - 26
    cv.hline(M, fy - 8, CW, INK, 1)
    cv.text_center(fy, "SOURCES: REUTERS, AP, AFP, DAWN, NDTV, TECHCRUNCH - ALL EVENTS OF 18 NOV 2026",
                   1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    save_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()

"""The World in One Day -- Sunday 22 November 2026.

A program that draws one newspaper front page summing up the world's
news of Sunday 22 November 2026 and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Python standard library only: no Pillow, no network, no randomness.
Every run writes the exact same bytes (1024x1024 PNG).

Stories (all reported on 22 November 2026):
  Lead. Iran strikes a U.S. air base in Kuwait and targets Bahrain as
     Gulf attacks widen. Multiple tankers are hit off the Oman coast
     and an ADNOC vessel is attacked in the Strait of Hormuz.
  1. A magnitude 6.9 earthquake shakes Peru's Andes; no damage or
     casualties were immediately reported.
  2. COP31 climate talks are deadlocked over fossil fuels.
  3. Trump touts a 'momentous' summit with Xi and Putin at APEC in
     Shenzhen; Vance won't back the Iran strikes in public.
  4. Drones hit a Russian cargo ship in the Baltic; Finland tightens
     security; Russia hits Ukraine with 400 drones and 110 missiles.
  5. Estonia moves to close its border with Russia; Moscow decries a
     'new Iron Curtain'.
  6. Mexican cartel boss 'El Chapo Isidro' is arrested in a
     special-forces raid; deadly cartel violence follows in Sinaloa,
     11 killed.
  7. Brazil's ex-president Bolsonaro is admitted to intensive care
     with acute bowel obstruction.
  8. Sport: India v New Zealand, 1st Test in Wellington; KL Rahul
     leads India's reply.
"""

import hashlib
import math
import os
import struct
import sys
import zlib

# ------------------------------------------------------------------ font --
# A 5x7 pixel font drawn for this entry. Each glyph is seven rows of
# five pixels; "#" is on, "." is off. Capitals, digits and a small
# set of punctuation. Lowercase input is folded to upper case.

FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "·": (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
}

# --------------------------------------------------------------- colours --
NAVY = (12, 20, 40)       # page background
NAVY2 = (30, 46, 80)      # mini-strip background
CREAM = (240, 234, 214)   # masthead text
PAPER = (244, 238, 222)   # card background
INK = (22, 22, 22)        # text on paper
RED = (166, 30, 30)       # lead red
FLAME = (220, 90, 30)     # flame orange
AMBER = (232, 160, 60)    # date line
GOLD = (212, 175, 55)     # frame and footer
BLUE = (29, 78, 137)      # climate blue
STEEL = (60, 90, 120)     # baltic steel
PLUM = (110, 60, 110)     # border plum
GREEN = (30, 110, 70)     # cartel green
GREY = (150, 160, 180)    # muted text on navy
DARK = (40, 40, 50)       # tanker hull


class Canvas:
    """An RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        for deg in range(360):
            a = math.radians(deg)
            self.set(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)),
                     color)

    def polyfill(self, pts, color):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(xx, y, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale

    def text(self, text, x, y, scale, color):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_centred(self, text, cx, y, scale, color):
        self.text(text, cx - self.text_width(text, scale) // 2, y, scale,
                  color)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines."""
        unit = 6 * scale
        lines = []
        for para in text.split("\n"):
            line = ""
            for word in para.split(" "):
                trial = word if not line else line + " " + word
                if len(trial) * unit <= max_width or not line:
                    line = trial
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return lines


# ----------------------------------------------------------------- icons --
# Every icon takes (cv, x, y, s, color): a box of size s at (x, y).


def icon_quake(cv, x, y, s, color):
    """Two mountain peaks split by a jagged crack."""
    cv.polyfill([(x, y + s), (x + s // 4, y + s // 3),
                 (x + s // 2, y + s)], color)
    cv.polyfill([(x + s // 3, y + s), (x + 2 * s // 3, y + s // 6),
                 (x + s, y + s)], color)
    crack = [(x + s // 2, y + s // 4), (x + s // 2 - 4, y + s // 2),
             (x + s // 2 + 4, y + 2 * s // 3),
             (x + s // 2 - 3, y + s - 4)]
    for a, b in zip(crack, crack[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED)


def icon_flame_tanker(cv, x, y, s, color):
    """A tanker hull under a flame."""
    flame = [(x + s // 2, y), (x + s - 8, y + s // 4),
             (x + s // 2 + 6, y + s // 3), (x + s - 2, y + s // 2),
             (x + s // 2, y + s // 2 + 4), (x + 2, y + s // 2),
             (x + s // 2 - 6, y + s // 3), (x + 8, y + s // 4)]
    cv.polyfill(flame, FLAME)
    cv.polyfill([(x + s // 2, y + s // 6), (x + s // 2 + 8, y + s // 3),
                 (x + s // 2, y + s // 2)], (250, 180, 40))
    hull = [(x + 2, y + 2 * s // 3), (x + s - 2, y + 2 * s // 3),
            (x + s - 10, y + s - 8), (x + 10, y + s - 8)]
    cv.polyfill(hull, DARK)
    cv.rect(x + s // 2 + 4, y + s // 2 + 2, 10, 2 * s // 3 - s // 2 - 2,
            DARK)
    cv.hline(x, y + s - 4, s, BLUE)
    cv.hline(x + 8, y + s - 1, s - 16, BLUE)


def icon_globe_cross(cv, x, y, s, color):
    """A globe with a diagonal bar across it, plus an oil drop."""
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 2
    cv.ring(cx, cy, r, color)
    cv.hline(cx - r, cy, 2 * r, color)
    cv.vline(cx, cy - r, 2 * r, color)
    cv.line(cx - r + 2, cy + r - 2, cx + r - 2, cy - r + 2, RED)
    drop = [(cx + r // 2, cy + r // 2 - 8), (cx + r // 2 + 6, cy + r // 2 + 2),
            (cx + r // 2, cy + r // 2 + 8), (cx + r // 2 - 6, cy + r // 2 + 2)]
    cv.polyfill(drop, (30, 30, 30))


def icon_flags(cv, x, y, s, color):
    """Three small flags on poles for the summit."""
    cols = [RED, GOLD, BLUE]
    fw = max(8, s // 5)              # flag width scales with the box
    step = (s - 4 - fw) // 2         # pole spacing; last flag ends at x+s
    for k in range(3):
        px = x + 4 + k * step
        cv.vline(px, y + 8, s - 12, color)
        cv.rect(px, y + 2, fw, 8, cols[k])
        cv.disc(px, y + s - 4, 2, color)


def icon_ship_drone(cv, x, y, s, color):
    """A cargo ship below a small drone."""
    cv.rect(x + s // 2 - 8, y, 16, 4, color)
    cv.disc(x + s // 2 - 12, y + 2, 3, color)
    cv.disc(x + s // 2 + 12, y + 2, 3, color)
    cv.vline(x + s // 2 - 12, y + 2, 8, color)
    cv.vline(x + s // 2 + 12, y + 2, 8, color)
    cv.vline(x + s // 2, y + 4, 14, color)
    hull = [(x + 4, y + s // 2 + 6), (x + s - 4, y + s // 2 + 6),
            (x + s - 12, y + s - 6), (x + 12, y + s - 6)]
    cv.polyfill(hull, color)
    cv.rect(x + s // 2 - 4, y + s // 2 - 6, 8, 12, color)
    cv.hline(x, y + s - 2, s, BLUE)


def icon_fence(cv, x, y, s, color):
    """A border fence: two rails and vertical bars."""
    cv.hline(x, y + 8, s, color)
    cv.hline(x, y + s - 8, s, color)
    for bx in range(x + 4, x + s, 10):
        cv.vline(bx, y + 8, s - 16, color)
    cv.line(x, y, x + s, y + s, RED)


def icon_cuffs(cv, x, y, s, color):
    """Handcuffs: two rings joined by a short chain."""
    cv.ring(x + 12, y + s // 2, 10, color)
    cv.ring(x + s - 12, y + s // 2, 10, color)
    cv.line(x + 22, y + s // 2 - 4, x + s - 22, y + s // 2 + 4, color)
    cv.disc(x + s // 2, y + s // 2, 3, color)


# ---------------------------------------------------------------- content --
LEAD_HEAD = "GULF IN FLAMES"
LEAD_SUB = "IRAN HITS U.S. BASE IN KUWAIT - TANKERS STRUCK OFF OMAN"
LEAD_BODY = (
    "Iran strikes a U.S. air base in Kuwait and targets Bahrain as Gulf "
    "attacks widen. Multiple tankers are hit off the Oman coast and an "
    "ADNOC vessel is attacked in the Strait of Hormuz.")

CARDS = [
    ("QUAKE", RED, icon_quake,
     "MAGNITUDE 6.9 SHAKES PERU",
     "The quake struck the Andes on Sunday. No damage or casualties "
     "were immediately reported. Tremors were felt across the region."),
    ("CLIMATE", BLUE, icon_globe_cross,
     "COP31 DEADLOCK ON FOSSIL FUELS",
     "Climate talks stall as the fight over fossil fuels leaves the "
     "deal deadlocked. Negotiators push for a breakthrough."),
    ("SUMMIT", GOLD, icon_flags,
     "TRUMP TOUTS XI-PUTIN SUMMIT",
     "Trump calls the Shenzhen APEC meeting 'momentous'. Vance won't "
     "back the Iran strikes in public."),
    ("BALTIC", STEEL, icon_ship_drone,
     "DRONES HIT RUSSIAN CARGO SHIP",
     "Drones strike a Russian cargo ship in the Baltic. Finland "
     "tightens security as tensions rise at sea."),
    ("BORDER", PLUM, icon_fence,
     "ESTONIA SHUTS RUSSIA BORDER",
     "Estonia moves to close its border with Russia. Moscow decries a "
     "'new Iron Curtain'."),
    ("CARTEL", GREEN, icon_cuffs,
     "CARTEL BOSS ARRESTED IN RAID",
     "'El Chapo Isidro' is seized in a special-forces raid. Deadly "
     "cartel violence follows in Sinaloa: 11 killed."),
]

MINIS = [
    ("BOLSONARO IN ICU",
     "Brazil's ex-president is admitted to intensive care with acute "
     "bowel obstruction."),
    ("INDIA V NEW ZEALAND",
     "1st Test, Wellington: KL Rahul leads India's reply after New "
     "Zealand's big first innings."),
]

FOOTER = "ONE DAY · ONE IMAGE"
SOURCES = ("SOURCES: BBC, REUTERS, TIMES OF INDIA, ARY NEWS, JAGRAN JOSH - "
           "ALL STORIES REPORTED 22 NOVEMBER 2026")


def draw():
    W, H = 1024, 1024
    cv = Canvas(W, H, NAVY)
    mx = 28

    # ------------------------------------------------------------ gold frame --
    cv.rect(14, 14, W - 28, 3, GOLD)
    cv.rect(14, H - 17, W - 28, 3, GOLD)
    cv.rect(14, 14, 3, H - 28, GOLD)
    cv.rect(W - 17, 14, 3, H - 28, GOLD)

    # ------------------------------------------------------------ masthead --
    cv.text_centred("THE WORLD IN ONE DAY", W // 2, 36, 6, CREAM)
    cv.text_centred("SUNDAY 22 NOVEMBER 2026", W // 2, 106, 2, AMBER)
    cv.text_centred("ONE IMAGE - NINE STORIES", W // 2, 130, 1, GREY)
    cv.hline(mx, 152, W - 2 * mx, GOLD)
    cv.hline(mx, 156, W - 2 * mx, GOLD)

    # ---------------------------------------------------------- lead story --
    ly, lh = 168, 182
    cv.rect(mx, ly, W - 2 * mx, lh, PAPER)
    cv.rect(mx, ly, 8, lh, RED)
    cv.text(LEAD_HEAD, mx + 24, ly + 10, 4, INK)
    cv.text(LEAD_SUB, mx + 24, ly + 52, 2, RED)
    body_w = W - 2 * mx - 24 - 150
    lines = cv.wrap(LEAD_BODY, body_w, 2)
    y = ly + 82
    for ln in lines:
        cv.text(ln, mx + 24, y, 2, INK)
        y += 22
    icon_flame_tanker(cv, W - mx - 138, ly + 46, 96, RED)

    # ------------------------------------------------------------ grid ------
    gy = 368
    cw, ch, hgap, vgap = 466, 150, 20, 16
    for idx, (tag, color, icon, head, body) in enumerate(CARDS):
        col, row = idx % 2, idx // 2
        x = mx + col * (cw + hgap)
        y = gy + row * (ch + vgap)
        cv.rect(x, y, cw, ch, PAPER)
        cv.rect(x, y, cw, 3, color)
        cv.text(tag, x + 14, y + 11, 2, color)
        head_lines = cv.wrap(head, cw - 28 - 52, 2)
        hy = y + 30
        for ln in head_lines[:1]:
            cv.text(ln, x + 14, hy, 2, INK)
            hy += 21
        # Body text stops 10px short of the icon zone (icon left edge
        # at cw-62), so no line can run into an icon.
        body_lines = cv.wrap(body, 380, 1)
        by = y + 58
        for ln in body_lines[:4]:
            cv.text(ln, x + 14, by, 1, INK)
            by += 11
        icon(cv, x + cw - 62, y + 18, 55, color)

    # -------------------------------------------------------- mini stories --
    my, mh = 866, 62
    for idx, (head, body) in enumerate(MINIS):
        x = mx + idx * (cw + hgap)
        cv.rect(x, my, cw, mh, NAVY2)
        cv.rect(x, my, 4, mh, GOLD)
        cv.text(head, x + 16, my + 9, 1, GOLD)
        body_lines = cv.wrap(body, cw - 32, 1)
        by = my + 26
        for ln in body_lines[:2]:
            cv.text(ln, x + 16, by, 1, CREAM)
            by += 11

    # -------------------------------------------------------------- footer --
    cv.hline(mx, 944, W - 2 * mx, GOLD)
    cv.text_centred(FOOTER, W // 2, 956, 2, GOLD)
    cv.text_centred(SOURCES, W // 2, 982, 1, GREY)
    return cv


# -------------------------------------------------------------------- png --
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def to_png(cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw()
    png = to_png(cv)
    assert png[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG magic"
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes, sha256 %s)"
          % (path, len(png), hashlib.sha256(png).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

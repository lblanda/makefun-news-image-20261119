# main.py -- draws "The World in One Day", a 1024x1024 news poster summing up
# Thursday 19 November 2026, and writes it to /output/entry.png.
#
# Pure Python 3 standard library only: no Pillow, no network, no fonts on
# disk. The picture is drawn pixel by pixel on an RGB canvas with a small
# 5x7 bitmap font (font5x7.py), and encoded as a PNG by hand (zlib + CRC).
# The story list lives in stories.py. Running the program twice writes the
# same bytes: nothing here reads the clock, the network or randomness.
#
#   MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import font5x7
import stories

W, H = 1024, 1024

PAPER = (246, 241, 231)
INK = (25, 25, 25)
NAVY = (22, 35, 63)
GOLD = (194, 154, 43)
RED = (166, 30, 34)
TEAL = (31, 111, 107)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
MUTED = (90, 88, 80)
LIGHT = (238, 232, 218)


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(color * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def hline(self, x, y, w, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)

    def vline(self, x, y, h, color, thickness=1):
        self.fill_rect(x, y, thickness, h, color)

    def line(self, x0, y0, x1, y1, color, thickness=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thickness, thickness, color)
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
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - half, cy + dy, 2 * half + 1, color)

    def ring(self, cx, cy, r, color, thickness=2):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            inner = int(max(0, (r - thickness) ** 2 - dy * dy) ** 0.5) if abs(dy) < r - thickness else 0
            self.hline(cx - half, cy + dy, half - inner, color)
            self.hline(cx + inner + 1, cy + dy, half - inner, color)

    def polygon(self, points, color):
        """Scanline fill of a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, color)

    def star(self, cx, cy, r, color):
        import math
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((int(cx + rr * math.cos(ang)), int(cy + rr * math.sin(ang))))
        self.polygon(pts, color)

    # -- text -------------------------------------------------------------
    def text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = font5x7.GLYPHS.get(ch, font5x7.GLYPHS[" "])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cx + col_i * scale, y + row_i * scale,
                                       scale, scale, color)
            cx += font5x7.CELL * scale
        return cx

    def text_center(self, cx, y, text, scale, color):
        w = font5x7.text_width(text, scale)
        self.text(cx - w // 2, y, text, scale, color)

    def paragraph(self, x, y, text, max_width, scale, color, leading=None):
        """Word-wrapped paragraph; returns the y below the last line."""
        lh = leading if leading is not None else font5x7.HEIGHT * scale + 4
        for line in font5x7.wrap(text, max_width, scale):
            self.text(x, y, line, scale, color)
            y += lh
        return y


# ---------------------------------------------------------------- icons

def icon_scales(c, x, y, s, color):
    # Scales of justice in a s x s box.
    c.vline(x + s // 2, y + 4, s - 14, color, 2)
    c.hline(x + 6, y + 8, s - 12, color, 2)
    c.hline(x + s // 2 - 10, y + s - 6, 20, color, 2)
    for cx in (x + 8, x + s - 8):
        c.line(cx, y + 8, cx - 8, y + s - 16, color, 2)
        c.line(cx, y + 8, cx + 8, y + s - 16, color, 2)
        c.polygon([(cx - 9, y + s - 16), (cx + 9, y + s - 16),
                   (cx, y + s - 8)], color)


def icon_bridge(c, x, y, s, color):
    # A bridge with a gap in its deck and smoke rising from it.
    c.fill_rect(x + 4, y + s - 22, 6, 14, color)
    c.fill_rect(x + s - 10, y + s - 22, 6, 14, color)
    c.hline(x + 2, y + s - 24, s // 2 - 6, color, 3)
    c.hline(x + s // 2 + 4, y + s - 24, s // 2 - 6, color, 3)
    c.line(x + 7, y + s - 24, x + s // 2, y + 16, color, 2)
    c.line(x + s - 7, y + s - 24, x + s // 2, y + 16, color, 2)
    for dx, dy, r in ((0, 0, 7), (9, -6, 5), (-8, -7, 5)):
        c.disc(x + s // 2 + dx, y + 10 + dy, r, MUTED)


def icon_tanker(c, x, y, s, color):
    # An oil tanker on waves, with a flame above its deck.
    c.polygon([(x + 4, y + s - 20), (x + s - 4, y + s - 20),
               (x + s - 12, y + s - 10), (x + 12, y + s - 10)], color)
    c.fill_rect(x + s - 22, y + s - 32, 12, 12, color)
    c.fill_rect(x + 10, y + s - 30, 8, 10, RED)
    c.fill_rect(x + 22, y + s - 30, 8, 10, GOLD)
    c.fill_rect(x + 34, y + s - 30, 8, 10, TEAL)
    for wy in (y + s - 6, y + s - 2):
        for wx in range(x + 2, x + s - 2, 10):
            c.hline(wx, wy, 7, color, 2)
    c.polygon([(x + s // 2, y + 2), (x + s // 2 - 6, y + 14),
               (x + s // 2 + 6, y + 14)], GOLD)


def icon_flame(c, x, y, s, color):
    # A flame: outer teardrop with an inner tongue.
    c.polygon([(x + s // 2, y + 2), (x + s - 6, y + s // 2),
               (x + s - 4, y + s - 8), (x + 6, y + s - 8),
               (x + 4, y + s // 2)], color)
    c.disc(x + s // 2, y + s - 10, 9, GOLD)
    c.polygon([(x + s // 2, y + s - 22), (x + s // 2 - 5, y + s - 8),
               (x + s // 2 + 5, y + s - 8)], WHITE)


def icon_tower(c, x, y, s, color):
    # A tall tower with lit windows, a crack and smoke at its top.
    c.fill_rect(x + s // 2 - 11, y + 10, 22, s - 16, color)
    for wy in range(y + 16, y + s - 10, 8):
        c.fill_rect(x + s // 2 - 7, wy, 14, 3, GOLD)
    c.line(x + s // 2 + 2, y + 12, x + s // 2 - 3, y + 24, WHITE, 2)
    c.line(x + s // 2 - 3, y + 24, x + s // 2 + 4, y + 34, WHITE, 2)
    c.disc(x + s // 2 + 14, y + 6, 6, MUTED)
    c.disc(x + s // 2 + 22, y + 2, 4, MUTED)


def icon_pad(c, x, y, s, color):
    # A game controller: body, sticks, d-pad and buttons.
    c.polygon([(x + 6, y + 12), (x + s - 6, y + 12), (x + s - 2, y + s - 8),
               (x + s - 14, y + s - 2), (x + 14, y + s - 2),
               (x + 2, y + s - 8)], color)
    c.disc(x + 14, y + s - 16, 5, PAPER)
    c.disc(x + s - 14, y + s - 16, 5, PAPER)
    c.fill_rect(x + s // 2 - 9, y + 18, 4, 12, PAPER)
    c.fill_rect(x + s // 2 - 13, y + 22, 12, 4, PAPER)
    for dx, dy, col in ((8, -2, GOLD), (14, 2, RED), (2, 2, TEAL)):
        c.disc(x + s // 2 + dx, y + 20 + dy, 3, col)


ICONS = {
    "scales": icon_scales,
    "bridge": icon_bridge,
    "tanker": icon_tanker,
    "flame": icon_flame,
    "tower": icon_tower,
    "pad": icon_pad,
}


# ---------------------------------------------------------------- poster

def draw_flag(c, x, y, w, h, kind):
    if kind == "usa":
        for i in range(7):
            c.fill_rect(x, y + i * h // 7, w, h // 7 + 1,
                        RED if i % 2 == 0 else WHITE)
        c.fill_rect(x, y, w * 2 // 5, h * 4 // 7, NAVY)
        for r in range(4):
            for col in range(5):
                c.set(x + 4 + col * 5, y + 4 + r * 5, WHITE)
    elif kind == "china":
        c.fill_rect(x, y, w, h, RED)
        c.star(x + 11, y + 11, 7, GOLD)
        for sx, sy in ((30, 6), (36, 11), (36, 18), (30, 23)):
            c.star(x + sx, y + sy, 3, GOLD)
    elif kind == "russia":
        c.fill_rect(x, y, w, h // 3, WHITE)
        c.fill_rect(x, y + h // 3, w, h // 3, (0, 57, 166))
        c.fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (213, 0, 50))


def draw_lead_art(c, x, y, w, h):
    # Shenzhen skyline at dusk, with the three leaders' flags above it.
    sky = (214, 226, 240)
    c.fill_rect(x, y, w, h, sky)
    heights = [58, 92, 70, 118, 84, 132, 96, 64, 110, 76, 120, 88, 66]
    bw = w // len(heights)
    base = y + h
    for i, bh in enumerate(heights):
        bx = x + i * bw
        c.fill_rect(bx + 2, base - bh, bw - 4, bh, NAVY)
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(bx + 6, bx + bw - 6, 9):
                if (wx + wy) % 23 < 11:
                    c.set(wx, wy, GOLD)
    # Three flag poles, left to right: USA, China, Russia.
    pole_x = [x + 52, x + w // 2 - 4, x + w - 96]
    for px, kind in zip(pole_x, ("usa", "china", "russia")):
        c.vline(px, y + 18, 74, INK, 3)
        draw_flag(c, px + 3, y + 20, 44, 28, kind)


def draw_panel(c, x, y, w, h, panel, accent):
    c.fill_rect(x, y, w, h, CARD)
    c.rect(x, y, w, h, NAVY, 2)
    # Kicker bar.
    c.fill_rect(x + 2, y + 2, w - 4, 30, accent)
    c.text(x + 12, y + 10, panel["kicker"], 2, WHITE)
    # Headline.
    hy = y + 44
    hy = c.paragraph(x + 12, hy, panel["headline"], w - 24, 3, INK, 24)
    # Body.
    c.paragraph(x + 12, hy + 6, panel["body"], w - 24, 2, MUTED, 17)
    # Icon band.
    band_y = y + h - 52
    c.fill_rect(x + 2, band_y, w - 4, 50, LIGHT)
    c.hline(x + 2, band_y, w - 4, accent, 2)
    icon = ICONS[panel["icon"]]
    icon(c, x + w // 2 - 22, band_y + 3, 44, accent)


def draw_poster():
    c = Canvas(W, H, PAPER)

    # Masthead.
    c.fill_rect(0, 0, W, 118, NAVY)
    c.disc(52, 59, 30, TEAL)
    c.ring(52, 59, 30, GOLD, 2)
    c.hline(30, 59, 44, GOLD, 2)
    c.vline(52, 37, 44, GOLD, 2)
    c.text(100, 24, stories.MASTHEAD, 5, WHITE)
    c.text(100, 76, stories.DATE_LINE, 3, GOLD)
    c.text(906, 18, "19", 8, WHITE)
    c.text(908, 82, "NOV 2026", 2, GOLD)
    c.fill_rect(0, 118, W, 6, GOLD)

    # Lead story.
    lx, ly, lw, lh = 24, 136, 976, 276
    c.fill_rect(lx, ly, lw, lh, CARD)
    c.rect(lx, ly, lw, lh, NAVY, 3)
    c.text(lx + 24, ly + 18, stories.LEAD["kicker"], 2, RED)
    hy = c.paragraph(lx + 24, ly + 46, stories.LEAD["headline"], 560, 4, INK, 37)
    c.paragraph(lx + 24, hy + 8, stories.LEAD["body"], 560, 2, MUTED, 19)
    draw_lead_art(c, lx + 616, ly + 18, 336, lh - 36)

    # Story panels, 3 across, 2 rows.
    accents = [TEAL, NAVY, RED, GOLD, NAVY, TEAL]
    pw, ph = 316, 240
    for i, panel in enumerate(stories.PANELS):
        px = 24 + (i % 3) * (pw + 14)
        py = 428 + (i // 3) * (ph + 14)
        draw_panel(c, px, py, pw, ph, panel, accents[i])

    # Also-today strip and footer.
    sy = 936
    c.fill_rect(24, sy, 976, 66, NAVY)
    end_y = c.paragraph(40, sy + 9, stories.ALSO_TODAY, 944, 2, WHITE, 18)
    c.text_center(512, end_y + 6, stories.FOOTER, 2, GOLD)

    return c


# ---------------------------------------------------------------- PNG

def png_chunk(kind, data):
    chunk = struct.pack(">I", len(data)) + kind + data
    chunk += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def encode_png(canvas):
    raw = bytearray()
    for y in range(canvas.height):
        raw.append(0)
        start = y * canvas.width * 3
        raw += canvas.pixels[start:start + canvas.width * 3]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += png_chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(draw_poster())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png)} bytes)")


if __name__ == "__main__":
    main()

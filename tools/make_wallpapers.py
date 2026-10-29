#!/usr/bin/env python3
"""Рисует зимние обои 4K для «Новогоднего оформителя».

Картинки полностью оригинальные: не фото и не чужие работы, поэтому их можно
спокойно держать в репозитории.

    python3 tools/make_wallpapers.py
"""

from __future__ import annotations

import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 3840, 2160
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "wallpapers")
THUMBS = os.path.join(OUT, "thumbs")
THUMB_SIZE = (480, 270)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(stops):
    """Вертикальный градиент по списку (позиция, цвет)."""
    column = Image.new("RGB", (1, H))
    pixels = column.load()
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0.0
                pixels[0, y] = mix(c0, c1, k)
                break
        else:
            pixels[0, y] = stops[-1][1]
    return column.resize((W, H), Image.BILINEAR).convert("RGBA")


def glow(canvas, center, radius, color, strength=1.0):
    """Мягкое пятно света."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                 fill=(*color, int(255 * strength)))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    canvas.alpha_composite(layer)


def stars(canvas, count, seed, y_limit=0.8, top_fade=True):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rnd.uniform(0, W)
        y = rnd.uniform(0, H * y_limit)
        r = rnd.uniform(1.0, 3.4)
        fade = 1 - (y / (H * y_limit)) * 0.7 if top_fade else 1
        alpha = int(rnd.randint(70, 235) * fade)
        colour = (255, 255, 255, alpha)
        if rnd.random() < 0.12:
            colour = (200, 225, 255, alpha)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=colour)

    blurred = layer.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(blurred)
    canvas.alpha_composite(layer)


def ridge(y_base, amplitude, frequency, seed):
    """Контур холма из суммы синусов."""
    rnd = random.Random(seed)
    phases = [rnd.uniform(0, math.tau) for _ in range(3)]
    points = []
    for x in range(-8, W + 9, 8):
        t = x / W
        y = (y_base
             + amplitude * 0.65 * math.sin(math.tau * frequency * t + phases[0])
             + amplitude * 0.28 * math.sin(math.tau * frequency * 2.3 * t + phases[1])
             + amplitude * 0.12 * math.sin(math.tau * frequency * 4.7 * t + phases[2]))
        points.append((x, y))
    return points


def hill(canvas, y_base, amplitude, frequency, seed, top, bottom, haze=0):
    points = ridge(y_base, amplitude, frequency, seed)
    polygon = points + [(W + 8, H + 8), (-8, H + 8)]

    top_y = y_base - amplitude
    bottom_y = y_base + amplitude
    column = Image.new("RGB", (1, H))
    pixels = column.load()
    for y in range(H):
        if y <= top_y:
            pixels[0, y] = top
        elif y >= bottom_y:
            pixels[0, y] = bottom
        else:
            pixels[0, y] = mix(top, bottom, (y - top_y) / (bottom_y - top_y))
    fill = column.resize((W, H), Image.BILINEAR).convert("RGBA")

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(fill, (0, 0), mask)
    if haze:
        layer = layer.filter(ImageFilter.GaussianBlur(haze))
    canvas.alpha_composite(layer)


def pine(draw, x, base_y, height, width, colour, snow=None):
    tiers = 4
    for i in range(tiers):
        apex_y = base_y - height * (1.0 - 0.18 * i)
        base = base_y - height * (0.62 - 0.16 * i)
        half = width * (0.18 + 0.16 * i)
        draw.polygon([(x, apex_y), (x - half, base), (x + half, base)],
                     fill=colour)
        if snow:
            draw.line([(x - half * 0.94, base - 4), (x + half * 0.94, base - 4)],
                      fill=snow, width=5)
    draw.rectangle([x - width * 0.05, base_y - height * 0.14,
                    x + width * 0.05, base_y], fill=colour)


def tree(draw, x, base_y, height, colour, snow=None):
    pine(draw, x, base_y, height, height * 0.55, colour, snow)


def grain(canvas, strength=0.05, seed=3):
    noise = Image.effect_noise((W, H), 22).convert("RGB")
    return Image.blend(canvas.convert("RGB"), noise, strength).convert("RGBA")


def vignette(canvas, strength=0.55):
    mask = Image.new("L", (W // 8, H // 8), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([-W // 24, -H // 24, W // 8 + W // 24, H // 8 + H // 24], fill=255)
    mask = mask.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", canvas.size, (4, 8, 16, 255))
    alpha = mask.point(lambda v: int((255 - v) * strength))
    dark.putalpha(alpha)
    canvas.alpha_composite(dark)


def save(canvas, slug):
    os.makedirs(THUMBS, exist_ok=True)
    image = canvas.convert("RGB")
    image.save(os.path.join(OUT, f"{slug}.jpg"), quality=90, optimize=True,
               progressive=True)
    image.copy().resize(THUMB_SIZE, Image.LANCZOS).save(
        os.path.join(THUMBS, f"{slug}.jpg"), quality=88, optimize=True)
    print("готово:", slug)


# --------------------------------------------------------------------------
# сцены
# --------------------------------------------------------------------------

def polar_night():
    canvas = sky([(0.0, (6, 12, 30)), (0.45, (14, 28, 56)),
                  (0.72, (28, 52, 88)), (1.0, (10, 20, 38))])
    stars(canvas, 1500, seed=11, y_limit=0.72)

    glow(canvas, (W * 0.76, H * 0.20), 300, (255, 246, 226), 0.95)
    moon = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(moon).ellipse([W * 0.76 - 150, H * 0.20 - 150,
                                  W * 0.76 + 150, H * 0.20 + 150],
                                 fill=(255, 250, 238, 255))
    canvas.alpha_composite(moon)

    hill(canvas, H * 0.70, 170, 0.8, 21, (32, 52, 84), (18, 32, 58), haze=3)
    hill(canvas, H * 0.82, 120, 1.3, 22, (232, 240, 250), (158, 182, 210), haze=2)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rnd = random.Random(5)
    for i in range(16):
        x = rnd.uniform(-100, W + 100)
        base = H * rnd.uniform(0.87, 0.94)
        tree(draw, x, base, rnd.uniform(360, 640),
             (14, 26, 44), (226, 238, 252, 170))
    canvas.alpha_composite(layer)

    vignette(canvas, 0.5)
    save(grain(canvas, 0.035), "polar-night")


def aurora():
    canvas = sky([(0.0, (5, 15, 26)), (0.5, (9, 30, 44)),
                  (0.78, (14, 44, 56)), (1.0, (7, 22, 32))])
    stars(canvas, 1200, seed=31, y_limit=0.7)

    bands = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(bands)
    rnd = random.Random(9)
    for index in range(5):
        colour = [(120, 255, 190), (90, 220, 255), (170, 150, 255),
                  (120, 255, 210), (80, 200, 255)][index]
        offset = H * (0.20 + index * 0.05)
        points = []
        for x in range(-40, W + 41, 10):
            t = x / W
            y = (offset
                 + 120 * math.sin(math.tau * (0.7 + index * 0.12) * t + index)
                 + 60 * math.sin(math.tau * 1.9 * t + index * 2.1))
            points.append((x, y))
        width = rnd.randint(60, 150)
        draw.line(points, fill=(*colour, 95), width=width, joint="curve")

    bands = bands.filter(ImageFilter.GaussianBlur(55))
    canvas.alpha_composite(bands)

    hill(canvas, H * 0.74, 150, 0.9, 41, (16, 34, 48), (8, 18, 28), haze=2)
    hill(canvas, H * 0.85, 110, 1.5, 42, (226, 240, 248), (148, 176, 204), haze=2)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rnd = random.Random(4)
    for _ in range(12):
        x = rnd.uniform(-60, W + 60)
        tree(draw, x, H * rnd.uniform(0.84, 0.94), rnd.uniform(300, 540),
             (10, 22, 32), (210, 235, 240, 150))
    canvas.alpha_composite(layer)

    vignette(canvas, 0.45)
    save(grain(canvas, 0.035), "aurora")


def sunset():
    canvas = sky([(0.0, (38, 26, 60)), (0.28, (86, 46, 78)),
                  (0.50, (176, 92, 96)), (0.66, (238, 150, 116)),
                  (0.78, (250, 196, 152)), (0.86, (206, 174, 190)),
                  (1.0, (232, 236, 246))])

    glow(canvas, (W * 0.68, H * 0.62), 420, (255, 214, 170), 0.85)
    sun = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sun).ellipse([W * 0.68 - 110, H * 0.62 - 110,
                                 W * 0.68 + 110, H * 0.62 + 110],
                                fill=(255, 240, 214, 255))
    sun = sun.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(sun)

    # облачные полосы
    clouds = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(clouds)
    rnd = random.Random(15)
    for _ in range(9):
        y = rnd.uniform(H * 0.30, H * 0.62)
        x = rnd.uniform(-400, W)
        w = rnd.uniform(500, 1500)
        h = rnd.uniform(16, 46)
        draw.ellipse([x, y, x + w, y + h], fill=(255, 196, 178, 40))
    clouds = clouds.filter(ImageFilter.GaussianBlur(30))
    canvas.alpha_composite(clouds)

    hill(canvas, H * 0.77, 150, 0.7, 51, (150, 128, 150), (98, 84, 116), haze=3)
    hill(canvas, H * 0.85, 100, 1.2, 52, (240, 236, 244), (172, 172, 196), haze=2)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rnd = random.Random(8)
    for _ in range(10):
        tree(draw, rnd.uniform(0, W), H * rnd.uniform(0.86, 0.96),
             rnd.uniform(280, 470),
             (74, 62, 88), (244, 240, 246, 160))
    canvas.alpha_composite(layer)

    vignette(canvas, 0.35)
    save(grain(canvas, 0.03), "sunset")


def minimal():
    canvas = sky([(0.0, (8, 16, 32)), (0.55, (14, 28, 52)),
                  (0.82, (32, 58, 92)), (1.0, (16, 30, 52))])
    stars(canvas, 420, seed=61, y_limit=0.6)

    glow(canvas, (W * 0.22, H * 0.30), 260, (214, 232, 255), 0.45)
    moon = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(moon).ellipse([W * 0.22 - 78, H * 0.30 - 78,
                                  W * 0.22 + 78, H * 0.30 + 78],
                                 fill=(238, 244, 255, 245))
    canvas.alpha_composite(moon.filter(ImageFilter.GaussianBlur(2)))
    hill(canvas, H * 0.88, 90, 0.5, 71, (18, 33, 56), (10, 20, 36), haze=1)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    tree(draw, W * 0.72, H * 0.90, 760, (10, 20, 36), (220, 234, 248, 120))
    canvas.alpha_composite(layer)

    vignette(canvas, 0.5)
    save(grain(canvas, 0.045), "minimal")


def bokeh():
    canvas = sky([(0.0, (10, 20, 40)), (0.55, (18, 38, 68)),
                  (1.0, (26, 52, 88))])

    rnd = random.Random(77)
    for _ in range(46):
        x = rnd.uniform(0, W)
        y = rnd.uniform(0, H)
        r = rnd.uniform(40, 260)
        strength = rnd.uniform(0.06, 0.22)
        glow(canvas, (x, y), r, (226, 240, 255), strength)

    flakes = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(flakes)
    for _ in range(140):
        x = rnd.uniform(0, W)
        y = rnd.uniform(0, H)
        r = rnd.uniform(2, 7)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=(255, 255, 255, rnd.randint(70, 190)))
    flakes = flakes.filter(ImageFilter.GaussianBlur(1.6))
    canvas.alpha_composite(flakes)

    vignette(canvas, 0.4)
    save(grain(canvas, 0.03), "bokeh")


def moon_forest():
    canvas = sky([(0.0, (6, 10, 22)), (0.40, (10, 20, 38)),
                  (0.70, (22, 34, 56)), (1.0, (12, 22, 38))])
    stars(canvas, 800, seed=91, y_limit=0.65)

    glow(canvas, (W * 0.30, H * 0.24), 260, (250, 244, 226), 0.8)
    moon = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(moon).ellipse([W * 0.30 - 120, H * 0.24 - 120,
                                  W * 0.30 + 120, H * 0.24 + 120],
                                 fill=(252, 248, 236, 255))
    canvas.alpha_composite(moon.filter(ImageFilter.GaussianBlur(4)))

    # туманные полосы
    fog = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(fog)
    rnd = random.Random(23)
    for _ in range(6):
        y = rnd.uniform(H * 0.55, H * 0.82)
        draw.rectangle([0, y, W, y + rnd.uniform(40, 110)],
                       fill=(150, 175, 200, 26))
    canvas.alpha_composite(fog.filter(ImageFilter.GaussianBlur(60)))

    # три плана леса
    for index, (scale, tone, count) in enumerate([
        (0.62, (26, 38, 58), 26),
        (0.45, (16, 26, 42), 20),
        (0.30, (9, 16, 28), 14),
    ]):
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        rnd = random.Random(100 + index)
        for _ in range(count):
            x = rnd.uniform(-80, W + 80)
            base = H * (0.86 + index * 0.05)
            tree(draw, x, base, rnd.uniform(320, 620) * scale + 240, tone, None)
        canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(index * 1.4)))

    hill(canvas, H * 0.95, 80, 1.0, 111, (212, 226, 242), (150, 172, 198), haze=2)

    vignette(canvas, 0.55)
    save(grain(canvas, 0.04), "moon-forest")


def cabin():
    canvas = sky([(0.0, (4, 10, 24)), (0.45, (10, 22, 44)),
                  (0.72, (18, 36, 62)), (1.0, (12, 24, 42))])
    stars(canvas, 1100, seed=131, y_limit=0.7)

    glow(canvas, (W * 0.2, H * 0.18), 240, (236, 242, 255), 0.8)
    moon = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(moon).ellipse([W * 0.2 - 95, H * 0.18 - 95,
                                  W * 0.2 + 95, H * 0.18 + 95],
                                 fill=(250, 248, 240, 255))
    canvas.alpha_composite(moon.filter(ImageFilter.GaussianBlur(3)))

    hill(canvas, H * 0.66, 200, 0.6, 141, (24, 42, 68), (14, 26, 44), haze=3)
    hill(canvas, H * 0.81, 120, 1.1, 142, (230, 238, 250), (160, 182, 210), haze=2)

    # домик
    house = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(house)
    x, y = W * 0.62, H * 0.79
    w, h = 560, 320
    draw.rectangle([x - w / 2, y - h, x + w / 2, y], fill=(30, 27, 38, 255))
    draw.polygon([(x - w / 2 - 80, y - h + 24), (x, y - h - 210),
                  (x + w / 2 + 80, y - h + 24)], fill=(20, 20, 30, 255))
    draw.line([(x - w / 2 - 66, y - h + 10), (x, y - h - 190),
               (x + w / 2 + 66, y - h + 10)],
              fill=(238, 245, 252, 240), width=18, joint="curve")
    for dx in (-160, 70):
        draw.rectangle([x + dx, y - h + 120, x + dx + 90, y - h + 220],
                       fill=(255, 214, 130, 255))
    draw.rectangle([x - 46, y - 150, x + 46, y], fill=(18, 16, 24, 255))
    canvas.alpha_composite(house)
    glow(canvas, (x - 115, y - h + 170), 170, (255, 196, 110), 0.55)
    glow(canvas, (x + 115, y - h + 170), 170, (255, 196, 110), 0.55)
    glow(canvas, (x, y + 10), 320, (255, 190, 120), 0.18)

    hill(canvas, H * 0.90, 90, 1.6, 143, (204, 218, 236), (148, 170, 198), haze=2)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rnd = random.Random(12)
    for _ in range(9):
        tree(draw, rnd.uniform(0, W), H * rnd.uniform(0.88, 0.96),
             rnd.uniform(380, 660),
             (12, 24, 40), (222, 236, 250, 150))
    canvas.alpha_composite(layer)

    vignette(canvas, 0.5)
    save(grain(canvas, 0.04), "cabin")


def frost():
    """Морозные узоры на стекле."""
    canvas = sky([(0.0, (18, 28, 52)), (0.28, (46, 64, 100)),
                  (0.52, (110, 122, 162)), (0.74, (196, 182, 200)),
                  (1.0, (246, 232, 234))])

    rnd = random.Random(211)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    def fern(x, y, angle, length, width, depth):
        if depth == 0 or length < 16:
            return
        x2 = x + math.cos(angle) * length
        y2 = y + math.sin(angle) * length
        draw.line([(x, y), (x2, y2)],
                  fill=(255, 255, 255, rnd.randint(120, 190)),
                  width=max(1, int(width)))
        fern(x2, y2, angle + rnd.uniform(-0.18, 0.18),
             length * 0.74, width * 0.7, depth - 1)
        for side in (-1, 1):
            if rnd.random() < 0.9:
                fern(x2, y2, angle + side * rnd.uniform(0.5, 1.05),
                     length * rnd.uniform(0.48, 0.66), width * 0.58, depth - 1)

    for corner_x, spread in ((0, 0.45), (W, -0.45)):
        for _ in range(4):
            fern(corner_x + rnd.uniform(-120, 120), H + 60,
                 -math.pi / 2 + spread + rnd.uniform(-0.35, 0.35),
                 rnd.uniform(430, 620), 11, 5)

    for _ in range(6):
        x = rnd.uniform(0, W)
        fern(x, H + 40, -math.pi / 2 + rnd.uniform(-0.6, 0.6),
             rnd.uniform(180, 320), 6, 3)

    layer = layer.filter(ImageFilter.GaussianBlur(1.6))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(22)))
    canvas.alpha_composite(layer)
    save(grain(canvas, 0.03), "frost")


SCENES = [polar_night, aurora, sunset, minimal, bokeh, moon_forest, cabin, frost]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for scene in SCENES:
        scene()

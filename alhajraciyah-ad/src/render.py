"""Al-Hajraciyah organic farm — 43s vertical ad renderer (1080x1920 @30fps)."""
import math, os, sys, subprocess, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
DUR = 43.0
BASE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(BASE, "fonts")
IMG = os.path.join(BASE, "img")

MAROON = (122, 28, 40)
MAROON_D = (70, 14, 22)
GOLD = (222, 173, 88)
GOLD_L = (250, 222, 160)
CREAM = (248, 238, 222)
INK = (40, 22, 18)

# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def ease_out(x):  # cubic
    return 1 - (1 - x) ** 3

def ease_in_out(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

def ease_back(x, s=1.7):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1

def lerp(a, b, t):
    return a + (b - a) * t

def lerpc(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))

@lru_cache(None)
def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(FD, name), size, layout_engine=ImageFont.Layout.RAQM)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f

KUFI = "ReemKufi%5Bwght%5D.ttf"
NOTO = "NotoKufiArabic%5Bwght%5D.ttf"
AMIRI = "Amiri-Bold.ttf"
RUQAA = "ArefRuqaa-Bold.ttf"
TAJ = "Tajawal-Bold.ttf"

@lru_cache(None)
def text_img(text, fname, size, fill, var=None, shadow=True, glow=None, stroke=0, stroke_fill=None):
    f = font(fname, size, var)
    kw = dict(direction="rtl", language="ar") if any("؀" <= ch <= "ۿ" for ch in text) else {}
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=f, stroke_width=stroke, **kw)
    pad = int(size * 0.6)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    org = (pad - bb[0], pad - bb[1])
    if glow:
        g = Image.new("L", (w, h), 0)
        ImageDraw.Draw(g).text(org, text, font=f, fill=255, stroke_width=max(2, size // 14), **kw)
        g = g.filter(ImageFilter.GaussianBlur(size / 5))
        gl = Image.new("RGBA", (w, h), glow[:3] + (0,))
        gl.putalpha(g.point(lambda v: int(v * (glow[3] if len(glow) > 3 else 200) / 255)))
        lay.alpha_composite(gl)
    if shadow:
        s = Image.new("L", (w, h), 0)
        ImageDraw.Draw(s).text((org[0], org[1] + size // 18), text, font=f, fill=150, stroke_width=stroke, **kw)
        s = s.filter(ImageFilter.GaussianBlur(size / 12))
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.putalpha(s)
        lay.alpha_composite(sh)
    d.text(org, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, **kw)
    return lay

def wipe_rtl(lay, p, soft=0.25):
    """Reveal a layer from right to left (Arabic reading direction) with a soft edge."""
    if p >= 1:
        return lay
    w, h = lay.size
    x = np.linspace(0, 1, w, dtype=np.float32)
    m = np.clip((x - (1 - p * (1 + soft))) / soft, 0, 1)
    a = np.asarray(lay.getchannel("A"), dtype=np.float32) * m[None, :]
    out = lay.copy()
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out

def with_alpha(lay, a):
    if a >= 0.999:
        return lay
    out = lay.copy()
    out.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    return out

def paste_center(frame, lay, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.003:
        return
    if abs(scale - 1) > 1e-3:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    lay = with_alpha(lay, alpha)
    frame.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def put_text(frame, text, fname, size, cx, cy, fill, t0, t, dur=0.7, var=None, out_t=None, glow=None, rise=40, wipe=True, stroke=0, stroke_fill=None):
    if t < t0:
        return
    p = ease_out(prog(t, t0, t0 + dur))
    a = p
    if out_t is not None:
        a *= 1 - ease_in_out(prog(t, out_t, out_t + 0.45))
    lay = text_img(text, fname, size, fill, var, True, glow, stroke, stroke_fill)
    if wipe:
        lay = wipe_rtl(lay, p)
    paste_center(frame, lay, cx, cy + (1 - p) * rise, a)

def vgrad(c1, c2, h=H, w=W, gamma=1.0):
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None] ** gamma
    c1, c2 = np.array(c1, np.float32), np.array(c2, np.float32)
    g = c1[None, :] * (1 - y) + c2[None, :] * y
    return np.repeat(g[:, None, :], w, axis=1)

def multi_grad(stops, h=H, w=W):
    y = np.linspace(0, 1, h, dtype=np.float32)
    pos = [s[0] for s in stops]
    cols = np.array([s[1] for s in stops], np.float32)
    g = np.stack([np.interp(y, pos, cols[:, k]) for k in range(3)], -1)
    return np.repeat(g[:, None, :], w, axis=1)

def radial(cx, cy, r, h=H, w=W):
    yy, xx = np.ogrid[:h, :w]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    return np.clip(1 - d, 0, 1).astype(np.float32)

def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

# ------------------------------------------------------------- global FX
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
YY, XX = np.mgrid[:H, :W]
VIG = (1 - 0.55 * np.clip(((XX - W / 2) / (W * 0.75)) ** 2 + ((YY - H / 2) / (H * 0.72)) ** 2, 0, 1)).astype(np.float32)

def finish(frame, fi, grain=6.0, vig=1.0):
    a = np.asarray(frame.convert("RGB"), dtype=np.float32)
    g = GRAIN[fi % len(GRAIN)]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)
    a = a * (1 - vig + vig * VIG[..., None]) + g[..., None] * grain
    return np.clip(a, 0, 255).astype(np.uint8)

# --------------------------------------------------------------- palms
def make_palm(h, seed, color=(20, 14, 18), dates=None, fronds=18):
    r = random.Random(seed)
    S = 2  # supersample
    Wc, Hc = int(h * 1.25) * S, int(h * 1.1) * S
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base = (Wc / 2, Hc - 2)
    lean = r.uniform(-0.12, 0.12) * h * S
    top = (Wc / 2 + lean, Hc - h * S * 0.78)
    # trunk
    n = 40
    pts_l, pts_r = [], []
    for i in range(n + 1):
        s = i / n
        x = lerp(base[0], top[0], s) + math.sin(s * math.pi) * lean * 0.3
        y = lerp(base[1], top[1], s)
        wdt = lerp(0.045, 0.028, s) * h * S
        pts_l.append((x - wdt, y)); pts_r.append((x + wdt, y))
    d.polygon(pts_l + pts_r[::-1], fill=color + (255,))
    # trunk scale texture
    for i in range(1, n, 2):
        s = i / n
        x = lerp(base[0], top[0], s) + math.sin(s * math.pi) * lean * 0.3
        y = lerp(base[1], top[1], s)
        wdt = lerp(0.045, 0.028, s) * h * S
        c2 = tuple(min(255, c + 18) for c in color)
        d.line([(x - wdt, y), (x, y - wdt * 0.5), (x + wdt, y)], fill=c2 + (255,), width=max(1, S))
    cx, cy = top
    # dates bunches
    if dates:
        for k in range(r.randint(3, 5)):
            ang = r.uniform(-2.2, -0.9) if k % 2 else r.uniform(0.9, 2.2)
            bx, by = cx + math.cos(ang) * 0.05 * h * S * (1 if k % 2 else -1), cy + 0.03 * h * S
            for j in range(26):
                dx = r.gauss(0, 0.022 * h * S); dy = abs(r.gauss(0.05, 0.03)) * h * S
                rr = 0.009 * h * S
                col = dates if r.random() > 0.3 else tuple(int(c * 0.75) for c in dates)
                d.ellipse([bx + dx - rr, by + dy - rr * 1.3, bx + dx + rr, by + dy + rr * 1.3], fill=col + (255,))
    # fronds
    for k in range(fronds):
        base_ang = -math.pi / 2 + (k / (fronds - 1) - 0.5) * math.pi * 1.55 + r.uniform(-0.1, 0.1)
        L = h * S * r.uniform(0.3, 0.42)
        droop = r.uniform(0.35, 0.8) * L * (0.6 + abs(math.sin(base_ang + math.pi / 2)))
        pts = []
        for i in range(24):
            s = i / 23
            x = cx + math.cos(base_ang) * L * s
            y = cy + math.sin(base_ang) * L * s + droop * s * s
            pts.append((x, y))
        for i in range(len(pts) - 1):
            wdt = int(lerp(0.012, 0.002, i / 23) * h * S) + 1
            d.line([pts[i], pts[i + 1]], fill=color + (255,), width=wdt)
        # leaflets
        for i in range(2, len(pts) - 1):
            s = i / 23
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            tx, ty = x1 - x0, y1 - y0
            tl = math.hypot(tx, ty) + 1e-6
            tx, ty = tx / tl, ty / tl
            ll = L * 0.2 * math.sin(math.pi * (0.15 + 0.85 * s)) * r.uniform(0.8, 1.1)
            for side in (-1, 1):
                a = 0.9 * side
                ex = tx * math.cos(a) - ty * math.sin(a)
                ey = tx * math.sin(a) + ty * math.cos(a)
                ey += 0.55  # gravity
                el = math.hypot(ex, ey)
                d.line([(x0, y0), (x0 + ex / el * ll, y0 + ey / el * ll)], fill=color + (255,), width=max(1, int(0.004 * h * S)))
    return im.resize((Wc // S, Hc // S), Image.LANCZOS)

# --------------------------------------------------------------- scenes
_cache = {}
def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]

def dune_layer(seed, y0, amp, color, h=H, w=W):
    r = np.random.default_rng(seed)
    x = np.arange(w)
    ph = r.uniform(0, 6, 4)
    y = y0 + amp * (0.6 * np.sin(x / w * 2.3 + ph[0]) + 0.3 * np.sin(x / w * 5.1 + ph[1]) + 0.1 * np.sin(x / w * 11 + ph[2]))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(0, h)] + list(zip(x.tolist(), y.tolist())) + [(w, h)], fill=color + (255,))
    return im

def palms_row(seed, n, hmin, hmax, y, color, dates=None, spread=(-100, W + 100)):
    r = random.Random(seed)
    im = Image.new("RGBA", (W + 400, H), (0, 0, 0, 0))
    xs = sorted(r.uniform(*spread) for _ in range(n))
    for i, x in enumerate(xs):
        hh = int(r.uniform(hmin, hmax))
        p = make_palm(hh, seed * 100 + i, color, dates)
        im.alpha_composite(p, (int(x + 200 - p.width / 2), int(y - p.height)))
    return im

STARS = [(random.Random(i).uniform(0, W), random.Random(i + 999).uniform(0, H * 0.55), random.Random(i + 7).uniform(0.6, 2.4), random.Random(i + 3).uniform(0, 6.28)) for i in range(260)]

def scene_dawn(t, fi):
    """0–5.5s: Qassim before dawn → sunrise over palm groves."""
    p = prog(t, 0, 5.6)
    sky = multi_grad([
        (0.0, lerpc((8, 12, 34), (46, 52, 104), p)),
        (0.45, lerpc((22, 26, 60), (196, 110, 96), p)),
        (0.62, lerpc((40, 36, 70), (250, 170, 96), p)),
        (1.0, lerpc((30, 24, 40), (120, 60, 50), p)),
    ])
    sun_y = lerp(1300, 1020, ease_out(p))
    glow = radial(W * 0.5, sun_y, 900) ** 2.2 * (0.25 + 0.75 * p)
    sky += glow[..., None] * np.array([255, 170, 80], np.float32) * 0.9
    fr = to_img(sky)
    d = ImageDraw.Draw(fr)
    sa = 1 - ease_in_out(prog(t, 0.5, 4.5))
    for (x, y, s, ph) in STARS:
        tw = 0.6 + 0.4 * math.sin(t * 3 + ph)
        a = int(255 * sa * tw)
        if a > 4:
            d.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=(255, 245, 230, a))
    # sun disc
    sd = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sd).ellipse([W / 2 - 120, sun_y - 120, W / 2 + 120, sun_y + 120], fill=(255, 226, 170, int(255 * clamp(p * 1.4))))
    fr.alpha_composite(sd.filter(ImageFilter.GaussianBlur(3)))
    cam = ease_in_out(p)
    far = cached("dune_far", lambda: dune_layer(3, 1180, 40, (92, 52, 58)))
    fr.alpha_composite(far, (0, int(-cam * 20)))
    pr2 = cached("palms_far", lambda: palms_row(11, 14, 220, 330, 1250, (58, 30, 42)))
    fr.alpha_composite(pr2, (int(-200 - cam * 30), int(-cam * 30)))
    mid = cached("dune_mid", lambda: dune_layer(5, 1330, 55, (44, 22, 30)))
    fr.alpha_composite(mid, (0, int(-cam * 50)))
    pr1 = cached("palms_near", lambda: palms_row(21, 5, 620, 900, 1640, (18, 10, 16), spread=(-160, W + 160)))
    fr.alpha_composite(pr1, (int(-200 - cam * 90), int(-cam * 80)))
    near = cached("dune_near", lambda: dune_layer(9, 1620, 45, (14, 8, 12)))
    fr.alpha_composite(near, (0, int(-cam * 110)))
    # atmospheric haze
    haze = radial(W / 2, sun_y, 1400) * 0.25 * p
    arr = np.asarray(fr, dtype=np.float32)
    arr[..., :3] += haze[..., None] * np.array([255, 190, 120])
    fr = to_img(arr[..., :3])
    # type
    put_text(fr, "القصيم", KUFI, 150, W / 2, 420, CREAM, 1.5, t, 1.0, "Bold", glow=(255, 190, 110, 150))
    put_text(fr, "حكايةٌ بدأت منذ الستينات", AMIRI, 64, W / 2, 575, GOLD_L, 2.6, t, 1.0)
    return fr

MEM_SKY = None
def scene_memory(t, fi):
    """5.5–11s: sepia memory — a 7-year-old walks with his father among the palms."""
    lt = t - 5.3
    p = prog(lt, 0, 5.8)
    sky = multi_grad([(0, (120, 72, 40)), (0.5, (236, 170, 96)), (0.7, (250, 206, 140)), (1, (150, 90, 50))])
    sky += (radial(W * 0.62, 900, 700) ** 2)[..., None] * np.array([255, 230, 170], np.float32) * 0.8
    fr = to_img(sky)
    back = cached("mem_back", lambda: palms_row(41, 10, 380, 520, 1360, (120, 70, 40), spread=(-100, W + 300)))
    fr.alpha_composite(back, (int(-200 - p * 60), 0))
    ground = cached("mem_ground", lambda: dune_layer(12, 1360, 18, (96, 56, 32)))
    fr.alpha_composite(ground)
    mid = cached("mem_mid", lambda: palms_row(43, 3, 700, 850, 1440, (70, 40, 22), dates=(150, 70, 30), spread=(-260, 60)))
    fr.alpha_composite(mid, (int(-200 + p * 120), 0))
    mid2 = cached("mem_mid2", lambda: palms_row(44, 2, 760, 900, 1440, (70, 40, 22), dates=(150, 70, 30), spread=(W + 40, W + 260)))
    fr.alpha_composite(mid2, (int(-200 + p * 120), 0))
    # father & son silhouettes walking right-to-left, hand in hand
    S = 2
    fig = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    col = (34, 18, 10, 255)
    x0 = lerp(700, 470, p)
    gy = 1548
    hands = []
    for (bx, hh, ph, adult) in ((x0, 560, 0.0, True), (x0 + 175, 330, 1.7, False)):
        step = lt * 4.2 + ph
        bob = abs(math.sin(step)) * hh * 0.015
        top = gy - hh - bob
        hr = hh * 0.068
        sh_y = top + hr * 2.6
        sw = math.sin(step) * hh * 0.035
        P = lambda pts: [(x * S, y * S) for x, y in pts]
        # thobe: shoulders -> hem, slight flare, hem swings with the stride
        d.polygon(P([(bx - hh * 0.105, sh_y), (bx + hh * 0.105, sh_y), (bx + hh * 0.12, sh_y + hh * 0.3),
                     (bx + hh * 0.13 + sw, gy - bob * 0.3), (bx - hh * 0.13 + sw * 0.4, gy - bob * 0.3), (bx - hh * 0.12, sh_y + hh * 0.3)]), fill=col)
        d.ellipse(P([(bx - hh * 0.11, sh_y - hr * 0.5), (bx + hh * 0.11, sh_y + hr * 1.2)]), fill=col)
        # feet peeking under hem
        fx = math.sin(step) * hh * 0.06
        d.ellipse(P([(bx - hh * 0.07 - fx, gy - hh * 0.02), (bx + hh * 0.01 - fx, gy + hh * 0.01)]), fill=col)
        d.ellipse(P([(bx - hh * 0.01 + fx, gy - hh * 0.02), (bx + hh * 0.07 + fx, gy + hh * 0.01)]), fill=col)
        # neck + head
        d.rectangle(P([(bx - hr * 0.45, top + hr * 1.6), (bx + hr * 0.45, sh_y)]), fill=col)
        d.ellipse(P([(bx - hr, top), (bx + hr, top + hr * 2.2)]), fill=col)
        if adult:
            # ghutra + agal: cloth falls behind the shoulders, flutters in the breeze
            fl = math.sin(lt * 3.0) * hr * 0.25
            d.polygon(P([(bx - hr * 1.05, top + hr * 0.35), (bx + hr * 1.05, top + hr * 0.35), (bx + hr * 1.35 + fl, sh_y + hr * 1.6),
                         (bx + hr * 0.2, sh_y + hr * 0.6), (bx - hr * 1.5, sh_y + hr * 1.3)]), fill=col)
            d.ellipse(P([(bx - hr * 1.12, top - hr * 0.12), (bx + hr * 1.12, top + hr * 0.75)]), fill=col)
        else:
            d.ellipse(P([(bx - hr * 1.05, top - hr * 0.05), (bx + hr * 1.05, top + hr * 0.9)]), fill=col)  # taqiyah
        # arm reaching toward the other figure
        side = 1 if adult else -1
        shx, shy = bx + side * hh * 0.1, sh_y + hr * 0.4
        hx, hy = bx + side * hh * 0.24, sh_y + hh * (0.28 if adult else 0.26)
        hands.append((hx, hy))
        d.line(P([(shx, shy), ((shx + hx) / 2 + side * hh * 0.02, (shy + hy) / 2), (hx, hy)]), fill=col, width=int(hh * 0.05 * S), joint="curve")
        # other arm swinging
        ox = bx - side * hh * 0.1
        d.line(P([(ox, shy), (ox - side * hh * 0.03 + math.sin(step) * hh * 0.05, sh_y + hh * 0.3)]), fill=col, width=int(hh * 0.045 * S), joint="curve")
    (ax, ay), (cx2, cy2) = hands
    mx, my = (ax + cx2) / 2, max(ay, cy2) + 6
    d.line([(ax * S, ay * S), (mx * S, my * S), (cx2 * S, cy2 * S)], fill=col, width=int(20 * S), joint="curve")
    d.ellipse([(mx - 14) * S, (my - 14) * S, (mx + 14) * S, (my + 14) * S], fill=col)
    fig = fig.resize((W, H), Image.LANCZOS)
    # long evening shadows
    shd = fig.transform((W, H), Image.AFFINE, (1, 1.6, -1.6 * gy, 0, 3.2, -2.2 * gy), Image.BILINEAR)
    shd_a = shd.getchannel("A").point(lambda v: int(v * 0.35))
    sh_img = Image.new("RGBA", (W, H), (30, 14, 6, 0)); sh_img.putalpha(shd_a)
    fr.alpha_composite(sh_img)
    fr.alpha_composite(fig)
    fg = cached("mem_fg", lambda: dune_layer(13, 1560, 12, (46, 24, 12)))
    fr.alpha_composite(fg)
    front = cached("mem_front", lambda: palms_row(47, 1, 1700, 1701, 2150, (24, 12, 8), spread=(0, 1)))
    fr.alpha_composite(front, (int(-200 + W + 60 - p * 160), 0))
    # sepia + light leak
    arr = np.asarray(fr.convert("RGB"), dtype=np.float32)
    lum = arr @ np.array([0.3, 0.59, 0.11], np.float32)
    sep = np.stack([lum * 1.08 + 18, lum * 0.86 + 8, lum * 0.62], -1)
    arr = arr * 0.35 + sep * 0.65
    leak = radial(W * (0.1 + 0.2 * math.sin(lt)), 300, 900) ** 2 * (0.35 + 0.15 * math.sin(lt * 2))
    arr += leak[..., None] * np.array([255, 120, 60])
    # flicker
    arr *= 0.96 + 0.04 * math.sin(fi * 2.7)
    fr = to_img(arr)
    # frame scratches
    d = ImageDraw.Draw(fr)
    rr = random.Random(fi // 2)
    for _ in range(2):
        x = rr.uniform(0, W)
        d.line([(x, 0), (x + rr.uniform(-10, 10), H)], fill=(255, 240, 210, 40), width=1)
    put_text(fr, "في السابعة من عمره", AMIRI, 76, W / 2, 330, CREAM, 5.9, t, 0.9)
    put_text(fr, "خلف أبيه.. بين النخيل", AMIRI, 76, W / 2, 440, CREAM, 6.9, t, 0.9)
    put_text(fr, "الأرضُ أمانة", RUQAA, 120, W / 2, 640, GOLD_L, 9.6, t, 1.0, glow=(255, 180, 90, 170))
    return fr

def draw_wheat(d, x, base_y, h, sway, col_stem, col_head, wdt):
    pts = []
    for i in range(12):
        s = i / 11
        pts.append((x + sway * s * s * h, base_y - h * s))
    d.line(pts, fill=col_stem, width=wdt, joint="curve")
    (px, py), (hx, hy) = pts[-2], pts[-1]
    ux, uy = hx - px, hy - py
    n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
    ear = h * 0.16
    g = max(1.6, h * 0.0085)
    for j in range(11):
        f = j / 10
        cx, cy = hx + ux * ear * f, hy + uy * ear * f
        r = g * (1.15 - 0.55 * f)
        for sd in (-1, 1):
            ox, oy = -uy * sd * r * 0.9, ux * sd * r * 0.9
            d.ellipse([cx + ox - r * 0.8, cy + oy - r * 1.3, cx + ox + r * 0.8, cy + oy + r * 1.3], fill=col_head)
            ax, ay = ux * 0.95 - uy * sd * 0.3, uy * 0.95 + ux * sd * 0.3
            if j % 2 == 0:
                d.line([(cx + ox, cy + oy), (cx + ox + ax * ear * 0.6, cy + oy + ay * ear * 0.6)], fill=col_head[:3] + (170,), width=2)

WHEAT = [(random.Random(i).uniform(-80, W + 80), random.Random(i + 5).random(), random.Random(i + 9).uniform(0, 6.28)) for i in range(170)]

def scene_wheat(t, fi):
    """11–15.8s: golden wheat, no chemicals, the old way."""
    lt = t - 10.8
    p = prog(lt, 0, 5.0)
    sky = multi_grad([(0, (110, 160, 205)), (0.4, (246, 212, 150)), (0.6, (255, 196, 116)), (1, (150, 96, 40))])
    sun = radial(W * 0.32, 1060, 520) ** 1.6
    sky += sun[..., None] * np.array([255, 240, 200], np.float32)
    fr = to_img(sky)
    far = cached("w_far", lambda: palms_row(61, 16, 200, 300, 1230, (150, 110, 80), spread=(-100, W + 300)))
    fr.alpha_composite(far, (int(-200 - p * 30), 0))
    field = multi_grad([(0, (226, 170, 80)), (0.4, (196, 136, 50)), (1, (110, 70, 24))], h=H - 1220)
    fr.alpha_composite(to_img(field), (0, 1220))
    S = 2
    top = 500
    lay = Image.new("RGBA", (W * S, (H - top) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for (x, z, ph) in sorted(WHEAT, key=lambda w: w[1]):
        depth = z
        h = (260 + 860 * depth ** 1.5) * S
        base = (H - top + 60) * S - (1 - depth) * 520 * S
        sway = 0.06 * math.sin(lt * 1.5 + ph + x * 0.004) + 0.025 * math.sin(lt * 3.3 + ph) + (ph - 3.14) * 0.03
        cs = lerpc((214, 170, 96), (120, 80, 26), depth)
        ch = lerpc((250, 222, 150), (196, 128, 40), depth)
        xx = (x - p * 50 * depth) * S
        draw_wheat(d, xx, base, h, sway, cs + (255,), ch + (255,), max(2, int((1.5 + 3 * depth) * S)))
    lay = lay.resize((W, H - top), Image.LANCZOS)
    fr.alpha_composite(lay, (0, top))
    arr = np.asarray(fr.convert("RGB"), dtype=np.float32)
    arr += (radial(W * 0.32, 1060, 1100) ** 3)[..., None] * np.array([140, 90, 30])
    fr = to_img(arr)
    d = ImageDraw.Draw(fr)
    for i in range(70):
        r = random.Random(i + 500)
        x = (r.uniform(0, W) + lt * r.uniform(10, 40)) % W
        y = (r.uniform(0, H) - lt * r.uniform(15, 50)) % H
        s = r.uniform(2, 6)
        d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 240, 200, int(120 * r.random())))
    put_text(fr, "بلا كيماويات", KUFI, 110, W / 2, 300, (255, 250, 240), 11.2, t, 0.8, "Bold", glow=(120, 60, 10, 140))
    put_text(fr, "بلا استعجال", KUFI, 110, W / 2, 440, (255, 250, 240), 12.4, t, 0.8, "Bold", glow=(120, 60, 10, 140))
    put_text(fr, "كما زرعها الأجداد", AMIRI, 70, W / 2, 585, INK, 13.6, t, 0.9, glow=(255, 240, 200, 160))
    return fr

# ---------------------------------------------------------- product shots
@lru_cache(None)
def product_card(name, cw=780):
    im = Image.open(os.path.join(IMG, name)).convert("RGB")
    ch = int(cw * im.height / im.width)
    im = im.resize((cw, ch), Image.LANCZOS)
    im = ImageEnhance.Sharpness(im).enhance(1.4)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return im

@lru_cache(None)
def blurred_bg(name):
    im = Image.open(os.path.join(IMG, name)).convert("RGB")
    im = ImageOps.fit(im, (W // 4, H // 4))
    im = im.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    arr = np.asarray(im, np.float32) * 0.45 + np.array(MAROON_D, np.float32) * 0.55
    return to_img(arr)

def rounded_mask(w, h, r):
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], r * 2, fill=255)
    return m.resize((w, h), Image.LANCZOS)

@lru_cache(None)
def card_shadow(w, h):
    s = Image.new("RGBA", (w + 200, h + 200), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle([100, 120, w + 100, h + 120], 40, fill=(0, 0, 0, 170))
    return s.filter(ImageFilter.GaussianBlur(30))

@lru_cache(None)
def arch_pattern():
    """Brand arch motif (from the logo) as a subtle repeating pattern."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for row in range(-1, 12):
        for col in range(-1, 7):
            x = col * 200 + (100 if row % 2 else 0)
            y = row * 200
            d.rounded_rectangle([x + 40, y + 30, x + 160, y + 190], 60, outline=(255, 230, 190, 16), width=3)
    return im

def sparkles(fr, t, seed, n=40, area=(0, 0, W, H), col=(255, 226, 160)):
    d = ImageDraw.Draw(fr)
    for i in range(n):
        r = random.Random(seed * 1000 + i)
        x = r.uniform(area[0], area[2]) + math.sin(t * r.uniform(0.5, 1.5) + i) * 20
        y = (r.uniform(area[1], area[3]) - t * r.uniform(20, 70)) % (area[3] - area[1]) + area[1]
        tw = 0.5 + 0.5 * math.sin(t * r.uniform(2, 6) + i)
        s = r.uniform(1.5, 5) * (0.6 + 0.4 * tw)
        a = int(200 * tw)
        d.ellipse([x - s, y - s, x + s, y + s], fill=col + (a,))
        if s > 4:
            d.line([(x - s * 3, y), (x + s * 3, y)], fill=col + (a // 2,), width=1)
            d.line([(x, y - s * 3), (x, y + s * 3)], fill=col + (a // 2,), width=1)

PRODUCTS = [
    # (start, end, image, name, sub, section)
    (15.6, 17.35, "winana.jpg", "الونّانة", "تمر عضوي", "من نخيلنا"),
    (17.35, 18.6, "khalas.jpg", "الخلاص", "تمر عضوي", "من نخيلنا"),
    (18.6, 20.3, "dibs.jpg", "دبس التمر", "عضوي ١٠٠٪", "من نخيلنا"),
    (20.3, 22.35, "burr.jpg", "دقيق البُرّ", "قمح عضوي أسمر", "من حقولنا"),
    (22.35, 23.4, "jareesh.jpg", "الجريش", "عضوي", "من حقولنا"),
    (23.4, 24.35, "talbina.jpg", "التلبينة", "عضوية", "من حقولنا"),
    (24.35, 25.9, "coffee.jpg", "قهوة الشعير", "عضوية", "من حقولنا"),
    (25.9, 28.55, "matazeez.jpg", "المطازيز", "عضوية", "على سُفرتكم"),
    (28.55, 30.3, "maamoul.jpg", "معمول الهجرسية", "بتمرنا العضوي", "على سُفرتكم"),
]

def scene_products(t, fi):
    cur = None
    for i, pr in enumerate(PRODUCTS):
        if pr[0] <= t < pr[1] or (i == len(PRODUCTS) - 1 and t >= pr[0]):
            cur = i
    if cur is None:
        cur = 0
    s0, s1, img, name, sub, sec = PRODUCTS[cur]
    lt = t - s0
    dur = s1 - s0
    fr = blurred_bg(img).copy()
    fr.alpha_composite(arch_pattern(), (0, int(-(t * 20) % 200)))
    # warm spotlight behind card
    arr = np.asarray(fr.convert("RGB"), np.float32)
    arr += (radial(W / 2, 900, 900) ** 2)[..., None] * np.array([120, 70, 40])
    fr = to_img(arr)
    sparkles(fr, t, cur + 3, 30)
    # section header (persists through a section; animates on section change)
    sec_start = min(p[0] for p in PRODUCTS if p[5] == sec)
    put_text(fr, sec, KUFI, 96, W / 2, 250, GOLD_L, sec_start, t, 0.6, "Bold", glow=(0, 0, 0, 90))
    # gold rule under header
    hp = ease_out(prog(t, sec_start + 0.1, sec_start + 0.8))
    d = ImageDraw.Draw(fr)
    d.line([(W / 2 - 200 * hp, 335), (W / 2 + 200 * hp, 335)], fill=GOLD + (220,), width=3)
    d.ellipse([W / 2 - 7, 328, W / 2 + 7, 342], fill=GOLD + (int(255 * hp),))
    # card: push-in from left (RTL flow), ken burns inside
    card = product_card(img)
    cw, ch = card.size
    ch_vis = min(ch, 1040)
    zoom = 1.0 + 0.08 * (lt / dur)
    zc = card.resize((int(cw * zoom), int(ch * zoom)), Image.BILINEAR)
    ox, oy = (zc.width - cw) // 2, (zc.height - ch_vis) // 2
    zc = zc.crop((ox, oy, ox + cw, oy + ch_vis)).convert("RGBA")
    # light sweep
    sw = prog(lt, 0.25, 1.1)
    if 0 < sw < 1:
        band = Image.new("L", zc.size, 0)
        bx = lerp(-300, cw + 300, sw)
        ImageDraw.Draw(band).polygon([(bx, 0), (bx + 90, 0), (bx - 110, ch_vis), (bx - 200, ch_vis)], fill=90)
        band = band.filter(ImageFilter.GaussianBlur(25))
        white = Image.new("RGBA", zc.size, (255, 250, 235, 0))
        white.putalpha(band)
        zc.alpha_composite(white)
    zc.putalpha(rounded_mask(cw, ch_vis, 40))
    frame_l = Image.new("RGBA", (cw + 24, ch_vis + 24), (0, 0, 0, 0))
    ImageDraw.Draw(frame_l).rounded_rectangle([0, 0, cw + 23, ch_vis + 23], 50, fill=GOLD_L + (255,))
    frame_l.alpha_composite(zc, (12, 12))
    enter = ease_back(prog(lt, 0, 0.45), 1.2) if cur != 0 else ease_out(prog(lt, 0, 0.6))
    leave = ease_in_out(prog(lt, dur - 0.28, dur)) if cur != len(PRODUCTS) - 1 else 0
    cx = W / 2 + (1 - enter) * -W * 0.9 + leave * W * 0.9
    rot = (1 - enter) * 6 - leave * 6
    cy = 960
    lay = frame_l
    if abs(rot) > 0.05:
        lay = lay.rotate(rot, Image.BICUBIC, expand=True)
    shadow = card_shadow(frame_l.width, frame_l.height)
    fr.alpha_composite(shadow, (int(cx - shadow.width / 2 + 10), int(cy - shadow.height / 2 + 20)))
    fr.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))
    # organic badge on card corner
    bp = ease_back(prog(lt, 0.35, 0.75), 2.5)
    if bp > 0:
        badge = organic_badge()
        paste_center(fr, badge, cx - cw / 2 + 40, cy - ch_vis / 2 + 40, clamp(bp) * (1 - leave), max(0.01, bp))
    # name + sub
    ty = cy + ch_vis / 2 + 140
    put_text(fr, name, RUQAA, 132, W / 2, ty, CREAM, s0 + 0.2, t, 0.55, out_t=(s1 - 0.3) if cur != len(PRODUCTS) - 1 else None, glow=(0, 0, 0, 120))
    put_text(fr, sub, TAJ, 52, W / 2, ty + 120, GOLD_L, s0 + 0.4, t, 0.5, out_t=(s1 - 0.3) if cur != len(PRODUCTS) - 1 else None)
    return fr

@lru_cache(None)
def organic_badge():
    S = 2
    r = 95 * S
    im = Image.new("RGBA", (r * 2 + 8, r * 2 + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = r + 4
    d.ellipse([c - r, c - r, c + r, c + r], fill=MAROON + (255,))
    d.ellipse([c - r + 10, c - r + 10, c + r - 10, c + r - 10], outline=GOLD + (255,), width=4 * S)
    # scalloped ring
    for k in range(24):
        a = k / 24 * 2 * math.pi
        x, y = c + math.cos(a) * (r - 2), c + math.sin(a) * (r - 2)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=MAROON + (255,))
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    t1 = text_img("عضوي", KUFI, 50, GOLD_L, "Bold", False)
    t2 = text_img("ORGANIC", TAJ, 22, CREAM, None, False)
    im.alpha_composite(t1, (im.width // 2 - t1.width // 2, im.height // 2 - t1.height // 2 - 12))
    im.alpha_composite(t2, (im.width // 2 - t2.width // 2, im.height // 2 - t2.height // 2 + 30))
    return im

# ------------------------------------------------------------- award
@lru_cache(None)
def medal():
    S = 2
    R = 230 * S
    size = R * 2 + 200 * S
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    # laurel wreath
    for side in (-1, 1):
        for k in range(15):
            a = math.radians(110 + k * 10.5)
            rr = R + 55 * S
            x, y = c + side * math.cos(a) * rr * -1, c + math.sin(a) * rr * -1
            x = c - side * math.cos(a) * rr
            y = c - math.sin(a) * rr * -1
            ang = math.degrees(a) * side
            leaf = Image.new("RGBA", (70 * S, 30 * S), (0, 0, 0, 0))
            ImageDraw.Draw(leaf).ellipse([0, 0, 70 * S - 1, 30 * S - 1], fill=GOLD + (255,))
            leaf = leaf.rotate(-ang + (90 if side > 0 else -90) + 30 * side, Image.BICUBIC, expand=True)
            im.alpha_composite(leaf, (int(x - leaf.width / 2), int(y - leaf.height / 2)))
    # disc
    yy, xx = np.mgrid[:size, :size]
    dist = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    shade = np.clip(0.75 + 0.35 * ((c - yy) + (c - xx)) / (2 * R), 0.4, 1.3)
    disc = np.zeros((size, size, 4), np.float32)
    disc[..., :3] = np.array(GOLD, np.float32) * shade[..., None]
    ring = (np.abs(dist - R * 0.86) < 6 * S)
    disc[ring, :3] = np.array(GOLD_L)
    disc[..., 3] = np.clip((R - dist) * 2, 0, 1) * 255
    dimg = Image.fromarray(np.clip(disc, 0, 255).astype(np.uint8), "RGBA")
    im.alpha_composite(dimg)
    im = im.resize((size // S, size // S), Image.LANCZOS)
    palm = make_palm(230, 5, MAROON_D, None, 14)
    im.alpha_composite(palm, (im.width // 2 - palm.width // 2, im.height // 2 - palm.height // 2 + 10))
    return im

def scene_award(t, fi):
    lt = t - 30.3
    fr = blurred_bg("sukari.jpg").copy()
    arr = np.asarray(fr.convert("RGB"), np.float32) * 0.7
    # rotating god rays
    ang = np.arctan2(YY - 820, XX - W / 2)
    rays = (0.5 + 0.5 * np.sin(ang * 16 + lt * 0.6)) ** 6
    rays *= np.clip(1 - np.sqrt((XX - W / 2) ** 2 + (YY - 820) ** 2) / 1300, 0, 1)
    arr += rays[..., None] * np.array([180, 120, 50]) * ease_out(prog(lt, 0, 1.0))
    arr += (radial(W / 2, 820, 700) ** 2)[..., None] * np.array([160, 100, 40])
    fr = to_img(arr)
    sparkles(fr, t, 99, 70, col=(255, 230, 170))
    bp_in = ease_back(prog(lt, 0.4, 1.1), 1.6)
    bp_out = ease_in_out(prog(lt, 2.3, 2.7))
    if bp_in > 0 and bp_out < 1:
        paste_center(fr, organic_badge(), W / 2, 880, clamp(bp_in) * (1 - bp_out), max(0.01, 2.7 * bp_in * (1 - 0.4 * bp_out) * (1 + 0.01 * math.sin(lt * 4))))
    mp = ease_back(prog(lt, 2.6, 3.4), 1.8)
    if mp > 0:
        m = medal()
        wob = 1 + 0.015 * math.sin(lt * 3)
        paste_center(fr, m, W / 2, 820, clamp(mp * 1.5), max(0.01, mp * wob))
    put_text(fr, "الجائزة الكبرى", KUFI, 116, W / 2, 1290, GOLD_L, 33.2, t, 0.7, "Bold", glow=(120, 60, 0, 200))
    put_text(fr, "جائزة جميل للتمور ٢٠٢٦", AMIRI, 66, W / 2, 1420, CREAM, 33.7, t, 0.7)
    put_text(fr, "موثّقة عالمياً ومحلياً", KUFI, 88, W / 2, 300, CREAM, 30.6, t, 0.7, "Bold", glow=(0, 0, 0, 120))
    # certificate chips
    cp = ease_out(prog(lt, 0.9, 1.5))
    if cp > 0:
        chips = ["زراعة عضوية", "إنتاج حيواني عضوي"]
        for i, c in enumerate(chips):
            lay = chip(c)
            paste_center(fr, lay, W / 2 + (1 - 2 * i) * 220, 440 + (1 - cp) * 30, cp)
    return fr

@lru_cache(None)
def chip(text):
    tl = text_img(text, TAJ, 38, CREAM, None, False)
    w, h = tl.width - 20, 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], 40, fill=MAROON + (235,), outline=GOLD + (255,), width=3)
    im.alpha_composite(tl, (w // 2 - tl.width // 2, h // 2 - tl.height // 2))
    return im

# ------------------------------------------------------------- end card
@lru_cache(None)
def logo_img():
    lg = Image.open(os.path.join(IMG, "logo.png")).convert("RGBA")
    a = np.asarray(lg, np.float32)
    # knock out the white background: keep maroon ink, alpha from darkness
    alpha = np.clip((a[..., 0] - a[..., 1] - 12) / 70, 0, 1)
    # remove outer grey circle area (outside) — keep ink only
    out = np.zeros_like(a)
    out[..., :3] = np.array(MAROON, np.float32)
    out[..., 3] = alpha * 255
    im = Image.fromarray(out.astype(np.uint8), "RGBA")
    bb = im.getbbox()
    return im.crop(bb)

def scene_end(t, fi):
    lt = t - 35.8
    base = multi_grad([(0, (252, 244, 230)), (0.6, CREAM), (1, (236, 214, 184))])
    base += (radial(W / 2, 800, 900) ** 2)[..., None] * np.array([6, 6, 4])
    fr = to_img(base)
    pat = arch_pattern()
    # tint pattern maroon at low alpha
    pa = Image.new("RGBA", (W, H), MAROON + (0,))
    pa.putalpha(pat.getchannel("A").point(lambda v: min(255, v * 2)))
    fr.alpha_composite(pa, (0, int(-lt * 15) % 200 - 200))
    # palms silhouettes at the bottom, rising
    rise = ease_out(prog(lt, 0, 1.2))
    row = cached("end_palms", lambda: palms_row(71, 7, 260, 420, H + 10, (150, 70, 70)))
    fr.alpha_composite(with_alpha(row, 0.35), (-200, int((1 - rise) * 300)))
    band = Image.new("RGBA", (W, 200), MAROON + (255,))
    fr.alpha_composite(band, (0, H - 200 + int((1 - rise) * 200)))
    # logo
    lp = ease_back(prog(lt, 0.15, 0.9), 1.6)
    if lp > 0:
        lg = logo_img()
        sc = 640 / lg.width * max(0.01, lp)
        paste_center(fr, lg, W / 2, 760, clamp(lp * 1.6), sc)
    # shine across logo
    tag = text_img("من أرضِنا.. إلى سُفرتِكم", RUQAA, 92, MAROON, None, False)
    if t > 38.1:
        p = ease_out(prog(t, 38.1, 39.1))
        paste_center(fr, wipe_rtl(tag, p), W / 2, 1300 + (1 - p) * 30, p)
    # url pill
    up = ease_back(prog(lt, 3.9, 4.5), 1.6)
    if up > 0:
        ul = url_pill()
        paste_center(fr, ul, W / 2, 1480, clamp(up), max(0.01, up))
    ip = ease_out(prog(lt, 4.5, 5.1))
    if ip > 0:
        feat = text_img("شحن مبرّد  •  استلام من المتجر", TAJ, 44, CREAM, None, False)
        paste_center(fr, feat, W / 2, H - 100, ip)
    sparkles(fr, t, 5, 20, area=(0, 300, W, 1400), col=GOLD)
    return fr

@lru_cache(None)
def url_pill():
    tl = text_img("alhajraciyah.com", TAJ, 62, CREAM, None, False)
    w, h = tl.width + 40, 118
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], 59, fill=MAROON + (255,), outline=GOLD + (255,), width=4)
    im.alpha_composite(tl, (w // 2 - tl.width // 2, h // 2 - tl.height // 2 - 4))
    return im

# ------------------------------------------------------------- timeline
SCENES = [
    (0.0, 5.3, scene_dawn),
    (5.3, 10.8, scene_memory),
    (10.8, 15.6, scene_wheat),
    (15.6, 30.3, scene_products),
    (30.3, 35.8, scene_award),
    (35.8, DUR + 1, scene_end),
]
XF = 0.35  # crossfade

def render(fi):
    t = fi / FPS
    frame = None
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b:
            frame = fn(t, fi)
            # dissolve into next scene's first frames
            if i + 1 < len(SCENES) and t > b - XF:
                nxt = SCENES[i + 1][2](t, fi)
                k = ease_in_out((t - (b - XF)) / XF)
                frame = Image.blend(frame, nxt, k)
            break
    # white flash on the award & logo hits
    for hit in (30.3, 33.0, 35.8):
        if hit <= t < hit + 0.25:
            k = 1 - (t - hit) / 0.25
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 244, 220, 255)), 0.6 * k)
    fade_in = clamp(t / 0.8)
    fade_out = 1 - clamp((t - (DUR - 0.6)) / 0.6)
    arr = finish(frame, fi, grain=5.0, vig=0.8 if t < 35.8 else 0.35)
    k = fade_in * fade_out
    if k < 1:
        arr = (arr.astype(np.float32) * k).astype(np.uint8)
    return arr

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for tt in sys.argv[2:]:
            fi = int(float(tt) * FPS)
            Image.fromarray(render(fi)).save(os.path.join(BASE, f"still_{tt}.jpg"), quality=88)
    else:
        from multiprocessing import Pool
        out = sys.argv[2]
        n = int(DUR * FPS)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for i, arr in enumerate(pool.imap(render, range(n), chunksize=4)):
                ff.stdin.write(arr.tobytes())
                if i % 60 == 0:
                    print(i, "/", n, flush=True)
        ff.stdin.close(); ff.wait()

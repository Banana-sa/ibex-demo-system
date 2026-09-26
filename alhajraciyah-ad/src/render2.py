"""Al-Hajraciyah ad v2 — generated photoreal scenes + product heroes (1080x1920 @30fps, 45.5s).
Reuses the helpers/type system from render.py."""
import sys, os, math, random, subprocess
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import render as R
from render import (W, H, FPS, clamp, prog, ease_out, ease_in_out, ease_back, lerp, lerpc, text_img, wipe_rtl,
                    with_alpha, paste_center, put_text, radial, to_img, multi_grad, finish, sparkles, organic_badge,
                    medal, chip, logo_img, url_pill, arch_pattern, palms_row, cached,
                    KUFI, AMIRI, RUQAA, TAJ, MAROON, MAROON_D, GOLD, GOLD_L, CREAM, INK)

DUR = 45.5
GEN = os.path.join(R.BASE, "gen")
T_PROD, T_AWARD, T_MEDAL, T_LOGO = 15.6, 31.7, 36.0, 39.3
OVER = 1.14  # oversize factor for camera moves

@lru_cache(None)
def plate(name):
    """Cover-fit the generated image at OVER× frame size, gently sharpened."""
    im = Image.open(os.path.join(GEN, name + ".png")).convert("RGB")
    im = ImageOps.fit(im, (int(W * OVER), int(H * OVER)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(2.2, 70, 2))
    return im

def camera(name, k, z0=1.0, z1=1.1, fx=0.5, fy=0.5, dx=0.0, dy=0.0):
    """Ken Burns: zoom z0→z1 about focus (fx,fy), with drift (dx,dy) in frame fractions, k in 0..1."""
    im = plate(name)
    z = lerp(z0, z1, k)
    sw, sh = im.width / z, im.height / z
    cx = im.width * fx + dx * W * k
    cy = im.height * fy + dy * H * k
    x0 = clamp(cx - sw / 2, 0, im.width - sw)
    y0 = clamp(cy - sh / 2, 0, im.height - sh)
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + sw, y0 + sh), Image.BICUBIC).convert("RGBA")

@lru_cache(None)
def grad_mask(top_px, bot_px, top_a=200, bot_a=235):
    y = np.arange(H, dtype=np.float32)
    a = np.clip(1 - y / top_px, 0, 1) ** 1.6 * top_a + np.clip((y - (H - bot_px)) / bot_px, 0, 1) ** 1.4 * bot_a
    m = np.repeat(a[:, None], W, 1).astype(np.uint8)
    im = Image.new("RGBA", (W, H), (18, 6, 8, 0))
    im.putalpha(Image.fromarray(m))
    return im

def grade(fr, mult=(1, 1, 1), add=(0, 0, 0), sat=1.0):
    a = np.asarray(fr.convert("RGB"), np.float32)
    if sat != 1.0:
        l = a @ np.array([0.3, 0.59, 0.11], np.float32)
        a = l[..., None] + (a - l[..., None]) * sat
    a = a * np.array(mult, np.float32) + np.array(add, np.float32)
    return to_img(a)

def pollen(fr, t, seed, n=60, col=(255, 236, 190), up=True):
    d = ImageDraw.Draw(fr)
    for i in range(n):
        r = random.Random(seed * 997 + i)
        x = (r.uniform(0, W) + t * r.uniform(-15, 35)) % W
        y = (r.uniform(0, H) - t * r.uniform(15, 55) * (1 if up else -1)) % H
        s = r.uniform(1.5, 5.5)
        a = int(170 * (0.5 + 0.5 * math.sin(t * r.uniform(1, 4) + i)))
        d.ellipse([x - s, y - s, x + s, y + s], fill=col + (a,))

# ---------------------------------------------------------------- story
def scene_dawn(t, fi):
    p = prog(t, 0, 5.6)
    fr = camera("s_dawn", ease_in_out(p), 1.0, 1.12, 0.5, 0.62, 0, -0.02)
    # night → sunrise: start cold/dark, warm up
    k = ease_in_out(prog(t, 0.2, 4.8))
    fr = grade(fr, mult=(lerp(0.35, 1.02, k), lerp(0.4, 1.0, k), lerp(0.7, 0.98, k)), sat=lerp(0.6, 1.08, k))
    arr = np.asarray(fr.convert("RGB"), np.float32)
    arr += (radial(W * 0.86, H * 0.4, 900) ** 2.4)[..., None] * np.array([255, 150, 60]) * 0.55 * k
    fr = to_img(arr)
    d = ImageDraw.Draw(fr)
    sa = 1 - ease_in_out(prog(t, 0.3, 4.0))
    for (x, y, s, ph) in R.STARS:
        if y < H * 0.35:
            a = int(255 * sa * (0.6 + 0.4 * math.sin(t * 3 + ph)))
            if a > 4:
                d.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=(255, 245, 230, a))
    fr.alpha_composite(grad_mask(700, 500, 150, 170))
    put_text(fr, "القصيم", KUFI, 160, W / 2, 400, CREAM, 1.5, t, 1.0, "Bold", glow=(255, 170, 90, 150))
    put_text(fr, "حكايةٌ بدأت منذ الستينات", AMIRI, 66, W / 2, 565, GOLD_L, 2.6, t, 1.0, glow=(0, 0, 0, 170))
    return fr

def scene_memory(t, fi):
    lt = t - 5.3
    p = prog(lt, 0, 5.8)
    fr = camera("s_memory", ease_in_out(p), 1.02, 1.16, 0.5, 0.66, 0, -0.01)
    arr = np.asarray(fr.convert("RGB"), np.float32)
    lum = arr @ np.array([0.3, 0.59, 0.11], np.float32)
    sep = np.stack([lum * 1.07 + 16, lum * 0.87 + 6, lum * 0.64], -1)
    arr = arr * 0.45 + sep * 0.55
    arr += (radial(W * (0.15 + 0.2 * math.sin(lt * 0.9)), 260, 900) ** 2 * (0.35 + 0.15 * math.sin(lt * 2)))[..., None] * np.array([255, 120, 50])
    arr *= 0.95 + 0.05 * math.sin(fi * 2.7)
    fr = to_img(arr)
    d = ImageDraw.Draw(fr)
    rr = random.Random(fi // 2)
    for _ in range(2):
        x = rr.uniform(0, W)
        d.line([(x, 0), (x + rr.uniform(-10, 10), H)], fill=(255, 240, 210, 45), width=1)
    fr.alpha_composite(grad_mask(760, 380, 190, 150))
    put_text(fr, "في السابعة من عمره", AMIRI, 78, W / 2, 300, CREAM, 5.9, t, 0.9)
    put_text(fr, "خلف أبيه.. بين النخيل", AMIRI, 78, W / 2, 410, CREAM, 6.9, t, 0.9)
    put_text(fr, "الأرضُ أمانة", RUQAA, 124, W / 2, 590, GOLD_L, 9.6, t, 1.0, glow=(255, 170, 80, 180))
    return fr

def scene_wheat(t, fi):
    lt = t - 10.8
    p = prog(lt, 0, 5.0)
    fr = camera("s_wheat", ease_in_out(p), 1.0, 1.12, 0.5, 0.6, -0.03, 0)
    arr = np.asarray(fr.convert("RGB"), np.float32)
    flick = 0.85 + 0.15 * math.sin(lt * 2.3)
    arr += (radial(W * 0.62, H * 0.2, 800) ** 2.5)[..., None] * np.array([255, 190, 110]) * 0.5 * flick
    fr = to_img(arr)
    pollen(fr, lt, 3, 80)
    fr.alpha_composite(grad_mask(760, 300, 170, 120))
    put_text(fr, "بلا كيماويات", KUFI, 112, W / 2, 290, (255, 250, 240), 11.2, t, 0.8, "Bold", glow=(90, 40, 0, 160))
    put_text(fr, "بلا استعجال", KUFI, 112, W / 2, 430, (255, 250, 240), 12.4, t, 0.8, "Bold", glow=(90, 40, 0, 160))
    put_text(fr, "كما زرعها الأجداد", AMIRI, 72, W / 2, 575, GOLD_L, 13.6, t, 0.9, glow=(0, 0, 0, 150))
    return fr

# ------------------------------------------------------------- products
PRODUCTS = [
    (15.6, 17.35, "p_winana", "الونّانة", "تمر عضوي", "من نخيلنا", (0.5, 0.58)),
    (17.35, 18.6, "p_khalas", "الخلاص", "تمر عضوي", "من نخيلنا", (0.5, 0.6)),
    (18.6, 20.3, "p_dibs", "دبس التمر", "عضوي ١٠٠٪", "من نخيلنا", (0.5, 0.5)),
    (20.3, 22.35, "p_burr", "دقيق البُرّ", "قمح عضوي أسمر", "من حقولنا", (0.5, 0.6)),
    (22.35, 23.4, "p_jareesh", "الجريش", "عضوي", "من حقولنا", (0.5, 0.58)),
    (23.4, 24.35, "p_talbina", "التلبينة", "عضوية", "من حقولنا", (0.5, 0.58)),
    (24.35, 25.9, "p_coffee", "قهوة الشعير", "عضوية", "من حقولنا", (0.45, 0.58)),
    (25.9, 28.55, "p_matazeez", "المطازيز", "من البُرّ العضوي", "على سُفرتكم", (0.5, 0.52)),
    (28.55, 30.1, "p_maamoul", "معمول الهجرسية", "بتمرنا العضوي", "على سُفرتكم", (0.5, 0.58)),
    (30.1, 31.7, "p_honey", "العسل العضوي", "عسل أكاسيا", "على سُفرتكم", (0.5, 0.55)),
]
TR = 0.32  # slide transition length

def product_plate(i, lt, dur):
    s0, s1, img, name, sub, sec, (fx, fy) = PRODUCTS[i]
    k = clamp((lt + TR) / (dur + TR))
    zin, zout = (1.0, 1.1) if i % 2 == 0 else (1.1, 1.0)
    return camera(img, ease_in_out(k), zin, zout, fx, fy, 0.012 * (1 if i % 2 else -1), 0)

def hblur(im, amount):
    if amount < 0.05:
        return im
    f = max(2, int(2 + amount * 28))
    return im.resize((W // f, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

def scene_products(t, fi):
    cur = 0
    for i, pr in enumerate(PRODUCTS):
        if t >= pr[0]:
            cur = i
    s0, s1, img, name, sub, sec, _ = PRODUCTS[cur]
    lt, dur = t - s0, s1 - s0
    base = product_plate(cur, lt, dur)
    if cur > 0 and lt < TR:
        # slide in from the left (RTL flow), old plate pushed right with parallax + motion blur
        k = ease_in_out(lt / TR)
        prev = product_plate(cur - 1, PRODUCTS[cur - 1][1] - PRODUCTS[cur - 1][0] + lt, PRODUCTS[cur - 1][1] - PRODUCTS[cur - 1][0])
        blur = math.sin(math.pi * k)
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        fr.alpha_composite(hblur(prev, blur), (int(k * W * 0.35), 0))
        new = hblur(base, blur)
        fr.alpha_composite(new, (int(-(1 - k) * W), 0))
        # soft edge shadow on the incoming plate
        ex = int(-(1 - k) * W) + W
        sh = Image.new("RGBA", (60, H), (0, 0, 0, 0))
        sh.putalpha(Image.fromarray(np.repeat((np.linspace(140, 0, 60)[None, :]).astype(np.uint8), H, 0)))
        fr.alpha_composite(sh, (max(-60, min(W, ex)), 0))
    else:
        fr = base
    fr.alpha_composite(grad_mask(430, 620, 185, 240))
    # light sweep across the hero after it lands
    sw = prog(lt, 0.35, 1.25)
    if 0 < sw < 1:
        band = Image.new("L", (W, H), 0)
        bx = lerp(-500, W + 500, sw)
        ImageDraw.Draw(band).polygon([(bx, 0), (bx + 140, 0), (bx - 260, H), (bx - 400, H)], fill=55)
        band = band.filter(ImageFilter.GaussianBlur(40))
        wl = Image.new("RGBA", (W, H), (255, 240, 210, 0)); wl.putalpha(band)
        fr.alpha_composite(wl)
    pollen(fr, t, cur + 11, 26, col=(255, 226, 160))
    # section header
    sec_start = min(p[0] for p in PRODUCTS if p[5] == sec)
    put_text(fr, sec, KUFI, 92, W / 2, 190, GOLD_L, sec_start, t, 0.6, "Bold", glow=(0, 0, 0, 140))
    hp = ease_out(prog(t, sec_start + 0.1, sec_start + 0.8))
    d = ImageDraw.Draw(fr)
    d.line([(W / 2 - 190 * hp, 272), (W / 2 + 190 * hp, 272)], fill=GOLD + (220,), width=3)
    d.ellipse([W / 2 - 7, 265, W / 2 + 7, 279], fill=GOLD + (int(255 * hp),))
    # organic seal
    bp = ease_back(prog(lt, 0.3, 0.7), 2.4)
    if bp > 0:
        paste_center(fr, organic_badge(), 120, 400, clamp(bp), max(0.01, bp * 1.1))
    # name + subtitle
    last = cur == len(PRODUCTS) - 1
    out_t = None if last else s1 - 0.25
    put_text(fr, name, RUQAA, 150, W / 2, 1560, CREAM, s0 + 0.12, t, 0.5, out_t=out_t, glow=(0, 0, 0, 170))
    put_text(fr, sub, TAJ, 54, W / 2, 1700, GOLD_L, s0 + 0.3, t, 0.5, out_t=out_t)
    if last:
        fo = ease_in_out(prog(t, T_AWARD - 0.3, T_AWARD))
        if fo > 0:
            fr = Image.blend(fr, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fo * 0.3)
    return fr

# ------------------------------------------------------ certification + award
def scene_award(t, fi):
    lt = t - T_AWARD
    if t < T_MEDAL:
        # certified organic: crops & livestock
        k = prog(t, T_AWARD, T_MEDAL)
        fr = camera("s_livestock", ease_in_out(k), 1.0, 1.1, 0.5, 0.6, 0.02, 0)
        fr = grade(fr, (1.02, 0.98, 0.92), sat=1.05)
        fr.alpha_composite(grad_mask(820, 560, 215, 200))
        pollen(fr, lt, 21, 30)
        put_text(fr, "موثّقة عالمياً ومحلياً", KUFI, 92, W / 2, 270, CREAM, T_AWARD + 0.3, t, 0.7, "Bold", glow=(0, 0, 0, 140))
        bp_in = ease_back(prog(lt, 0.2, 0.9), 1.6)
        if bp_in > 0:
            paste_center(fr, organic_badge(), W / 2, 560, clamp(bp_in), max(0.01, 1.7 * bp_in * (1 + 0.012 * math.sin(lt * 4))))
        for i, (c, st) in enumerate((("زراعة عضوية", 34.4), ("إنتاج حيواني عضوي", 35.0))):
            cp = ease_back(prog(t, st, st + 0.45), 1.8)
            if cp > 0:
                paste_center(fr, chip(c), W / 2 + (1 - 2 * i) * 230, 1640, clamp(cp), max(0.01, cp * 1.25))
        return fr
    # the award
    lt2 = t - T_MEDAL
    k = prog(t, T_MEDAL, T_LOGO)
    fr = camera("p_sukari", ease_in_out(k), 1.12, 1.02, 0.5, 0.62)
    fr = grade(fr, (0.55, 0.5, 0.45))
    arr = np.asarray(fr.convert("RGB"), np.float32)
    ang = np.arctan2(R.YY - 760, R.XX - W / 2)
    rays = (0.5 + 0.5 * np.sin(ang * 16 + lt2 * 0.6)) ** 6
    rays *= np.clip(1 - np.sqrt((R.XX - W / 2) ** 2 + (R.YY - 760) ** 2) / 1300, 0, 1)
    arr += rays[..., None] * np.array([170, 110, 45]) * ease_out(prog(lt2, 0, 0.8))
    arr += (radial(W / 2, 760, 650) ** 2)[..., None] * np.array([150, 95, 35])
    fr = to_img(arr)
    sparkles(fr, t, 99, 70, col=(255, 230, 170))
    mp = ease_back(prog(lt2, 0.05, 0.8), 1.8)
    if mp > 0:
        paste_center(fr, medal(), W / 2, 760, clamp(mp * 1.5), max(0.01, mp * (1 + 0.015 * math.sin(lt2 * 3))))
    put_text(fr, "الجائزة الكبرى", KUFI, 124, W / 2, 1230, GOLD_L, T_MEDAL + 0.25, t, 0.7, "Bold", glow=(110, 50, 0, 210))
    put_text(fr, "جائزة جميل للتمور ٢٠٢٦", AMIRI, 70, W / 2, 1365, CREAM, T_MEDAL + 0.8, t, 0.7, glow=(0, 0, 0, 150))
    put_text(fr, "عن تمر السكري المفتّل", TAJ, 48, W / 2, 1480, GOLD_L, T_MEDAL + 1.3, t, 0.6)
    return fr

# ---------------------------------------------------------------- end card
def scene_end(t, fi):
    lt = t - T_LOGO
    base = multi_grad([(0, (252, 244, 230)), (0.6, CREAM), (1, (236, 214, 184))])
    fr = to_img(base)
    pa = Image.new("RGBA", (W, H), MAROON + (0,))
    pa.putalpha(arch_pattern().getchannel("A").point(lambda v: min(255, v * 2)))
    fr.alpha_composite(pa, (0, int(-lt * 15) % 200 - 200))
    rise = ease_out(prog(lt, 0, 1.2))
    row = cached("end_palms", lambda: palms_row(71, 7, 260, 420, H + 10, (150, 70, 70)))
    fr.alpha_composite(with_alpha(row, 0.35), (-200, int((1 - rise) * 300)))
    fr.alpha_composite(Image.new("RGBA", (W, 200), MAROON + (255,)), (0, H - 200 + int((1 - rise) * 200)))
    lp = ease_back(prog(lt, 0.15, 0.9), 1.6)
    if lp > 0:
        lg = logo_img()
        paste_center(fr, lg, W / 2, 760, clamp(lp * 1.6), 640 / lg.width * max(0.01, lp))
    tag = text_img("من أرضِنا.. إلى سُفرتِكم", RUQAA, 92, MAROON, None, False)
    if t > 41.5:
        p = ease_out(prog(t, 41.5, 42.5))
        paste_center(fr, wipe_rtl(tag, p), W / 2, 1300 + (1 - p) * 30, p)
    up = ease_back(prog(t, 42.7, 43.3), 1.6)
    if up > 0:
        paste_center(fr, url_pill(), W / 2, 1480, clamp(up), max(0.01, up))
    ip = ease_out(prog(t, 43.2, 43.8))
    if ip > 0:
        paste_center(fr, text_img("شحن مبرّد  •  استلام من المتجر", TAJ, 44, CREAM, None, False), W / 2, H - 100, ip)
    sparkles(fr, t, 5, 20, area=(0, 300, W, 1400), col=GOLD)
    return fr

SCENES = [
    (0.0, 5.3, scene_dawn),
    (5.3, 10.8, scene_memory),
    (10.8, T_PROD, scene_wheat),
    (T_PROD, T_AWARD, scene_products),
    (T_AWARD, T_LOGO, scene_award),
    (T_LOGO, DUR + 1, scene_end),
]
XF = 0.4

def render(fi):
    t = fi / FPS
    frame = None
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b:
            frame = fn(t, fi)
            if i + 1 < len(SCENES) and t > b - XF:
                nxt = SCENES[i + 1][2](t, fi)
                frame = Image.blend(frame, nxt, ease_in_out((t - (b - XF)) / XF))
            break
    for hit in (T_AWARD, T_MEDAL, T_LOGO):
        if hit <= t < hit + 0.25:
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 244, 220, 255)), 0.55 * (1 - (t - hit) / 0.25))
    arr = finish(frame, fi, grain=5.0 if t < T_LOGO else 3.0, vig=0.75 if t < T_LOGO else 0.3)
    k = clamp(t / 0.8) * (1 - clamp((t - (DUR - 0.6)) / 0.6))
    if k < 1:
        arr = (arr.astype(np.float32) * k).astype(np.uint8)
    return arr

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for tt in sys.argv[2:]:
            Image.fromarray(render(int(float(tt) * FPS))).save(os.path.join(R.BASE, f"v2_{tt}.jpg"), quality=88)
    else:
        from multiprocessing import Pool
        out = sys.argv[2]
        n = int(DUR * FPS)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for i, arr in enumerate(pool.imap(render, range(n), chunksize=4)):
                ff.stdin.write(arr.tobytes())
                if i % 60 == 0:
                    print(i, "/", n, flush=True)
        ff.stdin.close(); ff.wait()

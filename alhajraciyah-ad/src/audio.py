"""Sound design for the Al-Hajraciyah ad: Arabic score in maqam Hijaz on D
(oud, ney, darbuka, daf, riq, strings), desert ambience, foley, transitions, VO mix."""
import os, json, wave
import numpy as np
from scipy import signal

SR = 48000
DUR = 43.0
N = int(SR * DUR)
BASE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE, "audio")
rng = np.random.default_rng(1)

def bus():
    return np.zeros((2, N), np.float32)

def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    x = x[: N - i]
    l = np.cos((pan + 1) * np.pi / 4) * gain
    r = np.sin((pan + 1) * np.pi / 4) * gain
    if x.ndim == 1:
        buf[0, i:i + len(x)] += x * l
        buf[1, i:i + len(x)] += x * r
    else:
        buf[0, i:i + x.shape[1]] += x[0] * l * 1.414
        buf[1, i:i + x.shape[1]] += x[1] * r * 1.414

def env(n, a, d_tau):
    t = np.arange(n) / SR
    e = np.exp(-t / d_tau)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e

def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)

def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)

def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)

# ---------------------------------------------------------------- pitch
D4 = 293.66
def hz(semi, octave=0):
    """semitones relative to D4"""
    return D4 * 2 ** (semi / 12 + octave)
# maqam Hijaz on D: D Eb F# G A Bb C D
HJ = {"D": 0, "Eb": 1, "F#": 4, "G": 5, "A": 7, "Bb": 8, "C": 10, "D'": 12, "Eb'": 13, "F#'": 16, "G'": 17, "A'": 19, "C,": -2, "A,": -5, "Bb,": -4, "G,": -7}

# ---------------------------------------------------------- instruments
def oud(f, dur=1.6, vel=1.0, bright=0.5):
    """Karplus–Strong plucked string with fretless oud body resonances."""
    n = int(dur * SR)
    per = SR / f
    L = int(per)
    exc = rng.uniform(-1, 1, L) * vel
    exc = lp(exc, 1500 + 5000 * bright, 1)
    x = np.zeros(n); x[:L] = exc
    a = 0.996 - 0.0015 * (f / 600)
    den = np.zeros(L + 2); den[0] = 1; den[L] = -a * 0.5; den[L + 1] = -a * 0.5
    y = signal.lfilter([1], den, x)
    # body: wooden bowl-back resonances + pick transient
    body = bp(y, 90, 400) * 0.6 + bp(y, 600, 1400) * 0.35 + y * 0.5
    pick = hp(rng.normal(0, 1, int(0.012 * SR)), 2000) * np.linspace(1, 0, int(0.012 * SR)) * 0.25 * vel
    body[:len(pick)] += pick
    return (body * env(n, 0.002, dur * 0.45)).astype(np.float32)

def ney(f, dur, vel=1.0, vib=5.2):
    """Breathy end-blown reed flute."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    vdepth = np.clip((t - 0.25) / 0.6, 0, 1) * 0.012
    ph = 2 * np.pi * np.cumsum(f * (1 + vdepth * np.sin(2 * np.pi * vib * t))) / SR
    tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph) + 0.06 * np.sin(4 * ph)
    breath = bp(rng.normal(0, 1, n), f * 0.8, min(f * 5, 12000)) * 0.9 + hp(rng.normal(0, 1, n), 3000) * 0.08
    a = np.clip(t / 0.18, 0, 1) ** 1.5
    r = np.clip((dur - t) / 0.35, 0, 1)
    swell = 0.8 + 0.2 * np.sin(np.pi * np.clip(t / dur, 0, 1))
    return ((tone * 0.55 + breath * 0.35) * a * r * swell * vel).astype(np.float32)

def pad(freqs, dur, vel=1.0, cutoff=1800, attack=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0, 0.007):
            ph = (f * (1 + det) * t + rng.random()) % 1
            out += (2 * ph - 1)
    out = lp(out, cutoff, 2) / (len(freqs) * 3)
    a = np.clip(t / attack, 0, 1)
    r = np.clip((dur - t) / 1.0, 0, 1)
    return (out * a * r * vel).astype(np.float32)

def dum(vel=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 95 + 110 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    slap = bp(rng.normal(0, 1, n), 200, 1200) * np.exp(-t / 0.02) * 0.4
    return ((body + slap) * vel).astype(np.float32)

def tek(vel=1.0, bright=1.0):
    n = int(0.15 * SR); t = np.arange(n) / SR
    x = bp(rng.normal(0, 1, n), 1800, 9000) * np.exp(-t / (0.018 * bright))
    ring = np.sin(2 * np.pi * 740 * t) * np.exp(-t / 0.03) * 0.3
    return ((x + ring) * vel * 0.8).astype(np.float32)

def daf(vel=1.0):
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 62 + 40 * np.exp(-t / 0.05)
    b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    skin = bp(rng.normal(0, 1, n), 100, 700) * np.exp(-t / 0.06) * 0.5
    jing = hp(rng.normal(0, 1, n), 6000) * np.exp(-t / 0.12) * 0.12 * (1 + 0.5 * np.sin(2 * np.pi * 23 * t))
    return ((b + skin + jing) * vel).astype(np.float32)

def riq(vel=1.0):
    n = int(0.2 * SR); t = np.arange(n) / SR
    x = hp(rng.normal(0, 1, n), 7000) * (np.exp(-t / 0.05)) * (1 + 0.6 * np.sin(2 * np.pi * 35 * t))
    return (x * vel * 0.22).astype(np.float32)

def boom(vel=1.0, dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 36 + 90 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    crack = lp(rng.normal(0, 1, n), 3000) * np.exp(-t / 0.05) * 0.6
    air = bp(rng.normal(0, 1, n), 300, 4000) * np.exp(-t / 0.7) * 0.12
    return ((sub + crack + air) * vel).astype(np.float32)

def whoosh(dur=0.6, lo=300, hi=6000, vel=1.0, rev=False):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    # time-varying band via two sweeping biquads (block-wise)
    out = np.zeros(n)
    blk = 512
    zi = None
    for i in range(0, n, blk):
        k = i / n
        k = k if not rev else 1 - k
        fc = lo * (hi / lo) ** (np.sin(np.pi * k) if not rev else k)
        sos = signal.butter(2, [fc * 0.6, min(fc * 1.6, SR / 2 - 100)], "bandpass", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    shape = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5 if not rev else (t / dur) ** 3
    return (out * shape * vel * 1.4).astype(np.float32)

def riser(dur=2.0, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    k = t / dur
    f = 200 * 2 ** (k * 3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.15
    nz = whoosh(dur, 400, 9000, 1.0, rev=True)
    return ((tone * k ** 2 + nz * 0.8) * vel).astype(np.float32)

def shimmer(dur=2.0, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(int(dur * 14)):
        f = r.choice([hz(12, 1), hz(16, 1), hz(19, 1), hz(24, 1), hz(7, 2), hz(12, 2)])
        st = r.integers(0, n - 4000)
        m = min(int(0.6 * SR), n - st)
        tt = np.arange(m) / SR
        out[st:st + m] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.18) * r.uniform(0.2, 0.6)
    return (out * vel * 0.25).astype(np.float32)

def bird(seed):
    r = np.random.default_rng(seed)
    out = []
    for _ in range(r.integers(2, 5)):
        d = r.uniform(0.05, 0.14); n = int(d * SR); t = np.arange(n) / SR
        f0 = r.uniform(2600, 4200)
        f = f0 + r.uniform(-1200, 1500) * (t / d) + 300 * np.sin(2 * np.pi * r.uniform(20, 45) * t)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        out += [s, np.zeros(int(r.uniform(0.03, 0.12) * SR))]
    return (np.concatenate(out) * 0.25).astype(np.float32)

def footstep(vel=1.0):
    n = int(0.18 * SR); t = np.arange(n) / SR
    crunch = bp(rng.normal(0, 1, n), 300, 3500) * np.exp(-t / 0.05) * (0.5 + 0.5 * rng.random(n))
    thud = np.sin(2 * np.pi * 80 * t) * np.exp(-t / 0.04)
    return ((crunch * 0.5 + thud * 0.5) * vel).astype(np.float32)

def reverb(stereo, seconds=2.2, wet=0.25, pre=0.02, bright=5000):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    irs = []
    for ch in range(2):
        ir = np.random.default_rng(10 + ch).normal(0, 1, n) * np.exp(-t / (seconds / 6.9))
        ir = lp(ir, bright, 1)
        ir = np.concatenate([np.zeros(int(pre * SR)), ir])
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    out = np.stack([signal.fftconvolve(stereo[c], irs[c])[:N] for c in range(2)])
    return (stereo * (1 - wet) + out * wet * 1.2).astype(np.float32)

# ============================================================ arrangement
mus = bus()     # music (ducked under VO)
amb = bus()     # ambience + foley
sfx = bus()     # transitions / hits (not ducked)

# --- ambience: desert wind across the whole spot, crickets → birds at dawn
wind = lp(np.cumsum(rng.normal(0, 1, N)) * 0.02, 900, 2)
wind = wind - lp(wind, 40, 1)
t = np.arange(N) / SR
wmod = 0.55 + 0.45 * np.sin(2 * np.pi * t / 7.3) * np.sin(2 * np.pi * t / 3.1 + 1)
wenv = np.interp(t, [0, 1, 11, 12, 15.5, 16, 30, 36, 43], [0.5, 0.8, 0.8, 1.2, 1.1, 0.35, 0.3, 0.2, 0.4])
wind = (wind * wmod * wenv / (np.abs(wind).max() + 1e-9)).astype(np.float32)
amb[0] += wind * 0.22; amb[1] += np.roll(wind, 2400) * 0.22
# wheat rustle (bright noise swells) during the wheat scene
rus = hp(rng.normal(0, 1, N), 2500) * np.interp(t, [10.6, 11.2, 15.4, 15.9], [0, 1, 1, 0]) * (0.5 + 0.5 * np.sin(2 * np.pi * t * 0.8) ** 2)
amb[0] += rus.astype(np.float32) * 0.025; amb[1] += np.roll(rus, 900).astype(np.float32) * 0.025
# crickets (night) fading as the sun rises
cr = np.sin(2 * np.pi * 4700 * t) * (np.sin(2 * np.pi * 28 * t) > 0.3) * (np.sin(2 * np.pi * 1.7 * t) > -0.2)
cr = lp(cr, 7000) * np.interp(t, [0, 0.6, 3.0, 4.5], [0, 1, 0.6, 0])
amb[0] += cr.astype(np.float32) * 0.02; amb[1] += np.roll(cr, 700).astype(np.float32) * 0.015
for i, bt in enumerate([2.6, 3.4, 4.3, 6.2, 8.1, 12.0, 14.2, 37.5, 40.0]):
    place(amb, bird(i), bt, 0.35 if bt < 30 else 0.2, pan=(-0.6 if i % 2 else 0.6))
# father & son footsteps in the sand (memory scene), stride ~0.75s
for k in range(8):
    place(amb, footstep(0.5), 5.6 + k * 0.75, 0.5, -0.1)
    place(amb, footstep(0.3), 5.95 + k * 0.75, 0.4, 0.2)
# old-film projector crackle in the memory scene
crk = np.zeros(N, np.float32)
idx = rng.integers(int(5.3 * SR), int(10.8 * SR), 260)
crk[idx] = rng.uniform(-1, 1, len(idx))
crk = hp(crk, 1500) * 0.6
amb[0] += crk.astype(np.float32) * 0.3; amb[1] += crk.astype(np.float32) * 0.3

# --- intro (0–5.3): low drone + ney call in Hijaz
place(mus, pad([hz(0, -2), hz(7, -2), hz(0, -1)], 11.0, 0.5, 700, 3.0), 0.0, 0.6)
ney_intro = [("A", 0.6, 1.6), ("Bb", 2.2, 0.5), ("A", 2.7, 0.6), ("G", 3.3, 0.5), ("F#", 3.8, 0.5), ("Eb", 4.3, 0.35), ("D", 4.65, 1.4)]
for nm, st, d in ney_intro:
    place(mus, ney(hz(HJ[nm]), d + 0.25, 0.7), st, 0.45, 0.15)

# --- memory (5.3–10.8): sparse, tender oud taqsim + ney answer
taqsim = [("D", 5.5), ("A,", 5.9), ("D", 6.3), ("Eb", 6.55), ("F#", 6.8), ("G", 7.6), ("F#", 7.9), ("Eb", 8.15), ("D", 8.5),
          ("A", 9.2), ("G", 9.45), ("F#", 9.7), ("G", 9.95), ("A", 10.2)]
for i, (nm, st) in enumerate(taqsim):
    place(mus, oud(hz(HJ[nm], -1), 1.8, 0.8, 0.35), st, 0.55, -0.25)
place(mus, pad([hz(0, -1), hz(4, -1), hz(7, -1)], 6.0, 0.45, 1100, 2.0), 5.3, 0.45)
for nm, st, d in [("D'", 8.6, 0.9), ("C", 9.4, 0.4), ("Bb", 9.8, 0.4), ("A", 10.2, 0.9)]:
    place(mus, ney(hz(HJ[nm]), d + 0.2, 0.6), st, 0.35, 0.3)

# --- wheat (10.8–15.6): oud ostinato wakes up, frame drum heartbeat, build
BEAT = 0.6125  # 98 BPM; 6 bars = the product section
e8 = BEAT / 2
ost = ["D", "A,", "D", "Eb", "F#", "Eb", "D", "A,"]
for b in range(8):
    for k, nm in enumerate(ost):
        st = 10.8 + b * 4 * BEAT * 0 + (b * 8 + k) * e8
        if st >= 15.6:
            break
        place(mus, oud(hz(HJ[nm], -1), 0.9, 0.55 + 0.25 * (k == 0), 0.5), st, 0.45, -0.3)
for k in range(8):
    st = 10.8 + k * BEAT
    if st < 15.3:
        place(mus, daf(0.5 + 0.06 * k), st, 0.35, 0.0)
place(mus, pad([hz(0, -1), hz(7, -1), hz(12, -1)], 5.2, 0.5, 1400, 2.5), 10.8, 0.5)
# darbuka roll into the groove
for k in range(12):
    place(mus, tek(0.3 + 0.06 * k), 14.85 + k * 0.06, 0.5, 0.2 * (-1) ** k)
place(sfx, riser(1.6, 0.6), 14.0, 0.45)

# --- products (15.6–30.3): full maqsum groove
T0 = 15.6
bars = 6
bass_roots = ["D", "D", "G,", "G,", "C,", "D"]   # i  i  iv  iv  VII  i
# maqsum: DUM tek - tek DUM - tek -   (8 eighths)
MAQSUM = [("D", 1.0), ("t", 0.7), (None, 0), ("t", 0.6), ("D", 0.9), (None, 0), ("t", 0.7), ("k", 0.4)]
for b in range(bars):
    for k, (hit, v) in enumerate(MAQSUM):
        st = T0 + (b * 8 + k) * e8
        if hit == "D":
            place(mus, dum(v), st, 0.8, 0.0)
        elif hit == "t":
            place(mus, tek(v), st, 0.55, 0.25)
        elif hit == "k":
            place(mus, tek(v, 0.6), st, 0.45, -0.25)
        # riq on every 16th for shimmer
        place(mus, riq(0.5 if k % 2 == 0 else 0.3), st, 0.35, 0.5)
        place(mus, riq(0.2), st + e8 / 2, 0.3, 0.5)
    place(mus, daf(0.8), T0 + b * 8 * e8, 0.45, 0.0)
    # bass: plucked low oud doubling root
    root = hz(HJ[bass_roots[b]], -2)
    for k in (0, 3, 4, 6):
        place(mus, oud(root, 1.0, 0.9, 0.2), T0 + (b * 8 + k) * e8, 0.6, 0.0)
# oud riff (hook) over the groove
riffA = ["D'", "D'", "A", "D'", "Eb'", "F#'", "Eb'", "D'"]
riffB = ["G", "F#", "Eb", "D", "Eb", "C", "D", None]
riffC = ["Bb", "A", "G", "A", "Bb", "C", "Bb", "A"]
riffD = ["G", "F#", "G", "A", "Bb", "A", "G", "F#"]
riffE = ["C", "Bb", "A", "G", "F#", "G", "Eb", "D"]
riffF = ["D", "F#", "A", "D'", "A", "F#", "D", None]
for b, rf in enumerate([riffA, riffB, riffC, riffD, riffE, riffF]):
    for k, nm in enumerate(rf):
        if nm:
            place(mus, oud(hz(HJ[nm], -1 if "'" not in nm else -1), 0.9, 0.75, 0.6), T0 + (b * 8 + k) * e8, 0.5, -0.35)
# string pad under each section
place(mus, pad([hz(0, -1), hz(4, -1), hz(7, -1)], 4.9, 0.55, 1800, 0.8), 15.6, 0.45)
place(mus, pad([hz(-7, 0), hz(-2, 0), hz(2, 0)], 5.0, 0.55, 1800, 0.8), 20.3, 0.45)   # G minor
place(mus, pad([hz(-2, 0), hz(3, 0), hz(7, 0)], 2.5, 0.55, 1800, 0.6), 25.2, 0.45)   # C minor
place(mus, pad([hz(0, -1), hz(4, -1), hz(9, -1)], 2.7, 0.55, 1800, 0.6), 27.6, 0.45)
# whooshes on every product card push
PRODUCT_CUTS = [15.6, 17.35, 18.6, 20.3, 22.35, 23.4, 24.35, 25.9, 28.55]
for i, c in enumerate(PRODUCT_CUTS):
    place(sfx, whoosh(0.45, 400, 5000, 0.6), c - 0.12, 0.28, pan=(-0.5 if i % 2 else 0.5))
    place(sfx, shimmer(0.6, 0.5, i), c + 0.15, 0.25, 0.3)
place(sfx, riser(1.5, 0.8), 28.8, 0.5)

# --- award (30.3–35.8): impact, big drums, triumphant strings, ney soars
place(sfx, boom(1.0), 30.3, 0.8)
place(sfx, shimmer(3.0, 1.0, 42), 30.3, 0.5)
place(mus, pad([hz(0, -1), hz(4, -1), hz(7, -1), hz(12, -1)], 5.8, 0.8, 2600, 0.4), 30.3, 0.6)
for k in range(9):
    st = 30.3 + k * BEAT
    place(mus, daf(0.7 if k % 2 else 1.0), st, 0.55, 0.0)
    if k % 2 == 0:
        place(mus, dum(0.8), st, 0.55, 0.0)
place(sfx, whoosh(0.9, 200, 7000, 0.8, rev=True), 32.1, 0.35)
place(sfx, boom(0.7, 2.0), 33.0, 0.55)
place(sfx, shimmer(2.5, 1.2, 7), 33.0, 0.6)
for nm, st, d in [("D'", 33.0, 0.6), ("Eb'", 33.6, 0.3), ("F#'", 33.9, 0.3), ("G'", 34.2, 0.3), ("A'", 34.5, 1.2)]:
    place(mus, ney(hz(HJ[nm]), d + 0.3, 0.8), st, 0.4, 0.2)
place(sfx, riser(1.2, 0.8), 34.6, 0.5)

# --- logo (35.8–43): signature hit, final oud strum, warm resolve
place(sfx, boom(1.0, 4.0), 35.8, 0.85)
place(sfx, shimmer(3.5, 1.0, 99), 35.9, 0.5)
strum = ["D", "A", "D'", "F#'", "A'"]
for k, nm in enumerate(strum):
    place(mus, oud(hz(HJ[nm], -1), 3.5, 0.9, 0.5), 35.85 + k * 0.035, 0.5, -0.2 + 0.1 * k)
place(mus, pad([hz(0, -2), hz(0, -1), hz(4, -1), hz(7, -1)], 7.2, 0.6, 1600, 0.3), 35.8, 0.55)
# gentle closing phrase under the tagline + URL
for i, (nm, st) in enumerate([("A", 38.2), ("G", 38.5), ("F#", 38.8), ("Eb", 39.1), ("D", 39.5), ("A,", 40.3), ("D", 40.9)]):
    place(mus, oud(hz(HJ[nm], -1), 2.0, 0.7, 0.4), st, 0.45, -0.2)
place(mus, ney(hz(0), 2.6, 0.6), 39.6, 0.35, 0.2)
for k in range(4):
    place(mus, daf(0.5 - 0.1 * k), 38.2 + k * 2 * BEAT, 0.3, 0.0)

# ============================================================ voice-over
VO_AT = {"v1": 1.2, "v2": 5.6, "v3": 11.0, "v4": 15.4, "v5": 20.4, "v6": 26.0, "v7": 30.6, "v8": 36.4}
vo = np.zeros(N, np.float32)
for k, st in VO_AT.items():
    w = wave.open(os.path.join(A, k + ".wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    i = int(st * SR)
    vo[i:i + len(x)] += x[: N - i]
# voice chain: HPF, presence lift, gentle compression, room
vo = hp(vo, 90).astype(np.float32)
vo = vo + bp(vo, 2500, 5000) * 0.35 + bp(vo, 120, 250) * 0.25
lvl = np.sqrt(lp(vo ** 2, 20, 1).clip(0) + 1e-9)
gain = np.minimum(1, (0.12 / (lvl + 1e-6)) ** 0.4)
vo = vo * gain
vo = vo / (np.abs(vo).max() + 1e-9) * 0.9
vo_st = reverb(np.stack([vo, vo]), 1.1, 0.12, 0.01, 6000)

# duck music + ambience under the VO (sidechain envelope)
sc = np.sqrt(lp(vo ** 2, 6, 1).clip(0))
sc = sc / (sc.max() + 1e-9)
duck = 1 - 0.62 * np.clip(sc * 4, 0, 1)
duck = lp(duck, 8, 1).astype(np.float32)

mus = reverb(mus, 2.4, 0.28)
sfx = reverb(sfx, 3.0, 0.25, 0.03, 7000)
amb = reverb(amb, 1.5, 0.15)

mix = mus * 0.9 * duck + amb * 0.9 * (0.6 + 0.4 * duck) + sfx * 0.9 + vo_st * 1.05
# master: fade in/out, glue compressor, soft clip limiter
fade = np.clip(t / 0.3, 0, 1) * np.clip((DUR - t) / 1.2, 0, 1)
mix *= fade
env_m = np.sqrt(lp(np.mean(mix ** 2, 0), 10, 1).clip(0) + 1e-9)
g = np.minimum(1, (0.25 / env_m) ** 0.3)
mix *= g
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix = mix / np.abs(mix).max() * 0.94
pcm = (mix.T * 32767).astype(np.int16)
with wave.open(os.path.join(BASE, "soundtrack.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
# stems for the editor
for name, s in (("stem_music.wav", mus * duck), ("stem_vo.wav", vo_st), ("stem_sfx_amb.wav", sfx + amb)):
    s = s / (np.abs(s).max() + 1e-9) * 0.9
    with wave.open(os.path.join(BASE, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((s.T * 32767).astype(np.int16).tobytes())
print("ok")

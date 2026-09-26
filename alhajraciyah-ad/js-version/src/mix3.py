"""Final mix for «تعرف من وين جا أكلك؟» — Lyria score (edited), gpt-audio VO, synthesized SFX."""
import json, wave
import numpy as np
from scipy import signal

SR = 48000
DUR = 45.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
TL = json.load(open("timeline.json"))

def rd(path):
    w = wave.open(path)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a.reshape(-1, w.getnchannels()).T if w.getnchannels() > 1 else np.stack([a, a])

def place(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= N: return
    x = x[..., : N - i]
    if x.ndim == 1: x = np.stack([x, x])
    buf[:, i:i + x.shape[1]] += x * g

def hp(x, f): return signal.sosfilt(signal.butter(2, f, "highpass", fs=SR, output="sos"), x)
def lp(x, f): return signal.sosfilt(signal.butter(2, f, "lowpass", fs=SR, output="sos"), x)
def bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)

# ------------------------------------------------------------ music edit
M = rd("music.wav")
J, OFF, XF = 37.2, 11.62, 0.25
music = np.zeros((2, N), np.float32)
a_end = int((J + XF / 2) * SR)
music[:, :a_end] = M[:, :a_end]
b0 = int((J - XF / 2 + OFF) * SR)
tail = M[:, b0:b0 + N - int((J - XF / 2) * SR)]
i0 = int((J - XF / 2) * SR)
nx = int(XF * SR)
ramp = np.sin(np.linspace(0, np.pi / 2, nx)) ** 2
music[:, i0:i0 + nx] = music[:, i0:i0 + nx] * (1 - ramp) + tail[:, :nx] * ramp
music[:, i0 + nx:i0 + tail.shape[1]] = tail[:, nx:]

# tape-stop into the rewind: slow the music down to a halt 5.45→5.9, silence, then rewind noise, music resumes at 6.6
ts0, ts1, rw1 = TL["rewind"][0] - 0.45, TL["rewind"][0], TL["rewind"][1]
seg = music[:, int(ts0 * SR):int(ts1 * SR) + SR].copy()
n = int((ts1 - ts0) * SR)
rate = np.linspace(1, 0.05, n)
pos = np.cumsum(rate)
stop = np.stack([np.interp(pos, np.arange(seg.shape[1]), seg[c]) for c in range(2)]) * np.linspace(1, 0.3, n)
music[:, int(ts0 * SR):int(ts0 * SR) + n] = stop
music[:, int(ts1 * SR):int(rw1 * SR)] = 0
# rewind: a burst of the upcoming music reversed and sped up ×6, band-limited like tape
src = M[:, int(7 * SR):int(11 * SR)][:, ::-1]
fast = src[:, ::6]
rlen = int((rw1 - ts1) * SR)
fast = np.stack([np.interp(np.linspace(0, fast.shape[1] - 1, rlen), np.arange(fast.shape[1]), fast[c]) for c in range(2)])
fast = np.stack([bp(fast[c], 300, 6000) for c in range(2)]) * np.sin(np.linspace(0, np.pi, rlen)) ** 0.7
sfx = np.zeros((2, N), np.float32)
place(sfx, fast.astype(np.float32), ts1, 0.9)
# fade music back in at the start of the journey
k0 = int(rw1 * SR)
music[:, k0:k0 + int(0.15 * SR)] *= np.linspace(0, 1, int(0.15 * SR))

# ------------------------------------------------------------- sfx kit
def whoosh(d=0.5, g=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n); out = np.zeros(n); zi = None
    for i in range(0, n, 512):
        fc = 400 * (6000 / 400) ** np.sin(np.pi * i / n)
        sos = signal.butter(2, [fc * 0.6, min(fc * 1.6, 23000)], "bandpass", fs=SR, output="sos")
        if zi is None: zi = np.zeros((sos.shape[0], 2))
        out[i:i + 512], zi = signal.sosfilt(sos, x[i:i + 512], zi=zi)
    return (out * np.sin(np.pi * t / d) ** 1.5 * g).astype(np.float32)

def boom(g=1.0, d=3.0):
    n = int(d * SR); t = np.arange(n) / SR
    f = 36 + 90 * np.exp(-t / 0.08)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9) + lp(rng.normal(0, 1, n), 2500) * np.exp(-t / 0.05) * 0.5
    return (x * g).astype(np.float32)

def shimmer(d=1.2, g=1.0, seed=0):
    r = np.random.default_rng(seed); n = int(d * SR); out = np.zeros(n)
    for _ in range(int(d * 12)):
        f = r.choice([1174.7, 1480, 1760, 2349, 2960]); st = r.integers(0, n - 3000); m = min(int(0.5 * SR), n - st)
        tt = np.arange(m) / SR; out[st:st + m] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.15) * r.uniform(0.2, 0.6)
    return (out * g * 0.2).astype(np.float32)

def tick(g=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 2350 * t) + 0.5 * np.sin(2 * np.pi * 3520 * t)) * np.exp(-t / 0.04) * g * 0.35).astype(np.float32)

for c in TL["cuts"]:
    place(sfx, whoosh(0.45, 0.35), c - 0.15)
for lab in TL["labels"]:
    place(sfx, tick(0.7), lab[0])
place(sfx, shimmer(1.5, 1.0, 1), TL["certs"])
place(sfx, boom(0.8), TL["award"])
place(sfx, shimmer(2.5, 1.3, 2), TL["award"])
place(sfx, boom(0.9, 4.0), TL["logo"])
place(sfx, shimmer(2.5, 1.0, 3), TL["logo"] + 0.1)
# cold mist on the chilled box
mist = hp(rng.normal(0, 1, int(1.6 * SR)), 4000) * np.sin(np.linspace(0, np.pi, int(1.6 * SR))) * 0.05
place(sfx, mist.astype(np.float32), TL["delivery"] + 0.3)
# room tone at the family table (hook) — soft murmur of a majlis, cups
room = lp(rng.normal(0, 1, int(6 * SR)), 900) * 0.012
place(sfx, room.astype(np.float32), 0.0)
for tcup in (1.2, 3.9):
    n = int(0.3 * SR); t = np.arange(n) / SR
    place(sfx, (np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.05) * 0.08).astype(np.float32), tcup)

# ---------------------------------------------------------------- VO
vo = np.zeros((2, N), np.float32)
for k, t0 in TL["vo"].items():
    x = rd(f"vo2/{k}.wav")[0]
    x = hp(x, 80)
    x = x + bp(x, 2500, 5500) * 0.3
    x = x / (np.abs(x).max() + 1e-9) * (0.85 if k.startswith("n") else 0.75)
    place(vo, x.astype(np.float32), t0)
# small room on the VO
ir = rng.normal(0, 1, int(0.6 * SR)) * np.exp(-np.arange(int(0.6 * SR)) / SR / 0.12)
ir /= np.sqrt((ir ** 2).sum())
vo = vo * 0.9 + np.stack([signal.fftconvolve(vo[c], ir)[:N] for c in range(2)]) * 0.12

sc = np.sqrt(lp(vo[0] ** 2, 6).clip(0)); sc /= sc.max() + 1e-9
gate = (np.abs(lp(vo[0] ** 2, 10)) > 1e-4).astype(np.float32)
gate = np.maximum.accumulate(gate[::-1])[::-1] * 0 + gate  # keep as is
hold = signal.convolve(gate, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same') > 0
duck = lp(1 - 0.72 * hold.astype(np.float32), 5).astype(np.float32).clip(0.2, 1)
mgain = np.interp(np.arange(N) / SR, [0, 21.5, 23.5, 36.8, 37.6, 45], [0.8, 0.8, 0.55, 0.55, 0.5, 0.5]).astype(np.float32)

mix = music * mgain * duck + sfx * 0.9 + vo * 1.0
t = np.arange(N) / SR
mix *= np.clip(t / 0.15, 0, 1) * np.clip((DUR - t) / 1.0, 0, 1)
env = np.sqrt(lp(np.mean(mix ** 2, 0), 10).clip(0) + 1e-9)
mix *= np.minimum(1, (0.25 / env) ** 0.3)
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix = mix / np.abs(mix).max() * 0.94
with wave.open("soundtrack3.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
for name, s in (("stem_music.wav", music * mgain * duck), ("stem_vo.wav", vo), ("stem_sfx.wav", sfx)):
    s = s / (np.abs(s).max() + 1e-9) * 0.9
    with wave.open(name, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((s.T * 32767).astype(np.int16).tobytes())
print("ok")
act = np.abs(lp(vo[0] ** 2, 10)) > 1e-4
mm = (music * mgain * duck)[0]
for i in range(0, 45, 3):
    sl = slice(i * SR, (i + 3) * SR); a = act[sl]
    if a.sum() < SR * 0.3: continue
    v = np.sqrt((vo[0][sl][a] ** 2).mean()); m = np.sqrt((mm[sl][a] ** 2).mean())
    print(i, "VO over music dB:", round(20 * np.log10(v / m), 1))

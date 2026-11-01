"""Code-made music bed + SFX, locked to the VO word timings, mixed with ducking. Zero cost, no samples.
  python scripts/soundtrack.py --vo audio/vo.mp3 --cues cues.json --out audio/
Writes music.wav, sfx.wav and mix.mp3 (-14 LUFS, true peak -1) in --out. See templates/cues.example.json.

cues.json (times in VO seconds; timeline time = VO time + vo_offset):
  vo_offset   seconds of lead-in before the VO
  bpm         tempo; fit it so final_bar lands on the logo: bpm = 240 * bars / (logo_t - anchor_t)
  anchor      VO time of the brand line; it lands on bar 3 (after 3 intro bars)
  final_bar   bar index (from the intro start) of the logo / final chord
  breakdowns  bar indexes that go quiet (pads + half the arpeggio, no drums), e.g. the breath before the logo
  tail        seconds the lockup holds after the final chord
  sfx         [{"type": "pop|whoosh|whoosh_down|tick|tap|coin|success|bell|riser_to_final|impact_final", "t": VO time}]
"""
import argparse
import json
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
rng = np.random.default_rng(7)

def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, hz): return sosfilt(butter(2, hz, "low", fs=SR, output="sos"), x)
def hp(x, hz): return sosfilt(butter(2, hz, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def db(d): return 10 ** (d / 20)

def env(n, a, r, sustain=1.0):
    e = np.full(n, sustain)
    na, nr = min(int(a * SR), n), min(int(r * SR), n)
    if na: e[:na] = np.linspace(0, sustain, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def add(buf, x, t):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x

# ---------- instruments ----------
@lru_cache(maxsize=None)                     # chords repeat; synthesis is the slow part
def pad_note(m, dur, cutoff):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for det in (-0.06, 0.0, 0.07):                       # three detuned saw voices
        f = mtof(m + det)
        for h in range(1, 9):
            if f * h > SR / 2: break
            x += np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.28)) / h
    return lp(x, cutoff) * env(n, 0.7, 0.9) * 0.05

def pluck(m, dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    x = sum(np.sin(2 * np.pi * f * h * t) * np.exp(-t * (5 + 4 * h)) / h for h in range(1, 6))
    return x * env(n, 0.004, 0.2) * 0.11

def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return x * env(n, 0.01, 0.12) * np.exp(-t * 1.6) * 0.22

def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.42

def hat():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * 90) * 0.05

def bell(f, dur=1.4, amp=0.2):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
    return x * np.exp(-t * 3.2) * env(n, 0.002, 0.05) * amp

# ---------- SFX ----------
def pop(f0=900, f1=1500):                    # chat bubble
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / t[-1])
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * 0.25

def whoosh(dur=0.55, amp=0.16, rising=True):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n)
    seg = n // 12
    for k in range(12):                      # stepped band sweep
        c = 400 * 2 ** ((k if rising else 11 - k) / 3)
        out[k * seg:(k + 1) * seg] = bp(x, c * 0.7, min(c * 1.4, 20000))[k * seg:(k + 1) * seg]
    shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return lp(out, 9000) * shape * amp

def tick(f=2400, amp=0.12):
    n = int(0.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 220) * amp

def tap():                                   # finger on glass + soft body
    return tick(3200, 0.2) + tick(700, 0.15)

def coin():
    return bell(mtof(88), 1.0, 0.11) + np.pad(bell(mtof(93), 1.0, 0.11), (int(0.08 * SR), 0))[: int(1.0 * SR)]

def success():                               # up-arpeggio, C major
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate((72, 76, 79, 84)):
        add(out, bell(mtof(m), 1.2, 0.08), k * 0.07)
    return out

def riser(dur):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    x = bp(rng.standard_normal(n), 800, 6000) * t ** 2.5 * 0.12
    f = 200 + 600 * t ** 2
    x += np.sin(2 * np.pi * np.cumsum(f) / SR) * t ** 2 * 0.04
    return x

def impact():
    n = int(2.5 * SR); t = np.arange(n) / SR
    f = 38 + 50 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 0.38


# ---------- arrangement ----------
CHORDS = {"C": [60, 64, 67, 74], "G": [55, 62, 67, 71], "Am": [57, 60, 64, 67], "F": [53, 57, 60, 64]}
ROOTS = {"C": 36, "G": 43, "Am": 45, "F": 41}
INTRO = ["Am", "F", "G"]                       # bars 0-2: the problem, filtered
LOOP = ["C", "G", "Am", "F"]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]


def build_music(total, g0, bar, beat, final_bar, breakdowns, tail):
    m = np.zeros(int(total * SR))
    for note in CHORDS["Am"]:                  # pre-roll under the hook
        add(m, pad_note(note, round(max(g0, 0.1) + 0.9, 3), 700), 0)
    for b in range(final_bar):
        t0 = g0 + b * bar
        ch = INTRO[b] if b < 3 else LOOP[(b - 3) % 4]
        quiet = b in breakdowns
        for note in CHORDS[ch]:
            add(m, pad_note(note, round(bar + 0.9, 3), 700 if b < 3 else (1400 if quiet else 2200)), t0)
        if b < 3: continue
        outro = b >= final_bar - 2
        for s in range(8):
            if quiet and s % 2: continue
            add(m, pluck(CHORDS[ch][ARP[s]] + 12), t0 + s * beat / 2)
        if quiet: continue
        for k in (0, 2):
            add(m, bass(ROOTS[ch], beat * 1.8), t0 + k * beat)
            if not (outro and k == 2): add(m, kick(), t0 + k * beat)
        if not outro:
            for s in range(4): add(m, hat(), t0 + (s + 0.5) * beat)
    tf = g0 + final_bar * bar                  # final chord on the logo, then a soft arpeggio under the lockup
    for note in CHORDS["C"] + [48]:
        add(m, pad_note(note, round(tail + 1.0, 3), 2600) * 1.4, tf)
    add(m, bass(36, 3.0) * 1.2, tf)
    for b in range(3):
        for s in range(8):
            add(m, pluck(CHORDS[["C", "F", "C"][b]][ARP[s]] + 12) * (0.6 - 0.15 * b), tf + 0.6 + b * bar + s * beat / 2)
    fade = int(2.5 * SR)
    m[-fade:] *= np.linspace(1, 0, fade)
    return m


def build_sfx(total, cues, vo, final_t):
    s = np.zeros(int(total * SR))
    one = {"pop": lambda: pop(), "whoosh": lambda: whoosh(0.6, 0.16), "whoosh_down": lambda: whoosh(0.45, 0.12, rising=False),
           "tick": lambda: tick(2300, 0.08), "tap": tap, "coin": coin, "success": success, "bell": lambda: bell(mtof(84), 0.8, 0.07)}
    for c in cues:
        t = vo(c["t"])
        if c["type"] == "riser_to_final":         # starts at t, peaks on the final chord: never under a word
            add(s, riser(max(0.5, final_t - t)), t)
        elif c["type"] == "impact_final":
            add(s, impact(), final_t)
        elif c["type"] in ("whoosh", "whoosh_down"):
            add(s, one[c["type"]](), t - 0.4)    # a whoosh peaks ~0.4 s in: centre it on the move
        else:
            add(s, one[c["type"]](), t)
    return s


def stereo_reverb(x, wet, decay):
    n = int(2.2 * SR); t = np.arange(n) / SR
    out = []
    for seed in (1, 2):
        ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-t / decay)
        ir = lp(ir, 6000); ir /= np.sqrt((ir ** 2).sum())
        out.append(x + wet * fftconvolve(x, ir)[: len(x)])
    return np.stack(out, 1)


def read_vo(path, tmpdir):
    tmp = Path(tmpdir) / "_vo48k.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), str(tmp)], check=True)
    sr, x = wavfile.read(tmp); tmp.unlink()
    return x.astype(np.float64) / 32768


def duck_curve(v, total_n, offset):
    e = np.zeros(total_n); i = int(offset * SR)
    e[i:i + len(v)] = np.abs(v)[: total_n - i]
    win = int(0.05 * SR)
    e = np.convolve(e, np.ones(win) / win, "same")
    e = np.minimum(e / (np.percentile(e[e > 0], 90) + 1e-9), 1)
    rel = int(0.35 * SR)                       # slow release so the bed doesn't pump
    e = np.convolve(e, np.ones(rel) / rel, "full")[: total_n]
    return 1 - 0.55 * np.minimum(e * 1.6, 1)   # down to ~-7 dB under speech


def rms_db(x):
    a = np.abs(x).mean(axis=-1) if x.ndim > 1 else np.abs(x)
    active = x[a > 1e-3]
    return 20 * np.log10(np.sqrt((active ** 2).mean()) + 1e-12)


def to_rms(x, target): return x * db(target - rms_db(x))
def to_peak(x, target): return x * db(target) / (np.abs(x).max() + 1e-12)


def write(path, x):
    peak = np.abs(x).max()
    if peak > 0.99: x = x * 0.99 / peak
    wavfile.write(path, SR, (x * 32767).astype(np.int16))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", required=True)
    ap.add_argument("--cues", required=True)
    ap.add_argument("--out", default="audio")
    a = ap.parse_args()
    c = json.load(open(a.cues, encoding="utf-8"))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    offset, bpm = c.get("vo_offset", 1.0), c["bpm"]
    beat = 60 / bpm; bar = 4 * beat
    vo = lambda t: t + offset
    g0 = vo(c["anchor"]) - 3 * bar
    final_t = g0 + c["final_bar"] * bar
    v = read_vo(a.vo, out)
    tail = c.get("tail", 8.0)
    total = max(final_t + tail, offset + len(v) / SR + 1.5)
    n = int(total * SR)
    v = to_rms(v, -20)                                                   # VO -20 dBFS RMS, bed 13 dB under, SFX peaks -9
    music = to_rms(stereo_reverb(build_music(total, g0, bar, beat, c["final_bar"], set(c.get("breakdowns", [])), tail), 0.35, 0.6), -33)
    music *= duck_curve(v, n, offset)[:, None]
    sfx = to_peak(stereo_reverb(build_sfx(total, c.get("sfx", []), vo, final_t), 0.18, 0.35), -9)
    vo_bus = np.zeros((n, 2)); i = int(offset * SR)
    vo_bus[i:i + len(v)] = v[: n - i, None]
    write(out / "music.wav", music)
    write(out / "sfx.wav", sfx)
    write(out / "_mix.wav", vo_bus + music + sfx)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out / "_mix.wav"), "-af", "loudnorm=I=-14:TP=-1:LRA=11",
                    "-ar", "48000", "-b:a", "192k", str(out / "mix.mp3")], check=True)
    (out / "_mix.wav").unlink()
    print(f"total {total:.2f}s  bar {bar:.3f}s  brand line {vo(c['anchor']):.2f}s  final chord {final_t:.2f}s -> {out / 'mix.mp3'}")


if __name__ == "__main__":
    main()

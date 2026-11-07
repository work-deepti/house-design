"""Neutral background score for the GH-18 R1 house tour, synthesised from scratch (numpy only, no samples).

Calm and unobtrusive under the voice-over: felt piano, warm string pads, soft bells; no beat. D major at 70 BPM, a slow
four-chord cycle (two bars per chord); a gentle swell on each floor change and a resolve on D for the end card. The
length follows film/r1/shots.mjs (title + shots + end card), so it always matches the edit.
Usage: python3 film/r1/score.py out.wav
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
BPM = 70
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(11)


def tour():
    js = "import * as m from './film/r1/shots.mjs'; console.log(JSON.stringify({shots: m.SHOTS, intro: m.INTRO_SEC, outro: m.OUTRO_SEC}))"
    out = subprocess.run(['node', '--input-type=module', '-e', js], cwd=os.path.dirname(os.path.dirname(HERE)), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


T = tour()
TOTAL = T['intro'] + sum(s['sec'] for s in T['shots']) + T['outro']
TAIL = 3.0
N = int((TOTAL + TAIL) * SR)
BARS = int(np.ceil(TOTAL / BAR))
# floor changes (seconds) for the swells
CHANGES, t, prev = [], T['intro'], None
for s in T['shots']:
    lv = s.get('lvl')
    if lv and prev and lv != prev:
        CHANGES.append(t)
    prev = lv or prev
    t += s['sec']
END_CARD = TOTAL - T['outro']


def hz(note):
    """'D3', 'Bb2', 'F#4' -> frequency."""
    names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n = names[note[0]]
    rest = note[1:]
    if rest.startswith('b'):
        n -= 1; rest = rest[1:]
    elif rest.startswith('#'):
        n += 1; rest = rest[1:]
    midi = 12 * (int(rest) + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, a, d, s, r, sus_len):
    t = np.arange(n) / SR
    e = np.zeros(n)
    e = np.where(t < a, t / max(a, 1e-6), e)
    dd = (t >= a) & (t < a + d)
    e = np.where(dd, 1 - (1 - s) * (t - a) / max(d, 1e-6), e)
    e = np.where((t >= a + d) & (t < sus_len), s, e)
    rr = t >= sus_len
    e = np.where(rr, s * np.exp(-(t - sus_len) / max(r, 1e-6) * 3), e)
    return e


# ------------------------------------------------------------------ instruments

def pad(freqs, dur, bright=1.0, attack=0.9, release=1.8):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for f in freqs:
        for k, det in enumerate((-0.11, 0.0, 0.13)):
            ff = f * 2 ** (det / 12)
            ph = rng.random() * 6.28
            sig = np.zeros(n)
            for h in range(1, 9):                      # warm, soft saw
                sig += np.sin(2 * np.pi * ff * h * t + ph * h) / h ** (1.6 - 0.35 * bright)
            pan = (-0.6, 0.0, 0.6)[k]
            out[:, 0] += sig * np.sqrt(0.5 * (1 - pan))
            out[:, 1] += sig * np.sqrt(0.5 * (1 + pan))
    e = env_adsr(n, attack, 0.5, 0.85, release, dur)
    trem = 1 + 0.06 * np.sin(2 * np.pi * 0.23 * t)
    return out * (e * trem)[:, None] / (len(freqs) * 3)


def pluck(f, dur=0.9, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * f * t) + 0.35 * bright * np.sin(4 * np.pi * f * t) * np.exp(-t * 9)
           + 0.15 * bright * np.sin(6 * np.pi * f * t) * np.exp(-t * 14))
    e = np.minimum(t / 0.004, 1) * np.exp(-t * 4.2)
    return sig * e


def bell(f, dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dcy) for m, a, dcy in ((1, 1, 1.2), (2.76, 0.4, 2.2), (5.4, 0.2, 3.5), (8.9, 0.08, 5)))
    return sig * np.minimum(t / 0.002, 1)


def bass(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)
    e = np.minimum(t / 0.01, 1) * np.exp(-t * 1.2)
    return np.tanh(sig * 1.4) * e


def kick(power=1.0):
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = rng.normal(size=n) * np.exp(-t * 300) * 0.25
    return np.tanh((body + click) * 1.6 * power)


def _unused_hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    x = rng.normal(size=n)
    x = np.diff(np.concatenate([[0], x]))             # crude high-pass
    return x * np.exp(-t * (14 if open_ else 70)) * 0.3


def impact(length=4.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 28 + 60 * np.exp(-t * 5)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.1)
    noise = rng.normal(size=n)
    lp = np.zeros(n)                                    # darkened noise burst
    a = 0.02
    acc = 0.0
    for i in range(0, min(n, int(1.2 * SR))):
        acc += a * (noise[i] - acc)
        lp[i] = acc
    burst = lp * np.exp(-t * 3.0) * 6
    return np.tanh((sub * 1.3 + burst) * 1.2)


def riser(length):
    n = int(length * SR)
    t = np.arange(n) / SR
    k = t / length
    noise = rng.normal(size=n)
    out = np.zeros(n)
    acc = 0.0
    for i in range(n):                                  # one-pole low-pass opening up
        a = 0.01 + 0.5 * k[i] ** 2
        acc += a * (noise[i] - acc)
        out[i] = acc
    sweep = np.sin(2 * np.pi * np.cumsum(180 + 900 * k ** 2) / SR) * 0.25
    return (out * 0.9 + sweep) * k ** 2.2


def reverse_swell(length):
    r = riser(length)
    return r * 0.8


def reverb(x, seconds=2.8, seed=1, wet=0.35):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.random.default_rng(seed).normal(size=n) * np.exp(-t * 6.9 / seconds)
    ir[:int(0.012 * SR)] = 0                           # pre-delay
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1
    while size < len(x) + n:
        size *= 2
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return x * (1 - wet) + y * wet * 2.2



def piano(f, dur=2.5, vel=0.8):
    """Felt piano: inharmonic partials with per-partial decay, soft hammer."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    B = 0.00035
    sig = np.zeros(n)
    for h in range(1, 11):
        fh = f * h * np.sqrt(1 + B * h * h)
        if fh > 9000:
            break
        a = (1 / h ** 1.25) * (0.55 + 0.45 * vel) ** (h - 1)
        dcy = 0.55 + 0.42 * h + f / 900
        sig += a * np.sin(2 * np.pi * fh * t + h) * np.exp(-t * dcy)
    hammer = rng.normal(size=n) * np.exp(-t * 180) * 0.04 * vel
    e = np.minimum(t / 0.004, 1) * np.minimum(1, (dur - t) / 0.25).clip(0, 1)
    return (sig * 0.6 + hammer) * e * vel


def shaker():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    x = np.convolve(rng.normal(size=n), np.ones(6) / 6, 'same')        # soft, darker brush
    x = np.diff(np.concatenate([[0], x])) * 2.0
    return x * np.minimum(t / 0.012, 1) * np.exp(-t * 40) * 0.08


def soft_kick():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 42 + 50 * np.exp(-t * 22)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * np.minimum(t / 0.003, 1)



def piano(f, dur=3.0, vel=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    B = 0.00035
    sig = np.zeros(n)
    for h in range(1, 10):
        fh = f * h * np.sqrt(1 + B * h * h)
        if fh > 8000:
            break
        sig += (1 / h ** 1.3) * (0.5 + 0.5 * vel) ** (h - 1) * np.sin(2 * np.pi * fh * t + h) * np.exp(-t * (0.5 + 0.4 * h + f / 900))
    e = np.minimum(t / 0.006, 1) * np.clip((dur - t) / 0.3, 0, 1)
    return sig * e * vel * 0.6


CHORDS = [  # (pad voicing, bass root, arpeggio)
    (['D3', 'A3', 'E4', 'F#4'], 'D2', ['D4', 'A4', 'F#5', 'E5']),
    (['B2', 'F#3', 'A3', 'D4'], 'B1', ['B3', 'F#4', 'D5', 'A4']),
    (['G2', 'D3', 'F#3', 'B3'], 'G1', ['G3', 'D4', 'B4', 'F#4']),
    (['A2', 'E3', 'G3', 'D4'], 'A1', ['A3', 'E4', 'D5', 'G4']),
]

pad_bus = np.zeros((N, 2))
pno_bus = np.zeros((N, 2))
fx_bus = np.zeros((N, 2))
low = np.zeros((N, 2))


def add(bus, sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    if sig.ndim == 1:
        bus[i:i + len(sig), 0] += sig * gain * np.sqrt(0.5 * (1 - pan))
        bus[i:i + len(sig), 1] += sig * gain * np.sqrt(0.5 * (1 + pan))
    else:
        bus[i:i + len(sig)] += sig * gain


for b in range(BARS):
    t0 = b * BAR
    if t0 >= END_CARD:
        break
    voicing, root, arp = CHORDS[(b // 2) % 4]
    if b % 2 == 0:
        add(pad_bus, pad([hz(x) for x in voicing], 2 * BAR, bright=0.7, attack=1.6 if b else 3.0, release=3.0), t0, 0.8)
        add(low, bass(hz(root), 2 * BAR) * 0.5, t0, 0.45)
    if b >= 1:                                       # sparse piano: four notes a bar, soft
        for k in range(4):
            add(pno_bus, piano(hz(arp[k]), 3.2, 0.5 + 0.1 * (k == 0)), t0 + k * BEAT + rng.normal() * 0.008, 0.45, (k - 1.5) * 0.25)
    if b % 4 == 3:                                   # a soft bell every fourth bar
        add(fx_bus, bell(hz(arp[2]) * 2, 4.0), t0 + 2 * BEAT, 0.07, 0.3)
for c in CHANGES:                                    # gentle swell into each floor
    add(fx_bus, np.convolve(reverse_swell(2.5), np.ones(8) / 8, 'same') * 0.22, c - 2.5, 1.0)
# end card: resolve on D
tt = np.arange(int(8 * SR)) / SR
add(pad_bus, pad([hz(x) for x in ['D3', 'A3', 'E4', 'F#4', 'A4']], T['outro'] + 1, bright=0.8, attack=0.6, release=4.0), END_CARD, 0.9)
add(low, np.sin(2 * np.pi * hz('D2') * tt) * np.exp(-tt * 0.5) * np.minimum(tt / 0.03, 1), END_CARD, 0.4)
for k, nt in enumerate(['D5', 'A5', 'F#5']):
    add(pno_bus, piano(hz(nt), 5.0, 0.55), END_CARD + k * 0.45, 0.5, (-0.3, 0.3, 0.0)[k])

pad_l, pad_r = reverb(pad_bus[:, 0], 4.5, 5, 0.55), reverb(pad_bus[:, 1], 4.5, 6, 0.55)
pn_l, pn_r = reverb(pno_bus[:, 0], 3.5, 9, 0.42), reverb(pno_bus[:, 1], 3.5, 10, 0.42)
fx_l, fx_r = reverb(fx_bus[:, 0], 5.0, 3, 0.55), reverb(fx_bus[:, 1], 5.0, 4, 0.55)
mix = np.stack([pad_l * 0.9 + pn_l + fx_l + low[:, 0], pad_r * 0.9 + pn_r + fx_r + low[:, 1]], 1)
t = np.arange(N) / SR
mix *= (np.minimum(1, t / 2.5) * np.clip((TOTAL + TAIL - t) / 5.0, 0, 1))[:, None]
mix = np.tanh(mix * 1.05)
mix /= np.max(np.abs(mix)) / 0.89

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'score_r1.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, '%.1f s' % (N / SR))

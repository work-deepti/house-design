"""Original score for the GH-18 R1 walkthrough film, synthesised from scratch (numpy only, no samples).

Warm, unhurried "property film" writing: felt piano, string pads, a soft heartbeat pulse, bells on the terraces.
80 BPM, 4/4, D major; one bar = 3 s = 72 frames, matching film/r1/shots.mjs (2 bars of title before the first shot).
  bars  0-1   title: pad swell, single piano notes
  bars  2-8   arrival (aerial, facade, approach): piano arpeggios enter
  bars  9-29  ground floor: bass and a soft pulse; the pulse drops out for the mandir (bars 18-19, bells);
              strings lift the deck and garden (bars 24-28)
  bars 30-41  first floor: swell into the chapter, fuller arpeggio
  bars 42-47  second floor terraces: strings and bells
  bars 48-49  afternoon-to-evening breakdown
  bars 50-54  finale: low bloom, resolve on D, long tail
Usage: python3 film/r1/score.py out.wav
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 80
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 55
TAIL = 3.0
N = int((BARS * BAR + TAIL) * SR)
rng = np.random.default_rng(11)


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


CHORDS = [  # (pad voicing, bass root, arpeggio)
    (['D3', 'A3', 'E4', 'F#4'], 'D2', ['D4', 'A4', 'E5', 'F#5', 'A5', 'F#5', 'E5', 'A4']),     # Dmaj9
    (['B2', 'F#3', 'A3', 'D4'], 'B1', ['B3', 'F#4', 'A4', 'D5', 'F#5', 'D5', 'A4', 'F#4']),    # Bm7
    (['G2', 'D3', 'F#3', 'B3'], 'G1', ['G3', 'D4', 'F#4', 'B4', 'D5', 'B4', 'F#4', 'D4']),     # Gmaj7
    (['A2', 'E3', 'G3', 'D4'], 'A1', ['A3', 'E4', 'G4', 'D5', 'E5', 'D5', 'G4', 'E4']),        # Asus4 (7)
]
FINAL = (['D3', 'A3', 'E4', 'F#4', 'A4'], 'D2', ['D5', 'A5', 'E6'])

pad_bus = np.zeros((N, 2))
pno_bus = np.zeros((N, 2))
fx_bus = np.zeros((N, 2))
drums = np.zeros((N, 2))
low = np.zeros((N, 2))


def add(bus, sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    if sig.ndim == 1:
        gl, gr = gain * np.sqrt(0.5 * (1 - pan)), gain * np.sqrt(0.5 * (1 + pan))
        bus[i:i + len(sig), 0] += sig * gl
        bus[i:i + len(sig), 1] += sig * gr
    else:
        bus[i:i + len(sig)] += sig * gain


def t_of(bar, beat=0.0):
    return bar * BAR + beat * BEAT


def section(b):
    if b < 2: return 'title'
    if b < 9: return 'arrive'
    if 18 <= b <= 19: return 'mandir'
    if b < 30: return 'gf'
    if b < 42: return 'ff'
    if b < 48: return 'sf'
    if b < 50: return 'evening'
    return 'finale'


for b in range(BARS):
    sec = section(b)
    if sec == 'finale':
        if b == 50:
            voicing, root, _ = FINAL
            add(pad_bus, pad([hz(x) for x in voicing], 4 * BAR, bright=1.1, attack=0.4, release=5.0), t_of(b), 0.95)
            add(pad_bus, pad([hz(x) * 2 for x in voicing[1:]], 4 * BAR, bright=1.4, attack=1.2, release=5.0), t_of(b), 0.35)
            tt = np.arange(int(9 * SR)) / SR
            add(low, np.sin(2 * np.pi * hz(root) * tt) * np.exp(-tt * 0.45) * np.minimum(tt / 0.02, 1), t_of(b), 0.55)
            add(fx_bus, impact(5.0) * 0.45, t_of(b), 1.0)
            for k, nt in enumerate(FINAL[2]):
                add(pno_bus, piano(hz(nt), 6.0, 0.7), t_of(b, k * 0.5), 0.55, (-0.3, 0.1, 0.35)[k])
        if b == 52:
            add(pno_bus, piano(hz('D4'), 7.0, 0.55), t_of(b, 2), 0.5, -0.1)
            add(pno_bus, piano(hz('A4'), 7.0, 0.5), t_of(b, 2.5), 0.4, 0.2)
        continue
    voicing, root, arp = CHORDS[b % 4]
    if sec == 'mandir':
        voicing, root, arp = CHORDS[2]
    pad_gain = {'title': 0.75, 'arrive': 0.8, 'gf': 0.7, 'mandir': 0.85, 'ff': 0.75, 'sf': 0.8, 'evening': 1.0}[sec]
    add(pad_bus, pad([hz(x) for x in voicing], BAR, bright=0.8, attack=1.0 if b else 2.4, release=2.5), t_of(b), pad_gain)
    if sec in ('sf', 'evening') or 24 <= b <= 28:        # strings an octave up
        add(pad_bus, pad([hz(x) * 2 for x in voicing[1:]], BAR, bright=1.3, attack=1.3, release=2.5), t_of(b), 0.32)
    # piano
    if sec == 'title':
        add(pno_bus, piano(hz(arp[0]), 4.0, 0.55), t_of(b, 0), 0.6, -0.2)
        add(pno_bus, piano(hz(arp[3]), 4.0, 0.45), t_of(b, 2), 0.45, 0.25)
    elif sec == 'mandir':
        for k in (0, 2):
            add(pno_bus, piano(hz(arp[k * 2]), 3.5, 0.45), t_of(b, k), 0.5, 0.1)
    elif sec == 'evening':
        for k in range(4):
            add(pno_bus, piano(hz(arp[k * 2]), 3.5, 0.5), t_of(b, k), 0.45, (k - 1.5) * 0.2)
    else:
        step = 1.0 if sec == 'arrive' and b < 5 else 0.5
        vel = {'arrive': 0.6, 'gf': 0.62, 'ff': 0.68, 'sf': 0.72}[sec]
        for k in range(int(4 / step)):
            nt = arp[(k * int(step * 2)) % 8]
            acc = 1.0 if k % (2 if step == 1 else 4) == 0 else 0.82
            add(pno_bus, piano(hz(nt), 2.2, vel * acc), t_of(b, k * step) + rng.normal() * 0.006, 0.42, ((k % 4) - 1.5) * 0.18)
    # bass
    if b >= 9 and sec not in ('mandir',):
        add(low, bass(hz(root), BAR * 0.95) * 0.9, t_of(b), 0.5)
    # pulse: heartbeat kick on 1 and 3, shaker on the off-beats
    pulse = (13 <= b <= 17) or (20 <= b <= 29) or (31 <= b <= 47)
    if pulse:
        for beat in (0, 2):
            add(drums, soft_kick(), t_of(b, beat), 0.55)
        for k in range(8):
            if k % 2:
                add(drums, shaker(), t_of(b, k * 0.5) + rng.normal() * 0.004, 0.5 if k % 4 == 3 else 0.32, 0.35)
    # bells: mandir (temple-like), terraces and evening sparkle
    if sec == 'mandir':
        add(fx_bus, bell(hz('D5'), 5.0), t_of(b, 0), 0.35, -0.2)
        add(fx_bus, bell(hz('A5'), 5.0), t_of(b, 2), 0.22, 0.25)
    if sec in ('sf', 'evening'):
        for k, nt in enumerate((arp[3], arp[4])):
            add(fx_bus, bell(hz(nt) * 2, 3.5), t_of(b, 1 + 2 * k), 0.1, (-0.4, 0.4)[k])

# swells into the chapters
for b, length in ((2, 2.4), (9, 2.4), (24, 3.0), (30, 3.0), (42, 3.0), (50, 3.0)):
    add(fx_bus, np.convolve(reverse_swell(length), np.ones(8) / 8, 'same') * 0.3, t_of(b) - length, 1.0)

pad_l = reverb(pad_bus[:, 0], 4.0, 5, 0.5)
pad_r = reverb(pad_bus[:, 1], 4.0, 6, 0.5)
pn_l = reverb(pno_bus[:, 0], 3.2, 9, 0.38)
pn_r = reverb(pno_bus[:, 1], 3.2, 10, 0.38)
fx_l = reverb(fx_bus[:, 0], 4.5, 3, 0.5)
fx_r = reverb(fx_bus[:, 1], 4.5, 4, 0.5)
dr_l = reverb(drums[:, 0], 1.2, 7, 0.15)
dr_r = reverb(drums[:, 1], 1.2, 8, 0.15)
mix_l = pad_l * 0.9 + pn_l + fx_l + dr_l * 0.8 + low[:, 0]
mix_r = pad_r * 0.9 + pn_r + fx_r + dr_r * 0.8 + low[:, 1]

t = np.arange(N) / SR
fade = np.minimum(1, t / 2.0) * np.clip((BARS * BAR + TAIL - t) / 5.0, 0, 1)
mix = np.stack([mix_l, mix_r], 1) * fade[:, None]
mix = np.tanh(mix * 1.05)
mix /= np.max(np.abs(mix)) / 0.89

out = sys.argv[1] if len(sys.argv) > 1 else 'score_r1.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, '%.1f s' % (N / SR))

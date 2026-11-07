"""Edit, grade, label, mix and encode the GH-18 R1 house tour (16:9).

Reads the frames from film/r1/render.mjs (film/r1/frames/<shot>/NNNN.jpg|png), the neutral score (film/r1/score.py) and,
if present, the voice-over lines from film/r1/voice.py (film/r1/vo/manifest.json). Grades the picture gently (soft filmic
contrast, warm highlights, light vignette, fine grain), adds the title and end cards and a minimal floor + room label on
each shot, cuts straight between shots with a short dip only where the tour changes floor, ducks the music under the
voice, and pipes everything into ffmpeg (H.264 High, AAC 320k, loudness-normalised).

Usage: python3 film/r1/post.py [out.mp4] [--4k] [--preview N]
  --4k        3840 x 2160 from the 4K frames (render.mjs 4k); default 1920 x 1080 (also from 4K frames, downsized)
  --preview N write every Nth frame as a JPG into the folder `out` instead of encoding
"""
import json
import os
import shutil
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.dirname(os.path.dirname(HERE))
FPS, SR = 24, 48000
UHD = '--4k' in sys.argv
W, H = (3840, 2160) if UHD else (1920, 1080)
K = W / 1920                     # the layout below is written for 1920 wide
FONTS = os.path.join(os.path.dirname(HERE), 'fonts')
DIP = 8                          # frames of dip-to-black on each side of a floor change


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(round(size * K)))


def k(v):
    return v * K


F_SUB = font('InterDisplay-Light.otf', 26)
F_SMALL = font('InterDisplay-Light.otf', 20)
F_LVL = font('InterDisplay-Medium.otf', 18)
F_ROOM = font('InterDisplay-Light.otf', 30)


def tour():
    js = "import * as m from './film/r1/shots.mjs'; console.log(JSON.stringify({shots: m.SHOTS, intro: m.INTRO_SEC, outro: m.OUTRO_SEC}))"
    out = subprocess.run(['node', '--input-type=module', '-e', js], cwd=VIEWER, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# ------------------------------------------------------------------ grade
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RAD = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2)
VIGNETTE = (1 - 0.16 * np.clip(RAD / 1.3, 0, 1) ** 2.4)[..., None]
del YY, XX, RAD


def grade(img, frame_no):
    x = img.astype(np.float32) / 255.0
    x = x + 0.2 * (x * x * (3 - 2 * x) - x)
    lum = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    shadow = np.array([0.99, 1.0, 1.015], np.float32)
    high = np.array([1.025, 1.005, 0.97], np.float32)
    x = x * (shadow + (high - shadow) * np.clip(lum * 1.2, 0, 1))
    x = lum + (x - lum) * 1.04
    x = x * VIGNETTE
    g = np.random.default_rng(frame_no).normal(0, 0.007, (H, W, 1)).astype(np.float32)
    x = x + g * (1 - np.abs(lum - 0.5))
    return np.clip(x, 0, 1) * 255


# ------------------------------------------------------------------ text
def tracked(draw, xy, text, fnt, fill, tracking, anchor='l'):
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x, y = xy
    if anchor == 'm':
        x -= total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + tracking
    return total


def overlay(canvas, draw_fn, alpha):
    if alpha <= 0.002:
        return canvas
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    if alpha < 1:
        a = np.array(layer)
        a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
        layer = Image.fromarray(a)
    base = canvas.convert('RGBA')
    base.alpha_composite(layer)
    return base.convert('RGB')


def ramp(f, a, b):
    return float(np.clip((f - a) / max(1, b - a), 0, 1))


def smooth(v):
    return v * v * (3 - 2 * v)


def title_card(d, a, scale=1.0, sub='CELEBRITY HOMES  ·  PALAM VIHAR  ·  GURUGRAM', line3=None):
    fnt = font('InterDisplay-Thin.otf', 190 * scale)
    tracked(d, (W / 2, H / 2 - k(150) * scale), 'GH-18', fnt, (245, 240, 232, int(255 * a)), k(38) * scale, 'm')
    tracked(d, (W / 2, H / 2 + k(70)), sub, F_SUB, (225, 214, 196, int(255 * a)), k(9), 'm')
    if line3:
        tracked(d, (W / 2, H / 2 + k(118)), line3, F_SMALL, (170, 160, 146, int(255 * a)), k(6), 'm')


# ------------------------------------------------------------------ edit
def build_timeline(T):
    tl = [('intro', f) for f in range(round(T['intro'] * FPS))]
    S = T['shots']
    for n, s in enumerate(S):
        frames = round(s['sec'] * FPS)
        lv, prev, nxt = s.get('lvl'), S[n - 1].get('lvl') if n else None, S[n + 1].get('lvl') if n + 1 < len(S) else None
        dip_in = bool(n) and bool(lv) and bool(prev) and lv != prev
        dip_out = bool(lv) and bool(nxt) and lv != nxt
        for i in range(frames):
            tl.append(('shot', dict(s=s, i=i, n=frames, dip_in=dip_in, dip_out=dip_out, first=n == 0, last=n == len(S) - 1)))
    tl += [('outro', f) for f in range(round(T['outro'] * FPS))]
    return tl


def load(sid, i):
    base = os.path.join(HERE, 'frames', sid, '%04d' % (i + 1))
    for ext in ('.jpg', '.png'):
        if os.path.exists(base + ext):
            im = Image.open(base + ext).convert('RGB')
            return np.array(im if im.size == (W, H) else im.resize((W, H), Image.LANCZOS))
    return np.full((H, W, 3), 40, np.uint8)            # not rendered yet (preview): grey slate


def render_frame(kind, data, fno, T):
    canvas = Image.new('RGB', (W, H), (0, 0, 0))
    if kind == 'intro':
        n = round(T['intro'] * FPS)
        a = smooth(ramp(data, 10, 34)) * (1 - smooth(ramp(data, n - 18, n - 2)))
        return overlay(canvas, lambda d: title_card(d, a, 1.0 + 0.03 * data / n), 1.0)
    if kind == 'outro':
        n = round(T['outro'] * FPS)
        a = smooth(ramp(data, 4, 20)) * (1 - smooth(ramp(data, n - 20, n - 2)))
        return overlay(canvas, lambda d: title_card(d, a, 0.72, sub='GROUND  ·  FIRST  ·  SECOND FLOOR (PROPOSED)',
                                                     line3='VISUALISED FROM THE REVISION R1 DESIGN MODEL'), 1.0)
    s, i, n = data['s'], data['i'], data['n']
    pic = grade(load(s['id'], i), fno)
    fade = 1.0
    if data['first']:
        fade *= smooth(ramp(i, 0, 24))
    if data['dip_in']:
        fade *= smooth(ramp(i, 0, DIP))
    if data['dip_out']:
        fade *= 1 - smooth(ramp(i, n - DIP, n - 1))
    if data['last']:
        fade *= 1 - smooth(ramp(i, n - 30, n - 1))
    canvas = Image.fromarray((pic * fade).astype(np.uint8))
    if s.get('lvl') and s.get('room'):                    # minimal label: floor over room, bottom left
        a = smooth(ramp(i, 8, 22)) * (1 - smooth(ramp(i, n - 20, n - 6)))
        lvl, room = s['lvl'].upper(), s['room'].upper()

        def label(d):
            x, y = k(84), H - k(132)
            d.line([(x, y + k(10)), (x + k(34), y + k(10))], fill=(226, 196, 150, 235), width=max(1, round(k(2))))
            tracked(d, (x + k(48), y), lvl, F_LVL, (226, 196, 150, 255), k(6))
            tracked(d, (x, y + k(34)), room, F_ROOM, (246, 242, 235, 255), k(5))
        canvas = overlay(canvas, label, a)
    return canvas


# ------------------------------------------------------------------ audio
def read_wav(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels())


def decode(path):
    out = subprocess.run([shutil.which('ffmpeg'), '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True)
    return np.frombuffer(out.stdout, np.float32)


def mix_audio(total_sec, out_wav):
    score = os.path.join(HERE, 'score_r1.wav')
    if not os.path.exists(score):
        subprocess.run([sys.executable, os.path.join(HERE, 'score.py'), score], check=True)
    music = read_wav(score)
    n = int((total_sec + 1) * SR)
    music = np.pad(music, ((0, max(0, n - len(music))), (0, 0)))[:n]
    vo = np.zeros(n, np.float32)
    man = os.path.join(HERE, 'vo', 'manifest.json')
    if os.path.exists(man):
        lines = json.load(open(man))['lines']
        free = 0.0
        for ln in lines:
            sig = decode(os.path.join(HERE, 'vo', ln['file']))
            start = max(ln['start'], free)                    # never let two lines overlap
            i = int(start * SR)
            sig = sig[: max(0, n - i)]
            vo[i:i + len(sig)] += sig
            free = start + len(sig) / SR + 0.4
        print('voice-over: %d lines' % len(lines))
    else:
        print('voice-over: none (run film/r1/voice.py to add it)')
    # duck the music about 9 dB under the voice, with a soft attack and release
    env = (np.abs(vo) > 0.01).astype(np.float32)
    win = int(0.35 * SR)
    env = np.convolve(env, np.ones(win) / win, 'same')
    env = np.clip(env * 4, 0, 1)
    duck = 1 - 0.65 * env
    peak = np.max(np.abs(vo)) or 1
    mix = music * duck[:, None] * 0.8 + (vo / peak * 0.9)[:, None]
    mix /= max(1.0, np.max(np.abs(mix)) / 0.95)
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    preview = int(sys.argv[sys.argv.index('--preview') + 1]) if '--preview' in sys.argv else 0
    if preview:
        args = [a for a in args if a != str(preview)]
    out = args[0] if args else os.path.join(HERE, 'GH-18_R1_house_tour%s.mp4' % ('_4K' if UHD else ''))
    T = tour()
    tl = build_timeline(T)
    dur = len(tl) / FPS
    print('timeline: %d frames (%.1f s), %dx%d' % (len(tl), dur, W, H))
    if preview:
        os.makedirs(out, exist_ok=True)
        for fno in range(0, len(tl), preview):
            render_frame(*tl[fno], fno, T).save(os.path.join(out, 'p%05d.jpg' % fno), quality=88)
        return
    audio = os.path.join(HERE, 'mix_r1.wav')
    mix_audio(dur, audio)
    cmd = [shutil.which('ffmpeg'), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
           '-i', audio, '-af', 'afade=t=out:st=%.2f:d=3,loudnorm=I=-16:TP=-1.5:LRA=11' % (dur - 3),
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17' if UHD else '16', '-tune', 'film', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fno, (kind, data) in enumerate(tl):
        p.stdin.write(render_frame(kind, data, fno, T).tobytes())
        if fno % 240 == 0:
            print('frame', fno, '/', len(tl), flush=True)
    p.stdin.close()
    p.wait()
    print('wrote', out)


if __name__ == '__main__':
    main()

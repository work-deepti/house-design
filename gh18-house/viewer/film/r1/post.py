"""Edit, grade, title and encode the GH-18 R1 walkthrough film.

Reads the frames rendered by film/r1/render.mjs (film/r1/frames/<shot>/NNNN.png) and the score (film/r1/score.py),
cuts on the bar lines of the 80 BPM score, grades the picture (soft filmic contrast, warm highlights, gentle vignette,
fine grain), letterboxes it to 2.39:1 inside 1920x1080, adds the title, chapter and room captions, dips to black
between floors, and pipes the result into ffmpeg (H.264 High, CRF 16, AAC 320k, loudness-normalised).

Usage: python3 film/r1/post.py out.mp4 [--4k] [--preview N]
  --4k       : UHD 3840x2160 from 3840x1608 frames (render.mjs 4k); default 1920x1080 from 1920x804 frames
  --preview N: write every Nth frame as a JPG into the folder `out` instead of encoding
"""
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.dirname(os.path.dirname(HERE))
FPS = 24
UHD = '--4k' in sys.argv
W, H, PIC_H = (3840, 2160, 1608) if UHD else (1920, 1080, 804)
K = W / 1920                 # layout below is written for 1920 wide and scaled by K
TOP = (H - PIC_H) // 2
FONTS = os.path.join(os.path.dirname(HERE), 'fonts')
DIP = 10                     # frames of dip-to-black on each side of a floor change


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(round(size * K)))


def k(v):
    return v * K


F_SUB = font('InterDisplay-Light.otf', 26)
F_CAP = font('InterDisplay-Light.otf', 30)
F_NUM = font('InterDisplay-Medium.otf', 20)
F_CHAP = font('InterDisplay-Medium.otf', 19)
F_SMALL = font('InterDisplay-Light.otf', 20)


def meta():
    js = "import * as m from './film/r1/shots.mjs'; console.log(JSON.stringify({shots: m.SHOTS, bar: m.BAR, intro: m.INTRO_BARS, outro: m.OUTRO_FRAMES}))"
    out = subprocess.run(['node', '--input-type=module', '-e', js], cwd=VIEWER, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# ------------------------------------------------------------------ grade
YY, XX = np.mgrid[0:PIC_H, 0:W].astype(np.float32)
RAD = np.sqrt(((XX - W / 2) / (W / 2)) ** 2 + ((YY - PIC_H / 2) / (PIC_H / 2)) ** 2)
VIGNETTE = (1 - 0.2 * np.clip(RAD / 1.3, 0, 1) ** 2.4)[..., None]


def grade(img, frame_no):
    x = img.astype(np.float32) / 255.0
    x = x + 0.24 * (x * x * (3 - 2 * x) - x)                                   # soft filmic S-curve
    lum = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    shadow = np.array([0.985, 1.0, 1.02], np.float32)                          # neutral-cool shadows
    high = np.array([1.03, 1.005, 0.965], np.float32)                          # warm highlights
    x = x * (shadow + (high - shadow) * np.clip(lum * 1.2, 0, 1))
    x = lum + (x - lum) * 1.05
    x = x * VIGNETTE
    g = np.random.default_rng(frame_no).normal(0, 0.009, (PIC_H, W, 1)).astype(np.float32)
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


def title_card(d, a_title, a_sub, scale=1.0, sub='CELEBRITY HOMES  ·  PALAM VIHAR  ·  GURUGRAM', line3=None):
    if a_title > 0:
        fnt = font('InterDisplay-Thin.otf', int(190 * scale))
        tracked(d, (W / 2, H / 2 - k(150) * scale), 'GH-18', fnt, (245, 240, 232, int(255 * a_title)), int(k(38) * scale), 'm')
    if a_sub > 0:
        tracked(d, (W / 2, H / 2 + k(70)), sub, F_SUB, (225, 214, 196, int(255 * a_sub)), k(9), 'm')
        if line3:
            tracked(d, (W / 2, H / 2 + k(118)), line3, F_SMALL, (170, 160, 146, int(255 * a_sub)), k(6), 'm')


# ------------------------------------------------------------------ edit
def build_timeline(M):
    bar_f = round(M['bar'] * FPS)
    tl = [('intro', f) for f in range(M['intro'] * bar_f)]
    S = M['shots']
    cap_no = 0
    for k, s in enumerate(S):
        n = round(s['bars'] * bar_f)
        if s.get('caption'):
            cap_no += 1
        dip_in = bool(s.get('chapter')) and k > 0 or s['id'] == 'e01_timelapse'
        dip_out = k + 1 < len(S) and (bool(S[k + 1].get('chapter')) or S[k + 1]['id'] == 'e01_timelapse')
        for i in range(n):
            tl.append(('shot', dict(s=s, i=i, n=n, cap=cap_no if s.get('caption') else None, dip_in=dip_in, dip_out=dip_out, first=k == 0, last=k == len(S) - 1)))
    tl += [('outro', f) for f in range(M['outro'])]
    return tl


def render_frame(kind, data, fno, frames_dir, M):
    canvas = Image.new('RGB', (W, H), (0, 0, 0))
    if kind == 'intro':
        f, n = data, M['intro'] * round(M['bar'] * FPS)
        a_t = smooth(ramp(f, 16, 52)) * (1 - smooth(ramp(f, n - 26, n - 6)))
        a_s = smooth(ramp(f, 60, 86)) * (1 - smooth(ramp(f, n - 26, n - 6)))
        return overlay(canvas, lambda d: title_card(d, a_t, a_s, 1.0 + 0.03 * f / n), 1.0)
    if kind == 'outro':
        f = data
        a = smooth(ramp(f, 0, 6)) * (1 - smooth(ramp(f, M['outro'] - 30, M['outro'] - 4)))
        return overlay(canvas, lambda d: title_card(d, a, a, 0.72, sub='GROUND  ·  FIRST  ·  SECOND FLOOR (PROPOSED)',
                                                     line3='VISUALISED FROM THE REVISION R1 DESIGN MODEL'), 1.0)
    s, i, n = data['s'], data['i'], data['n']
    path = os.path.join(frames_dir, s['id'], '%04d.png' % (i + 1))
    if not os.path.exists(path):
        path = path[:-4] + '.jpg'
    if os.path.exists(path):
        pic = np.array(Image.open(path).convert('RGB').resize((W, PIC_H), Image.LANCZOS))
    else:                                                    # not rendered yet (preview): grey slate
        pic = np.full((PIC_H, W, 3), 40, np.uint8)
    pic = grade(pic, fno)
    fade = 1.0
    if data['first']:
        fade *= smooth(ramp(i, 0, 30))                           # fade up from the title
    if data['dip_in']:
        fade *= smooth(ramp(i, 0, DIP))
    if data['dip_out']:
        fade *= 1 - smooth(ramp(i, n - DIP, n - 1))
    if data['last']:
        fade *= 1 - 0.55 * smooth(ramp(i, n - 120, n - 60))     # darken under the end title
    canvas.paste(Image.fromarray((pic * fade).astype(np.uint8)), (0, TOP))

    if s.get('chapter'):                                     # floor chapter, top left
        a = smooth(ramp(i, 12, 30)) * (1 - smooth(ramp(i, 96, 116)))
        txt = s['chapter'].upper()

        def chap(d):
            x, y = k(96), TOP + k(70)
            d.line([(x, y + k(11)), (x + k(40), y + k(11))], fill=(226, 196, 150, 230), width=round(k(2)))
            tracked(d, (x + k(56), y), txt, F_CHAP, (236, 228, 214, 255), k(8))
        canvas = overlay(canvas, chap, a)
    if data['cap']:
        a = smooth(ramp(i, 14, 30)) * (1 - smooth(ramp(i, n - 22, n - 8)))
        txt = s['caption'].upper()

        def cap(d):
            x, y = k(96), TOP + PIC_H - k(92)
            tracked(d, (x, y + k(4)), '%02d' % data['cap'], F_NUM, (226, 196, 150, 255), k(3))
            d.line([(x + k(44), y + k(16)), (x + k(92), y + k(16))], fill=(226, 196, 150, 220), width=round(k(2)))
            tracked(d, (x + k(108), y), txt, F_CAP, (246, 242, 235, 255), k(6))
        canvas = overlay(canvas, cap, a)
    if data['last']:
        a = smooth(ramp(i, n - 110, n - 70))
        canvas = overlay(canvas, lambda d: title_card(d, a, a, 0.72, sub='CELEBRITY HOMES  ·  PALAM VIHAR  ·  GURUGRAM'), 1.0)
    return canvas


def main():
    pos = [a for a in sys.argv[1:] if not a.startswith('--') and not a.isdigit()]
    out = pos[0] if pos else os.path.join(HERE, 'GH-18_R1_walkthrough%s.mp4' % ('_4K' if UHD else ''))
    preview = int(sys.argv[sys.argv.index('--preview') + 1]) if '--preview' in sys.argv else 0
    frames_dir = os.path.join(HERE, 'frames')
    M = meta()
    tl = build_timeline(M)
    dur = len(tl) / FPS
    print('timeline: %d frames (%.1f s)' % (len(tl), dur))
    if preview:
        os.makedirs(out, exist_ok=True)
        for fno in range(0, len(tl), preview):
            kind, data = tl[fno]
            render_frame(kind, data, fno, frames_dir, M).save(os.path.join(out, 'p%05d.jpg' % fno), quality=88)
        return
    score = os.path.join(HERE, 'score_r1.wav')
    if not os.path.exists(score):
        subprocess.run([sys.executable, os.path.join(HERE, 'score.py'), score], check=True)
    cmd = [shutil.which('ffmpeg'), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
           '-i', score, '-af', 'afade=t=out:st=%.2f:d=4,loudnorm=I=-16:TP=-1.5:LRA=11' % (dur - 4),
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17' if UHD else '16', '-tune', 'film', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fno, (kind, data) in enumerate(tl):
        p.stdin.write(render_frame(kind, data, fno, frames_dir, M).tobytes())
        if fno % 240 == 0:
            print('frame', fno, '/', len(tl), flush=True)
    p.stdin.close()
    p.wait()
    print('wrote', out)


if __name__ == '__main__':
    main()

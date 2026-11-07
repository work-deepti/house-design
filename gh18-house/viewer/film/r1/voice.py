"""Voice-over for the GH-18 R1 house tour: one MP3 per shot that has a `vo` line in film/r1/shots.mjs.

Uses Microsoft's neural Indian-English voices through the free `edge-tts` tool (no account or key; needs internet).
Run on the Mac (pip install edge-tts), then python3 film/r1/post.py mixes the lines in, ducking the music under them.
Usage: python3 film/r1/voice.py [--voice en-IN-NeerjaNeural | en-IN-PrabhatNeural] [--rate -4%]
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VO_DIR = os.path.join(HERE, 'vo')


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def tour():
    js = "import * as m from './film/r1/shots.mjs'; console.log(JSON.stringify({shots: m.SHOTS, intro: m.INTRO_SEC}))"
    out = subprocess.run(['node', '--input-type=module', '-e', js], cwd=os.path.dirname(os.path.dirname(HERE)), capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def duration(path):
    out = subprocess.run([shutil.which('ffprobe') or 'ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True)
    return float(out.stdout.strip() or 0)


async def main():
    import edge_tts
    voice, rate = arg('--voice', 'en-IN-NeerjaNeural'), arg('--rate', '-4%')
    os.makedirs(VO_DIR, exist_ok=True)
    T = tour()
    t, lines = T['intro'], []
    for s in T['shots']:
        if s.get('vo'):
            lines.append((s['id'], t, s['vo']))
        t += s['sec']
    manifest = []
    for k, (sid, start, text) in enumerate(lines):
        path = os.path.join(VO_DIR, sid + '.mp3')
        await edge_tts.Communicate(text, voice, rate=rate).save(path)
        d = duration(path)
        nxt = lines[k + 1][1] if k + 1 < len(lines) else 1e9
        room = nxt - (start + 0.6)
        flag = '' if d <= room else '   <-- runs %.1f s into the next line; post.py will delay that one' % (d - room)
        print('%-18s %5.1f s at %6.1f s%s' % (sid, d, start + 0.6, flag))
        manifest.append(dict(id=sid, file=os.path.basename(path), start=round(start + 0.6, 3), dur=round(d, 3)))
    with open(os.path.join(VO_DIR, 'manifest.json'), 'w') as f:
        json.dump(dict(voice=voice, rate=rate, lines=manifest), f, indent=1)
    print('wrote', len(manifest), 'lines to', VO_DIR)


if __name__ == '__main__':
    asyncio.run(main())

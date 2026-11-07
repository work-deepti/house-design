// Render the R1 film's frames from the live three.js model of Revision R1 (/v1/, headless Chromium, SwiftShader).
// Usage (from gh18-house/viewer, after `npm run build`):
//   node film/r1/render.mjs [gpu] [4k] [only=a,b] [still] [w=1920 h=804] [part=0/2] [port=4181]
//   gpu   : a visible Chromium window on the real GPU (fast on a Mac, Apple silicon / Metal); default: headless SwiftShader (CPU)
//   4k    : 3840 x 1608 frames (2.39:1 inside 3840 x 2160); post.py --4k makes the UHD film from them
//   still : render the frame at u=0.5 of each shot (or at=0.1,0.9 for several) into film/r1/stills/
//   part=k/n : render every n-th frame starting at k, so n processes can share the work (resumable: existing frames are skipped)
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, renameSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SHOTS, poseAt, framesOf } from './shots.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const args = Object.fromEntries(process.argv.slice(2).map((a) => a.split('=')).map(([k, v]) => [k, v ?? true]));
const only = args.only ? String(args.only).split(',') : null;
const W = +(args.w || (args['4k'] ? 3840 : 1920)), H = +(args.h || (args['4k'] ? 1608 : 804));
const PORT = +(args.port || 4181);
const [PK, PN] = args.part ? String(args.part).split('/').map(Number) : [0, 1];
const AT = args.at ? String(args.at).split(',').map(Number) : [0.5];
const EXT = args['4k'] || args.jpg ? 'jpg' : 'png';        // 4K frames as JPEG q95 (~1.5 MB each instead of ~6 MB)

// the cloud build container ships its own Playwright + Chromium under /opt; anywhere else (a Mac) use the project's
const PW_OPT = '/opt/node22/lib/node_modules/playwright/index.mjs';
const { chromium } = existsSync(PW_OPT) ? await import(PW_OPT) : await import('playwright');

let server = null;
try { await fetch(`http://localhost:${PORT}/`); } catch {
  server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], { cwd: root, stdio: 'pipe' });
  await new Promise((res) => { server.stdout.on('data', (d) => { if (String(d).includes(String(PORT))) res(); }); setTimeout(res, 8000); });
}
const browser = args.gpu
  ? await chromium.launch({ headless: false, args: ['--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'] })
  : await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('pageerror', (e) => console.error('pageerror', String(e)));
  await page.goto(`http://localhost:${PORT}/v1/?headless&cinema`);
  await page.waitForFunction(() => window.viewer && (window.viewer.ready || window.viewer.error), null, { timeout: 300000 });
  const err = await page.evaluate(() => window.viewer.error);
  if (err) throw new Error(err);
  await page.waitForTimeout(5000);    // textures

  const t0 = Date.now();
  let done = 0;
  for (const shot of SHOTS) {
    if (only && !only.includes(shot.id)) continue;
    const n = framesOf(shot);
    const dir = path.join(here, args.still ? 'stills' : path.join('frames', shot.id));
    mkdirSync(dir, { recursive: true });
    const list = args.still ? AT.map((u) => Math.round(u * (n - 1))) : [...Array(n).keys()].filter((i) => i % PN === PK);
    for (const i of list) {
      const file = args.still ? path.join(dir, `${shot.id}_${String(i).padStart(3, '0')}.${EXT}`) : path.join(dir, String(i + 1).padStart(4, '0') + '.' + EXT);
      if (!args.still && existsSync(file)) continue;
      const pose = poseAt(shot, n > 1 ? i / (n - 1) : 0);
      await page.evaluate((o) => { window.viewer.cine(o); window.viewer.renderFrame(); }, pose);
      const tmp = file + '.tmp.' + EXT;
      await page.screenshot(EXT === 'jpg' ? { path: tmp, type: 'jpeg', quality: 95 } : { path: tmp });
      renameSync(tmp, file);          // never leave a half-written frame behind
      done++;
      if (done % 20 === 0 || args.still) console.log(`${shot.id} ${i + 1}/${n}  ${((Date.now() - t0) / 1000 / done).toFixed(1)} s/frame`);
    }
  }
  console.log('done', done, 'frames in', ((Date.now() - t0) / 60000).toFixed(1), 'min');
} finally {
  await browser.close();
  if (server) server.kill();
  process.exit(0);
}

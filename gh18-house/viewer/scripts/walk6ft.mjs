// 6-ft person route test on the R1 model (F18): walks plan routes through the viewer's own floors and colliders with a
// 250 mm body radius and a 1.86 m head (6'-0" + shoes). Reports the nearest obstacle per leg, the biggest step and the
// lowest overhead. Usage (from gh18-house/viewer, with `npx vite preview --port 4187` running): node scripts/walk6ft.mjs
let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  ({ chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs'));
}
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const v = await b.newPage();
await v.goto('http://localhost:4187/v1/?headless');
await v.waitForFunction(() => window.viewer && window.viewer.ready, null, { timeout: 180000 });
const routes = {   // [x, y] in model mm; the first point carries the foot level in m (GF floor 0.45, lawn 0)
  'Lounge -> door -> deck -> lawn': [[4880, 8450, 0.45], [4880, 8350], [4500, 6400], [4350, 6000], [4350, 5590], [4350, 5000], [3400, 4300], [3400, 2400], [3400, 1500]],
  'Door -> tulsi (devotee spot)': [[4350, 6000, 0.45], [4350, 5590], [4350, 5150], [2200, 5000], [1500, 3200], [1500, 2400], [1450, 1650]],
};
const res = await v.evaluate(({ routes }) => {
  const wk = viewer.walker();
  const R = 250, HEAD = 1.86;
  const segDist = (px, py, ax, ay, bx, by) => {
    const dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy || 1;
    const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / L));
    return Math.hypot(px - ax - t * dx, py - ay - t * dy);
  };
  const inside = (x, y, poly) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c; } return c; };
  const dist = (x, y, poly) => inside(x, y, poly) ? 0 : Math.min(...poly.map((p, i) => segDist(x, y, ...p, ...poly[(i + 1) % poly.length])));
  const out = {};
  for (const [name, pts] of Object.entries(routes)) {
    let seg = [], foot = pts[0][2], minClear = 1e9, minAt = null, maxStep = 0, stepAt = null, head = 1e9, headAt = null, problems = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const [ax, ay] = pts[i], [bx, by] = pts[i + 1];
      let sMin = 1e9; const n = Math.ceil(Math.hypot(bx - ax, by - ay) / 25);
      for (let k = 0; k <= n; k++) {
        const x = ax + ((bx - ax) * k) / n, y = ay + ((by - ay) * k) / n;
        const hs = wk.heights(x, y);
        let best = null; for (const hh of hs) if (Math.abs(hh - foot) <= 0.42 && (best === null || Math.abs(hh - foot) < Math.abs(best - foot))) best = hh;
        if (best === null) { problems.push(`no floor within a step at ${x.toFixed(0)},${y.toFixed(0)}`); continue; }
        const st = Math.abs(best - foot); if (st > maxStep + 1e-6) { maxStep = st; stepAt = [x, y, foot, best]; }
        foot = best;
        for (const c of wk.data.colliders) {
          if (c.y1 < foot + 0.05) continue;                       // below the ankle: a floor edge, not an obstacle
          const d = dist(x, y, c.poly);
          if (c.y0 > foot + 0.05) {                                // overhead: a lintel, beam or rafter
            if (d < R && c.y0 - foot < head) { head = c.y0 - foot; headAt = [x, y]; }
            continue;
          }
          if (d < minClear) { minClear = d; minAt = [x, y]; }
          if (d < sMin) sMin = d;
        }
      }
      seg.push(`${ax},${ay} -> ${bx},${by}: nearest obstacle ${Math.round(sMin)} mm`);
    }
    out[name] = { seg, minClear, minAt, maxStep, stepAt, head, headAt, problems: [...new Set(problems)].slice(0, 5) };
  }
  return out;
}, { routes });
console.log(JSON.stringify(res, null, 1));
await b.close();

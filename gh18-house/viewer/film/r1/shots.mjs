// GH-18 R1 walkthrough film: shot list for the finalised Revision R1 model (/v1/).
// World units are metres: X = plan x (East = -X, West = +X), Z = plan y (South / back lawn = 0, North / street = +Z),
// Y up from natural ground. Floors: GF +0.45, FF +3.75, SF +7.05 (eye height about 1.5 above each).
// Cuts land on the bar lines of the 80 BPM score (1 bar = 3 s = 72 frames at 24 fps).
// time: 0 = afternoon, ~0.55 = golden hour, 1 = dusk (viewer.cine blends sun, sky and interior lights).
// The camera only moves through the model as built: no object, room or material is added or changed.
// No neighbourhood scenery (context.js): only the house and its own plot (owner, Nov 2026); a shot can opt in with context: true.
export const FPS = 24;
export const BPM = 80;
export const BAR = 240 / BPM;            // 3.0 s = 72 frames
export const INTRO_BARS = 2;             // black + title, made in post
export const OUTRO_FRAMES = 96;          // end card after the last shot

const DAY = 0.32, GOLD = 0.6;
export const SHOTS = [
  // ---------------------------------------------------------------- arrival
  { id: 'a01_aerial', bars: 3, chapter: null, caption: null, time: 0.5, exposure: 1.0, fov: 34,
    keys: [{ pos: [30, 24, 46], target: [4.7, 3.5, 14] }, { pos: [20, 11, 37], target: [4.7, 4.5, 16] }, { pos: [13.5, 3.6, 31], target: [5.0, 4.6, 18.5] }] },
  { id: 'a02_facade', bars: 2, caption: 'The curved glass foyer', time: 0.5, exposure: 1.0, fov: 32,
    keys: [{ pos: [-1.0, 3.4, 30.5], target: [3.8, 3.2, 19.5] }, { pos: [7.5, 3.2, 30.0], target: [5.2, 3.0, 19.8] }] },
  { id: 'a03_approach', bars: 2, time: 0.5, exposure: 0.95, fov: 46,
    keys: [{ pos: [3.6, 1.95, 24.2], target: [4.6, 1.7, 19.0] }, { pos: [5.0, 2.0, 21.4], target: [5.2, 1.75, 17.0] }] },
  // ---------------------------------------------------------------- ground floor
  { id: 'g01_foyer', bars: 2, chapter: 'Ground floor', caption: 'Entrance foyer', time: DAY, exposure: 0.88, fov: 56, interior: true,
    keys: [{ pos: [5.5, 2.0, 20.0], target: [4.8, 1.6, 16.8] }, { pos: [5.15, 1.98, 17.6], target: [5.1, 1.7, 13.0] }] },
  { id: 'g02_study', bars: 2, caption: 'Guest lounge · Study', time: DAY, exposure: 0.88, fov: 56, interior: true,
    keys: [{ pos: [8.6, 1.95, 19.35], target: [6.3, 1.2, 16.6] }, { pos: [8.2, 1.9, 19.3], target: [7.6, 1.1, 15.3] }] },
  { id: 'g03_guest', bars: 2, caption: 'Guest room', time: DAY, exposure: 0.88, fov: 56, interior: true,
    keys: [{ pos: [3.6, 2.0, 18.25], target: [0.9, 1.15, 15.4] }, { pos: [3.4, 1.9, 17.3], target: [0.7, 1.1, 17.0] }] },
  { id: 'g04_lounge', bars: 3, caption: 'Family lounge', time: DAY, exposure: 0.88, fov: 52, interior: true,
    keys: [{ pos: [4.0, 1.75, 9.6], target: [7.6, 1.2, 6.4] }, { pos: [5.6, 1.7, 10.1], target: [7.2, 1.15, 6.0] }, { pos: [7.4, 1.65, 10.0], target: [6.0, 1.1, 6.0] }] },
  { id: 'g05_mandir', bars: 2, caption: 'Mandir', time: 0.88, exposure: 0.55, fov: 44, interior: true,
    keys: [{ pos: [5.7, 1.6, 8.35], target: [3.45, 1.45, 8.35] }, { pos: [4.75, 1.5, 8.35], target: [3.45, 1.45, 8.35] }] },
  { id: 'g06_dining', bars: 2, caption: 'Dining', time: DAY, exposure: 0.88, fov: 46, interior: true,
    keys: [{ pos: [6.6, 1.95, 11.2], target: [5.7, 1.1, 9.85] }, { pos: [7.5, 1.9, 10.3], target: [5.7, 1.1, 9.85] }, { pos: [7.4, 1.85, 8.9], target: [5.7, 1.1, 9.85] }] },
  { id: 'g07_kitchen', bars: 2, caption: 'Kitchen', time: DAY, exposure: 0.88, fov: 58, interior: true,
    keys: [{ pos: [2.75, 1.85, 10.9], target: [1.3, 1.0, 6.2] }, { pos: [2.3, 1.75, 10.2], target: [1.0, 1.0, 6.0] }] },
  { id: 'g09_deck', bars: 3, caption: 'Deck · Pergola', time: GOLD, exposure: 0.95, fov: 44,
    keys: [{ pos: [2.2, 1.9, 1.0], target: [5.8, 1.1, 4.0] }, { pos: [5.8, 2.3, 0.4], target: [5.8, 1.1, 4.0] }, { pos: [9.2, 1.9, 1.2], target: [5.8, 1.1, 4.0] }] },
  { id: 'g10_garden', bars: 2, caption: 'Back garden · Tulsi', time: GOLD, exposure: 0.95, fov: 46,
    keys: [{ pos: [4.2, 1.6, 0.9], target: [0.6, 1.3, 1.65] }, { pos: [2.9, 1.5, 1.3], target: [0.6, 1.2, 1.65] }] },
  { id: 'g11_stair', bars: 1, time: DAY, exposure: 0.88, fov: 58, interior: true,
    keys: [{ pos: [4.9, 2.0, 13.0], target: [8.3, 2.5, 13.45] }, { pos: [5.7, 2.35, 13.35], target: [8.6, 3.1, 13.45] }] },
  // ---------------------------------------------------------------- first floor
  { id: 'f01_lobby', bars: 1, chapter: 'First floor', caption: 'Lobby · Pantry', time: DAY, exposure: 0.88, fov: 58, interior: true,
    keys: [{ pos: [5.2, 5.35, 14.4], target: [6.2, 4.6, 11.0] }, { pos: [5.5, 5.3, 13.6], target: [6.3, 4.65, 11.0] }] },
  { id: 'f02_master', bars: 3, caption: 'Master bedroom', time: DAY, exposure: 0.88, fov: 54, interior: true,
    keys: [{ pos: [4.7, 5.35, 9.7], target: [8.6, 4.4, 8.7] }, { pos: [5.2, 5.25, 9.3], target: [8.7, 4.4, 8.4] }, { pos: [5.7, 5.15, 8.3], target: [7.8, 4.6, 6.2] }] },
  { id: 'f03_balcony', bars: 2, caption: 'Master balcony', time: GOLD, exposure: 0.95, fov: 48,
    keys: [{ pos: [5.2, 5.6, 1.0], target: [7.0, 4.8, 6.6] }, { pos: [7.6, 6.4, 1.6], target: [7.6, 4.9, 6.6] }] },
  { id: 'f04_bath', bars: 2, caption: 'Master washroom', time: DAY, exposure: 0.88, fov: 60, interior: true,
    keys: [{ pos: [1.7, 5.35, 8.8], target: [2.6, 4.3, 10.3] }, { pos: [1.5, 5.32, 9.0], target: [2.65, 4.35, 10.0] }] },
  { id: 'f05_bed3', bars: 2, caption: 'Bedroom 3', time: DAY, exposure: 0.88, fov: 56, interior: true,
    keys: [{ pos: [3.9, 5.3, 19.4], target: [1.0, 4.4, 15.2] }, { pos: [3.6, 5.2, 18.0], target: [0.8, 4.4, 15.0] }] },
  { id: 'f06_kids', bars: 2, caption: 'Kids room', time: DAY, exposure: 0.88, fov: 56, interior: true,
    keys: [{ pos: [6.3, 5.3, 17.0], target: [6.0, 4.6, 21.0] }, { pos: [6.6, 5.25, 17.6], target: [8.4, 4.4, 19.6] }] },
  // ---------------------------------------------------------------- second floor (proposed)
  { id: 's01_utility', bars: 3, chapter: 'Second floor · proposed', caption: 'Utility · Covered terrace', time: GOLD, exposure: 0.9, fov: 56,
    keys: [{ pos: [8.4, 8.75, 7.0], target: [6.6, 7.7, 8.8] }, { pos: [7.6, 8.75, 7.0], target: [3.0, 7.8, 10.0] }] },
  { id: 's02_terrace', bars: 3, caption: 'Front terrace', time: 0.66, exposure: 0.95, fov: 50,
    keys: [{ pos: [6.8, 9.6, 20.6], target: [2.2, 7.4, 17.4] }, { pos: [3.6, 10.6, 21.4], target: [2.0, 7.3, 16.8] }] },
  // ---------------------------------------------------------------- evening
  { id: 'e01_timelapse', bars: 2, caption: 'Afternoon to evening', time: [0.3, 1.0], exposure: [0.85, 1.1], fov: 46,
    keys: [{ pos: [1.6, 3.3, -6.5], target: [5.4, 4.6, 10] }, { pos: [3.6, 3.5, -4.8], target: [5.2, 4.6, 10] }] },
  { id: 'e02_finale', bars: 3, caption: null, time: 1.0, exposure: 1.15, fov: 34,
    keys: [{ pos: [11, 9.5, 33], target: [4.7, 4.5, 16] }, { pos: [20, 19, 41], target: [4.7, 4.0, 15] }, { pos: [32, 30, 52], target: [4.7, 3.5, 14] }] },
];

function catmull(p0, p1, p2, p3, t) {
  const t2 = t * t, t3 = t2 * t;
  return p1.map((_, i) => 0.5 * ((2 * p1[i]) + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2 + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3));
}
function path(points, u) {
  if (points.length === 1) return points[0];
  const n = points.length - 1;
  const s = Math.min(n - 1e-9, Math.max(0, u * n));
  const i = Math.floor(s), t = s - i;
  const P = (k) => points[Math.max(0, Math.min(n, k))];
  const p0 = i === 0 ? P(0).map((v, j) => 2 * v - P(1)[j]) : P(i - 1);
  const p3 = i + 1 === n ? P(n).map((v, j) => 2 * v - P(n - 1)[j]) : P(i + 2);
  return catmull(p0, P(i), P(i + 1), p3, t);
}
export function ease(u) { const e = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; return 0.55 * u + 0.45 * e; }
function value(v, u) {
  if (Array.isArray(v) && Array.isArray(v[0])) {
    for (let i = 1; i < v.length; i++) if (u <= v[i][0]) { const [u0, a] = v[i - 1], [u1, b] = v[i]; const k = (u - u0) / (u1 - u0 || 1); return a + (b - a) * k * k * (3 - 2 * k); }
    return v[v.length - 1][1];
  }
  if (Array.isArray(v)) { const s = u * u * (3 - 2 * u); return v[0] + (v[1] - v[0]) * s; }
  return v;
}
export function poseAt(shot, u) {
  const e = ease(u);
  return { pos: path(shot.keys.map((k) => k.pos), e), target: path(shot.keys.map((k) => k.target), e), fov: shot.fov,
    time: value(shot.time, u), exposure: shot.exposure === undefined ? undefined : value(shot.exposure, u), explode: 0,
    interior: !!shot.interior, cutaway: !!shot.cutaway, context: shot.context === true, floor: shot.floor || 'ALL' };
}
export const framesOf = (shot) => Math.round(shot.bars * BAR * FPS);

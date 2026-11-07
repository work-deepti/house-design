// GH-18 R1 house tour: shot list for the finalised Revision R1 model (/v1/), first-person, 16:9.
// Style after the owner's reference tour: eye-level, wide lens, walking room to room through the doorways, with close-ups
// of the details that matter (kitchen appliances, gas valve, storage, the concealed under-stair door).
// World units are metres: X = plan x (East = -X, West = +X), Z = plan y (South / back lawn = 0, North / street = +Z),
// Y up from natural ground. Floors: GF +0.45, FF +3.75, SF +7.05; eye height 1.55 above each (Y 2.0 / 5.3 / 8.6).
// time: 0 = afternoon, ~0.55 = golden hour, 1 = dusk. The camera only moves through the model as built: no object, room
// or material is added or changed, and there is no neighbourhood scenery (only the house and its plot).
// Each shot: sec (duration), lvl + room (the on-screen label; `floor` is the viewer's floor filter), optional vo (voice-over line, film/r1/voice.py).
export const FPS = 24;
export const INTRO_SEC = 4;
export const OUTRO_SEC = 4;

const D = 0.32, G = 0.6;                 // daylight, golden hour
const IN = { time: D, exposure: 0.9, fov: 62, interior: true };
const GF = 'Ground floor', FF = 'First floor', SF = 'Second floor (proposed)';
const k = (pos, target) => ({ pos, target });

export const SHOTS = [
  // ---------------------------------------------------------------- arrival
  { id: 'x01_aerial', sec: 7, time: 0.5, exposure: 1.0, fov: 34,
    keys: [k([30, 24, 46], [4.7, 3.5, 14]), k([20, 11, 37], [4.7, 4.5, 16]), k([13.5, 3.6, 31], [5.0, 4.6, 18.5])] },
  { id: 'x02_approach', sec: 6, lvl: GF, room: 'Entrance court', time: 0.5, exposure: 0.95, fov: 60,
    keys: [k([5.4, 1.95, 23.6], [5.0, 1.8, 17.0]), k([5.2, 2.0, 20.7], [5.0, 1.8, 16.5])],
    vo: 'Welcome to G H 18, at Celebrity Homes, Palam Vihar. A home planned around light, Vastu and everyday living.' },
  // ---------------------------------------------------------------- ground floor
  { id: 'g01_foyer', sec: 6, lvl: GF, room: 'Entrance foyer', ...IN,
    keys: [k([5.2, 2.0, 20.0], [6.0, 1.5, 18.3]), k([5.1, 2.0, 17.9], [5.1, 1.8, 14.0])] },
  { id: 'g02_lobby', sec: 5, lvl: GF, room: 'Lobby · stair and lift', ...IN,
    keys: [k([5.1, 2.0, 17.4], [5.6, 1.9, 13.0]), k([5.0, 2.0, 15.6], [7.0, 2.1, 12.4])] },
  { id: 'g03_study', sec: 7, lvl: GF, room: 'Guest lounge · study', ...IN,
    keys: [k([5.4, 2.0, 15.9], [8.8, 1.3, 16.0]), k([6.9, 1.95, 16.0], [8.9, 1.3, 17.2]), k([7.6, 1.95, 17.4], [6.2, 1.3, 19.0])] },
  { id: 'g04_store_door', sec: 6, lvl: GF, room: 'Concealed under-stair store door', ...IN, fov: 52,
    keys: [k([7.4, 1.7, 16.35], [6.55, 1.25, 15.25]), k([6.7, 1.6, 16.2], [6.55, 1.2, 15.25])],
    vo: 'In the guest lounge, a concealed, handleless door in the walnut panelling opens into storage under the staircase.' },
  { id: 'g05_store', sec: 5, lvl: GF, room: 'Under-stair store', ...IN, fov: 66,
    keys: [k([6.45, 1.95, 14.95], [7.6, 1.2, 14.2]), k([6.6, 1.85, 14.75], [8.2, 0.9, 14.4])] },
  { id: 'g06_guest', sec: 6, lvl: GF, room: 'Guest room', ...IN,
    keys: [k([4.6, 2.0, 15.1], [1.2, 1.3, 17.0]), k([3.4, 1.95, 15.6], [1.0, 1.2, 17.2])] },
  { id: 'g07_toilet', sec: 5, lvl: GF, room: 'Toilet', ...IN,
    keys: [k([4.5, 2.0, 13.5], [2.0, 1.4, 12.2]), k([3.3, 1.95, 12.9], [3.7, 1.2, 11.9])] },
  { id: 'g08_dining', sec: 6, lvl: GF, room: 'Dining', ...IN,
    keys: [k([5.2, 2.0, 11.0], [5.7, 1.2, 9.85]), k([7.2, 1.95, 10.6], [5.7, 1.2, 9.85])] },
  { id: 'g09_kitchen', sec: 6, lvl: GF, room: 'Kitchen', ...IN,
    keys: [k([3.9, 2.0, 9.85], [1.0, 1.5, 9.6]), k([2.4, 2.0, 9.4], [1.0, 1.3, 6.4])],
    vo: 'The kitchen works in three zones: storage and refrigeration, preparation and washing, and cooking.' },
  { id: 'g10_fridge', sec: 6, lvl: GF, room: 'Kitchen · fridge, pantry and appliance tower', ...IN,
    keys: [k([1.7, 2.0, 8.3], [0.6, 1.5, 10.1]), k([1.15, 2.0, 8.6], [3.1, 1.3, 8.4])],
    vo: 'A full-size refrigerator, a tall pantry, and a tower for the microwave and O T G.' },
  { id: 'g11_mixer', sec: 5, lvl: GF, room: 'Kitchen · microwave, OTG and mixer station', ...IN, fov: 56,
    keys: [k([1.7, 1.9, 7.9], [3.1, 1.5, 8.0]), k([2.0, 1.85, 7.6], [3.1, 1.2, 6.9])] },
  { id: 'g12_hob', sec: 6, lvl: GF, room: 'Kitchen · PNG hob, chimney and gas valve', ...IN, fov: 56,
    keys: [k([1.7, 1.85, 7.6], [0.4, 1.3, 7.2]), k([1.4, 1.8, 7.2], [0.4, 1.2, 6.7])],
    vo: 'The gas hob faces east, under a chimney, with an exposed gas line and an isolation valve within easy reach.' },
  { id: 'g13_drawers', sec: 5, lvl: GF, room: 'Kitchen · deep drawers and prep counter', ...IN, fov: 58,
    keys: [k([2.1, 1.75, 7.9], [0.9, 0.6, 7.2]), k([2.0, 1.8, 7.2], [1.5, 0.8, 5.9])] },
  { id: 'g14_wash', sec: 6, lvl: GF, room: 'Kitchen · sink, dish rack, RO water and bins', ...IN,
    keys: [k([2.1, 2.0, 9.6], [1.9, 1.3, 11.4]), k([2.0, 1.95, 10.05], [2.8, 1.1, 11.2])],
    vo: 'The washing zone has a double sink, a drainboard and dish rack, R O drinking water, and segregated waste bins.' },
  { id: 'g15_lounge', sec: 7, lvl: GF, room: 'Family lounge', ...IN,
    keys: [k([4.2, 2.0, 9.4], [7.6, 1.3, 6.4]), k([6.6, 1.95, 9.3], [8.6, 1.2, 7.0])] },
  { id: 'g16_mandir', sec: 5, lvl: GF, room: 'Mandir', ...IN, time: 0.88, exposure: 0.55, fov: 48,
    keys: [k([5.5, 1.8, 8.35], [3.45, 1.5, 8.35]), k([4.6, 1.7, 8.35], [3.45, 1.5, 8.35])] },
  { id: 'g17_deck', sec: 8, lvl: GF, room: 'Deck · covered seating', time: G, exposure: 0.95, fov: 48,
    keys: [k([2.2, 1.9, 1.0], [5.8, 1.1, 4.0]), k([5.8, 2.3, 0.4], [5.8, 1.1, 4.0]), k([9.2, 1.9, 1.2], [5.8, 1.1, 4.0])],
    vo: 'At the back, a covered deck under the pergola opens onto the garden and the tulsi.' },
  { id: 'g18_garden', sec: 5, lvl: GF, room: 'Back garden · tulsi', time: G, exposure: 0.95, fov: 50,
    keys: [k([4.2, 1.6, 0.9], [0.6, 1.3, 1.65]), k([2.9, 1.5, 1.3], [0.6, 1.2, 1.65])] },
  { id: 'g19_stair', sec: 4, lvl: GF, room: 'Stair', ...IN,
    keys: [k([4.9, 2.0, 13.0], [8.3, 2.5, 13.45]), k([5.7, 2.35, 13.35], [8.6, 3.1, 13.45])] },
  // ---------------------------------------------------------------- first floor
  { id: 'f01_lobby', sec: 4, lvl: FF, room: 'Lobby · pantry', ...IN,
    keys: [k([5.2, 5.35, 14.4], [6.2, 4.6, 11.0]), k([5.5, 5.3, 13.6], [6.3, 4.65, 11.0])] },
  { id: 'f02_master', sec: 7, lvl: FF, room: 'Master bedroom', ...IN,
    keys: [k([4.7, 5.35, 9.7], [8.6, 4.4, 8.7]), k([5.2, 5.25, 9.3], [8.7, 4.4, 8.4]), k([5.7, 5.15, 8.3], [7.8, 4.6, 6.2])],
    vo: 'Upstairs, the master bedroom opens onto its own balcony, with a walk-in dresser and a washroom with a bathtub.' },
  { id: 'f03_balcony', sec: 5, lvl: FF, room: 'Master balcony', time: G, exposure: 0.95, fov: 48,
    keys: [k([5.2, 5.6, 1.0], [7.0, 4.8, 6.6]), k([7.6, 6.4, 1.6], [7.6, 4.9, 6.6])] },
  { id: 'f04_wardrobe', sec: 5, lvl: FF, room: 'Master wardrobes', ...IN,
    keys: [k([6.0, 5.3, 8.8], [4.2, 4.6, 6.0]), k([5.2, 5.3, 8.4], [3.6, 4.6, 10.4])] },
  { id: 'f05_dresser', sec: 5, lvl: FF, room: 'Dresser', ...IN, fov: 66,
    keys: [k([3.7, 5.3, 6.9], [0.6, 4.7, 7.6]), k([2.7, 5.3, 7.1], [0.5, 4.6, 8.2])] },
  { id: 'f06_bath', sec: 5, lvl: FF, room: 'Master washroom', ...IN, fov: 66,
    keys: [k([1.7, 5.35, 8.8], [2.6, 4.3, 10.3]), k([1.5, 5.32, 9.0], [2.65, 4.35, 10.0])] },
  { id: 'f07_bed3', sec: 6, lvl: FF, room: 'Bedroom 3', ...IN,
    keys: [k([3.9, 5.3, 19.4], [1.0, 4.4, 15.2]), k([3.6, 5.2, 18.0], [0.8, 4.4, 15.0])] },
  { id: 'f08_bed3_toilet', sec: 4, lvl: FF, room: 'Bedroom 3 toilet', ...IN, fov: 66,
    keys: [k([2.85, 5.3, 13.4], [3.4, 4.4, 11.0]), k([2.9, 5.3, 12.6], [3.3, 4.3, 11.0])] },
  { id: 'f09_kids', sec: 7, lvl: FF, room: 'Kids room · study and storage', ...IN,
    keys: [k([6.3, 5.3, 17.0], [6.0, 4.6, 21.0]), k([6.6, 5.25, 17.6], [8.4, 4.4, 19.6]), k([7.0, 5.25, 18.0], [4.8, 4.8, 18.6])],
    vo: 'The kids room has a study desk, full-height storage, and the curved glass front.' },
  { id: 'f10_kids_glass', sec: 4, lvl: FF, room: 'Kids room · curved glazing', ...IN,
    keys: [k([7.2, 5.3, 18.2], [5.6, 4.9, 21.2]), k([6.9, 5.3, 19.0], [5.6, 4.9, 21.2])] },
  { id: 'f11_kids_toilet', sec: 4, lvl: FF, room: 'Kids toilet', ...IN, fov: 66,
    keys: [k([6.6, 5.3, 17.6], [7.6, 4.4, 15.7]), k([6.6, 5.3, 17.0], [7.8, 4.4, 15.6])] },
  // ---------------------------------------------------------------- second floor (proposed)
  { id: 's01_lobby', sec: 4, lvl: SF, room: 'Lobby', ...IN,
    keys: [k([6.6, 8.6, 13.9], [4.9, 8.0, 10.4]), k([5.6, 8.6, 12.6], [4.9, 8.0, 10.4])],
    vo: 'The proposed second floor adds a servant room, storage, and a covered terrace for washing and ironing.' },
  { id: 's02_servant', sec: 5, lvl: SF, room: 'Servant room', ...IN,
    keys: [k([4.8, 8.6, 13.95], [1.2, 7.8, 14.7]), k([3.6, 8.55, 14.1], [1.0, 7.8, 14.9])] },
  { id: 's03_servant_wc', sec: 4, lvl: SF, room: 'Servant washroom', ...IN, fov: 66,
    keys: [k([1.5, 8.6, 13.6], [1.6, 7.7, 11.3]), k([1.5, 8.6, 13.05], [1.7, 7.7, 11.3])] },
  { id: 's04_store', sec: 4, lvl: SF, room: 'Store · cupboards', ...IN, fov: 66,
    keys: [k([4.9, 8.6, 11.9], [2.6, 7.9, 12.2]), k([4.2, 8.6, 11.9], [2.6, 7.9, 12.4])] },
  { id: 's05_terrace_back', sec: 7, lvl: SF, room: 'Covered rear terrace', time: G, exposure: 0.9, fov: 60,
    keys: [k([8.4, 8.75, 7.0], [6.6, 7.7, 8.8]), k([7.6, 8.75, 7.0], [3.0, 7.8, 10.0])] },
  { id: 's06_laundry', sec: 5, lvl: SF, room: 'Washing and ironing', time: G, exposure: 0.9, fov: 60,
    keys: [k([3.6, 8.6, 8.7], [1.8, 7.9, 10.4]), k([2.8, 8.55, 9.0], [1.6, 7.9, 10.4])] },
  { id: 's07_terrace_front', sec: 7, lvl: SF, room: 'Front terrace', time: 0.66, exposure: 0.95, fov: 52,
    keys: [k([6.8, 9.6, 20.6], [2.2, 7.4, 17.4]), k([3.6, 10.6, 21.4], [2.0, 7.3, 16.8])],
    vo: 'And an open front terrace, for quiet evenings.' },
  // ---------------------------------------------------------------- evening
  { id: 'e01_timelapse', sec: 6, time: [0.3, 1.0], exposure: [0.85, 1.1], fov: 46,
    keys: [k([1.6, 3.3, -6.5], [5.4, 4.6, 10]), k([3.6, 3.5, -4.8], [5.2, 4.6, 10])] },
  { id: 'e02_finale', sec: 7, time: 1.0, exposure: 1.15, fov: 34,
    keys: [k([11, 9.5, 33], [4.7, 4.5, 16]), k([20, 19, 41], [4.7, 4.0, 15]), k([32, 30, 52], [4.7, 3.5, 14])] },
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
export const framesOf = (shot) => Math.round(shot.sec * FPS);

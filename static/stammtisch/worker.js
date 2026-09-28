/* Stammtisch engine worker.
 *
 * Runs the WebAssembly Jass engine off the main thread, so a PIMC search (~100 ms
 * a move, ~1 s for a coach call) never freezes the page.
 *
 * Two things are deliberate here:
 *
 *  - The round lives in the engine, not in JS. Dealing, legality, Weis, Stöck,
 *    the multipliers and the match bonus are the engine's own code, the same code
 *    that was replayed against 1.8 M logged human games. Reimplementing any of it
 *    in JS would only add a second, less tested set of rules.
 *
 *  - The worker holds every hand but only ever sends back the seats the human
 *    plays. The bots' cards never reach the page, so they cannot be read out of
 *    devtools.
 *
 * ABI note: the engine takes card sets as uint64 bitmasks, which Emscripten
 * exposes through the BigInt i64 ABI. Every hand crossing the boundary is a
 * BigInt, never a Number.
 */

importScripts("jass.js");

const ACT_TRUMP = 36, ACT_PUSH = 42;

let M = null, fn = null, buf = null;
let env = 0;                       // the engine round
let mine = [0];                    // seats the human plays
const agents = new Map();
const loaded = new Set();

const maskOf = (cards) => cards.reduce((m, c) => m | (1n << BigInt(c)), 0n);
function bitsOf(mask, n = 36) {
  const out = [];
  for (let i = 0; i < n; i++) if ((mask >> BigInt(i)) & 1n) out.push(i);
  return out;
}

function modelsFor(spec) {
  if (spec.startsWith("heuristic") || spec.startsWith("random")) return [];
  const need = ["trump_policy.bin", "card_policy.bin"];
  if (spec.includes("strong")) need.push("card_policy_strong.bin");
  return need;
}

async function ensureModels(spec) {
  for (const name of modelsFor(spec)) {
    if (loaded.has(name)) continue;
    postMessage({ type: "progress", what: name, state: "start" });
    const res = await fetch(`models/${name}`);
    if (!res.ok) throw new Error(`could not load models/${name} (${res.status})`);
    const bytes = new Uint8Array(await res.arrayBuffer());
    M.FS.writeFile(`/models/${name}`, bytes);
    loaded.add(name);
    postMessage({ type: "progress", what: name, state: "done", bytes: bytes.length });
  }
}

async function agentFor(spec) {
  if (agents.has(spec)) return agents.get(spec);
  await ensureModels(spec);
  const p = M.ccall("jass_agent_create", "number", ["string"], [spec]);
  if (!p) throw new Error(`unknown agent "${spec}"`);
  agents.set(spec, p);
  return p;
}

async function init() {
  M = await createJassModule();
  try { M.FS.mkdir("/models"); } catch (e) { /* already there */ }

  buf = {
    seat: M._malloc(1), legal: M._malloc(8), hands: M._malloc(4 * 8),
    history: M._malloc(36), info: M._malloc(8 * 2),
    action: M._malloc(2), done: M._malloc(1), score: M._malloc(2 * 2),
    agentMask: M._malloc(1),
    played: M._malloc(36), trick: M._malloc(16),
    cards: M._malloc(9 * 4), values: M._malloc(9 * 8), se: M._malloc(9 * 8),
    tinfo: M._malloc(7 * 8), human: M._malloc(7 * 8),
  };

  fn = {
    envCreate: M.cwrap("jass_env_create", "number", ["number", "bigint"]),
    envReset: M.cwrap("jass_env_reset", null, ["number"]),
    envSetRules: M.cwrap("jass_env_set_rules", null, ["number", "number"]),
    envObserve: M.cwrap("jass_env_observe", null,
      ["number", "number", "number", "number", "number", "number"]),
    envStep: M.cwrap("jass_env_step", "number",
      ["number", "number", "number", "number", "number"]),
    envAgentActions: M.cwrap("jass_env_agent_actions", null,
      ["number", "number", "number", "number"]),
    advise: M.cwrap("jass_advise", "number",
      ["bigint", "number", "number", "number", "number", "number", "number", "number",
       "number", "number", "number", "number", "bigint", "number", "number", "number"]),
    analyzeTrump: M.cwrap("jass_analyze_trump", null,
      ["bigint", "number", "number", "number", "number", "number", "number", "number",
       "number", "bigint", "number", "number"]),
    trumpPolicy: M.cwrap("jass_trump_policy", "number", ["bigint", "number", "number"]),
  };
}

/* Full observation, worker-side only. */
function observe() {
  fn.envObserve(env, buf.seat, buf.legal, buf.hands, buf.history, buf.info);
  const info = new Int16Array(M.HEAP16.buffer, buf.info, 8);
  const hands = Array.from(new BigUint64Array(M.HEAPU8.buffer, buf.hands, 4));
  const nPlayed = info[4];
  return {
    seat: new Int8Array(M.HEAP8.buffer, buf.seat, 1)[0],
    legal: new BigUint64Array(M.HEAPU8.buffer, buf.legal, 1)[0],
    hands,
    history: Array.from(new Int8Array(M.HEAP8.buffer, buf.history, 36)).slice(0, nPlayed),
    trump: info[0], declarer: info[1], pushed: !!info[2], dealer: info[3],
    nPlayed, trickFirst: info[5], points: [info[6], info[7]],
  };
}

/* What the page is allowed to see. */
function publicState() {
  const o = observe();
  const inTrump = o.trump < 0;
  return {
    seat: o.seat,
    toMove: o.seat,
    isMine: mine.includes(o.seat),
    trump: o.trump, declarer: o.declarer, pushed: o.pushed, dealer: o.dealer,
    nPlayed: o.nPlayed, trickFirst: o.trickFirst, points: o.points,
    history: o.history,
    myHands: Object.fromEntries(mine.map((s) => [s, bitsOf(o.hands[s])])),
    counts: o.hands.map((h) => bitsOf(h).length),
    legal: inTrump ? bitsOf(o.legal, 43).filter((a) => a >= ACT_TRUMP)
                   : bitsOf(o.legal, 36),
    phase: inTrump ? "trump" : "play",
  };
}

const handlers = {
  async newGame({ seed, rules, seats }) {
    if (env) M.ccall("jass_env_destroy", null, ["number"], [env]);
    mine = seats && seats.length ? seats : [0];
    env = fn.envCreate(1, BigInt(seed >>> 0));
    fn.envSetRules(env, rules);
    fn.envReset(env);
    return publicState();
  },

  async state() { return publicState(); },

  /* Apply one action for a seat the human plays. */
  async play({ action }) {
    const before = observe();
    if (!mine.includes(before.seat)) throw new Error("not your seat");
    if (!((before.legal >> BigInt(action)) & 1n)) throw new Error("illegal move");
    return step(action);
  },

  /* Let the engine act for the seat on move. */
  async bot({ spec }) {
    const a = await agentFor(spec);
    const o = observe();
    if (mine.includes(o.seat)) throw new Error("that seat is yours");
    new Int8Array(M.HEAP8.buffer, buf.agentMask, 1)[0] = 1;
    fn.envAgentActions(env, a, buf.agentMask, buf.action);
    const action = new Int16Array(M.HEAP16.buffer, buf.action, 1)[0];
    return { ...step(action), action, seat: o.seat };
  },

  /* Coach on a card decision: what was each legal card worth, from this seat's
     information only (never the true deal). */
  async adviseCard({ samples, seed }) {
    const o = observe();
    if (o.trump < 0 || !mine.includes(o.seat)) return null;
    const roll = await agentFor("net").catch(() => 0);
    M.HEAP8.set(Int8Array.from(o.history), buf.played);
    const n = fn.advise(o.hands[o.seat], buf.played, o.history.length, o.seat, o.dealer,
                        o.trump, o.pushed ? 1 : 0, rulesId, samples, 6, roll,
                        roll ? 0.5 : 0.0, BigInt(seed >>> 0),
                        buf.cards, buf.values, buf.se);
    if (n < 0) return null;
    const cards = new Int32Array(M.HEAP32.buffer, buf.cards, n);
    const values = new Float64Array(M.HEAPF64.buffer, buf.values, n);
    const se = new Float64Array(M.HEAPF64.buffer, buf.se, n);
    return Array.from({ length: n }, (_, i) => ({ card: cards[i], value: values[i], se: se[i] }));
  },

  /* Coach on the trump call, plus how often Swisslos players pick each mode. */
  async adviseTrump({ samples, seed }) {
    const o = observe();
    if (o.trump >= 0 || !mine.includes(o.seat)) return null;
    const roll = await agentFor("net").catch(() => 0);
    fn.analyzeTrump(o.hands[o.seat], 0, o.dealer, o.pushed ? 1 : 0, rulesId, samples, 6,
                    roll, roll ? 0.5 : 0.0, BigInt(seed >>> 0), buf.tinfo, 0);
    const values = Array.from(new Float64Array(M.HEAPF64.buffer, buf.tinfo, 7));
    let human = null;
    if (fn.trumpPolicy(o.hands[o.seat], o.pushed ? 1 : 0, buf.human) === 0)
      human = Array.from(new Float64Array(M.HEAPF64.buffer, buf.human, 7));
    return { values, human };
  },
};

let rulesId = 0;

function step(action) {
  new Int16Array(M.HEAP16.buffer, buf.action, 1)[0] = action;
  const illegal = fn.envStep(env, buf.action, 0, buf.done, buf.score);
  if (illegal) throw new Error("the engine rejected that move");
  const done = new Int8Array(M.HEAP8.buffer, buf.done, 1)[0] === 1;
  const out = { ...publicState(), done };
  if (done) {
    const sc = new Int16Array(M.HEAP16.buffer, buf.score, 2);
    out.finalScore = [sc[0], sc[1]];
    // The last card is forced, so the engine's history is complete here.
    out.history = observe().history;
  }
  return out;
}

let ready = null;

async function handle({ id, type, args }) {
  try {
    if (!ready) ready = init();
    await ready;
    if (type === "newGame") rulesId = (args && args.rules) || 0;
    const h = handlers[type];
    if (!h) throw new Error(`unknown request "${type}"`);
    const t0 = performance.now();
    const result = await h(args || {});
    postMessage({ id, ok: true, result, ms: performance.now() - t0 });
  } catch (err) {
    postMessage({ id, ok: false, error: String((err && err.message) || err) });
  }
}

/* Requests run strictly in the order they arrive. The page relies on this: it
   posts a coach request and the move itself back to back, and the advice must be
   computed on the position *before* that move. Handlers await internally, so
   without this chain a second request could interleave at an await point. */
let chain = Promise.resolve();
onmessage = (e) => { chain = chain.then(() => handle(e.data)); };

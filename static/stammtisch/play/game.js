/* Stammtisch — playing a Schieber round against the engine in the browser.
 *
 * The round itself lives in the WebAssembly engine, behind a worker (../worker.js).
 * This file is only the table: it renders what the worker reports, collects the
 * human's decisions, and asks the engine to act for the other seats.
 *
 * Seat conventions come straight from the engine:
 *   next_seat(s) = (s + 3) % 4   -> play order 0 -> 3 -> 2 -> 1
 *   partner(s)   = (s + 2) % 4   -> seat 0 and 2 are one team, 1 and 3 the other
 *   team_of(s)   = s & 1
 */
"use strict";

const SUITS = [
  { name: "Eichel",   glyph: "♦", red: true  },  // Swisslos maps Eichel to diamonds
  { name: "Rosen",    glyph: "♥", red: true  },
  { name: "Schilten", glyph: "♠", red: false },
  { name: "Schellen", glyph: "♣", red: false },
];
const RANKS = ["A", "K", "O", "U", "10", "9", "8", "7", "6"];
const TRUMP_NAMES = ["Eichel ♦", "Rosen ♥", "Schilten ♠", "Schellen ♣", "Obenabe", "Undeufe"];
const MULT = [1, 1, 2, 2, 3, 3];
const SEAT_NAMES = ["Du", "Links", "Partner", "Rechts"];
const ACT_TRUMP = 36, ACT_PUSH = 42;

const nextSeat = (s) => (s + 3) % 4;
const teamOf = (s) => s & 1;

const $ = (id) => document.getElementById(id);

/* ------------------------------------------------------------------ *
 * Worker plumbing
 * ------------------------------------------------------------------ */
const worker = new Worker("../worker.js");
let nextId = 1;
const pending = new Map();

worker.onmessage = (e) => {
  const d = e.data;
  if (d.type === "progress") {
    setStatus(d.state === "start"
      ? `lädt ${d.what} …`
      : `${d.what} geladen (${(d.bytes / 1e6).toFixed(1)} MB)`);
    return;
  }
  const p = pending.get(d.id);
  if (!p) return;
  pending.delete(d.id);
  d.ok ? p.resolve(d.result) : p.reject(new Error(d.error));
};

worker.onerror = (e) => showError(`Worker-Fehler: ${e.message || e}`);

function call(type, args) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    worker.postMessage({ id, type, args });
  });
}

/* ------------------------------------------------------------------ *
 * Rendering helpers
 * ------------------------------------------------------------------ */
function cardEl(card, { small = false } = {}) {
  const suit = SUITS[Math.floor(card / 9)];
  const el = document.createElement("div");
  el.className = "card" + (suit.red ? " red" : "") + (small ? " small" : "");
  el.innerHTML = `<span class="rank">${RANKS[card % 9]}</span><span class="suit">${suit.glyph}</span>`;
  el.title = `${suit.name} ${RANKS[card % 9]}`;
  return el;
}

const cardName = (c) => `${SUITS[Math.floor(c / 9)].name} ${RANKS[c % 9]}`;

function setStatus(text) { $("status").textContent = text; }
function showError(text) { $("error").textContent = text; }

function log(text, cls) {
  const d = document.createElement("div");
  if (cls) d.className = cls;
  d.textContent = text;
  const box = $("log");
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ------------------------------------------------------------------ *
 * Game state (only what the page is allowed to know)
 * ------------------------------------------------------------------ */
const G = {
  spec: "pimc",
  mode: "solo",
  rules: 0,
  samples: 64,
  mine: [0],
  state: null,
  busy: false,
  losses: [],
  seedCounter: 1,
  lastTrick: null,      // the trick just finished, kept on the table until the next card
  pending: null,        // card the human clicked, shown before the worker answers
};

/* Every state change goes through here so a completed trick can be remembered:
   once the fourth card falls the engine moves trick_first to the winner, so the
   leader has to be captured from the state before the move. */
function setState(next) {
  const prev = G.state;
  if (prev && next.nPlayed > prev.nPlayed && next.nPlayed % 4 === 0 && next.nPlayed > 0) {
    G.lastTrick = {
      cards: next.history.slice(next.nPlayed - 4, next.nPlayed),
      leader: prev.trickFirst,
      winner: next.trickFirst,
    };
  } else if (prev && next.nPlayed % 4 === 1) {
    G.lastTrick = null;               // a new trick has started
  }
  G.state = next;
}

const seed = () => (Date.now() + G.seedCounter++ * 7919) >>> 0;

/* ------------------------------------------------------------------ *
 * Drawing the table
 * ------------------------------------------------------------------ */
function render() {
  const s = G.state;
  if (!s) return;

  // seats
  for (const el of document.querySelectorAll(".seat")) {
    const seat = Number(el.dataset.seat);
    const who = el.querySelector(".who");
    const meta = el.querySelector(".meta");
    const mineSeat = G.mine.includes(seat);
    who.innerHTML = SEAT_NAMES[seat] +
      (mineSeat ? '<span class="badge">du</span>'
                : `<span class="badge">${G.spec.split(":")[0]}</span>`);
    const bits = [];
    if (seat === s.dealer) bits.push("Geber");
    if (seat === s.declarer) bits.push("hat Trumpf angesagt");
    meta.textContent = bits.join(" · ");
    el.classList.toggle("turn", seat === s.toMove);

    const backs = el.querySelector(".backs");
    backs.innerHTML = "";
    if (!mineSeat) {
      for (let i = 0; i < s.counts[seat]; i++) {
        const b = document.createElement("div");
        b.className = "back";
        backs.appendChild(b);
      }
    }
  }

  // Current trick, or the one that just finished.
  const trick = $("trick");
  trick.innerHTML = "";
  const inTrick = s.nPlayed % 4;
  const showLast = inTrick === 0 && G.lastTrick;
  const cards = showLast ? G.lastTrick.cards
                         : s.history.slice(s.nPlayed - inTrick, s.nPlayed);
  let seat = showLast ? G.lastTrick.leader : s.trickFirst;
  for (const card of cards) {
    const holder = document.createElement("div");
    holder.style.textAlign = "center";
    const lbl = document.createElement("div");
    lbl.style.cssText = "font-size:0.7rem;opacity:0.8;margin-bottom:2px";
    lbl.textContent = SEAT_NAMES[seat] + (showLast && seat === G.lastTrick.winner ? " \u2605" : "");
    holder.appendChild(lbl);
    const c = cardEl(card);
    if (showLast && seat !== G.lastTrick.winner) c.style.opacity = "0.55";
    holder.appendChild(c);
    trick.appendChild(holder);
    seat = nextSeat(seat);
  }
  if (G.pending && !showLast) {
    const holder = document.createElement("div");
    holder.style.textAlign = "center";
    const lbl = document.createElement("div");
    lbl.style.cssText = "font-size:0.7rem;opacity:0.8;margin-bottom:2px";
    lbl.textContent = SEAT_NAMES[G.pending.seat];
    holder.appendChild(lbl);
    holder.appendChild(cardEl(G.pending.card));
    trick.appendChild(holder);
  }

  // header note
  const note = $("tricknote");
  if (s.phase === "trump") {
    note.textContent = s.pushed ? "Trumpf wurde geschoben." : "Trumpf ansagen.";
  } else {
    const m = G.rules === 0 ? ` ×${MULT[s.trump]}` : "";
    note.textContent = `Trumpf: ${TRUMP_NAMES[s.trump]}${m}  ·  ` +
      `Stich ${Math.floor(s.nPlayed / 4) + 1}/9  ·  ` +
      `Punkte ${s.points[0]} : ${s.points[1]}`;
  }

  renderHand();
  renderTrumpChoice();
}

function renderHand() {
  const s = G.state;
  const hand = $("hand");
  const label = $("handlabel");
  hand.innerHTML = "";

  // Which of my seats is on move (in team mode the partner's hand shows too).
  const seatToShow = G.mine.includes(s.toMove) ? s.toMove : G.mine[0];
  const cards = (s.myHands[seatToShow] || [])
    .filter((c) => !(G.pending && G.pending.card === c))
    .slice().sort((a, b) => a - b);
  const myTurn = s.isMine && s.phase === "play";
  const legal = new Set(myTurn ? s.legal : []);

  label.textContent = G.mine.length > 1
    ? `Hand von ${SEAT_NAMES[seatToShow]}${myTurn ? " — du bist am Zug" : ""}`
    : (myTurn ? "Deine Karten — du bist am Zug" : "Deine Karten");

  for (const c of cards) {
    const el = cardEl(c);
    if (myTurn) {
      if (legal.has(c)) {
        el.classList.add("playable");
        el.onclick = () => humanPlays(c);
      } else {
        el.classList.add("dim");
        el.title += " — nicht erlaubt";
      }
    }
    el.dataset.card = String(c);
    hand.appendChild(el);
  }
}

function renderTrumpChoice() {
  const s = G.state;
  const box = $("trumpchoice");
  box.innerHTML = "";
  if (!(s.phase === "trump" && s.isMine)) return;

  for (const action of s.legal) {
    const b = document.createElement("button");
    if (action === ACT_PUSH) {
      b.textContent = "Schieben";
    } else {
      const m = action - ACT_TRUMP;
      b.innerHTML = `${TRUMP_NAMES[m]}` +
        (G.rules === 0 ? ` <span class="mult">×${MULT[m]}</span>` : "");
    }
    b.onclick = () => humanTrump(action);
    box.appendChild(b);
  }
}

/* ------------------------------------------------------------------ *
 * The coach
 * ------------------------------------------------------------------ */
function verdictFor(loss, noise) {
  // Same thresholds the offline review uses: a decision only counts against you
  // when the loss clears twice its own sampling noise.
  if (loss < 1 || loss <= 2 * noise) return { cls: "good", text: "✓ gut" };
  if (loss < 4)  return { cls: "warn", text: "?! Ungenauigkeit" };
  if (loss < 10) return { cls: "warn", text: "? Fehler" };
  return { cls: "bad", text: "?? Patzer" };
}

async function coachCard(chosen) {
  if (!G.samples) return;
  const panel = $("coach"), body = $("coachbody");
  panel.hidden = false;
  body.innerHTML = '<div class="thinking">rechnet …</div>';

  let options;
  try {
    options = await call("adviseCard", { samples: G.samples, seed: seed() });
  } catch (e) { body.innerHTML = ""; return; }
  if (!options || options.length < 2) {
    body.innerHTML = '<div class="thinking">nur eine erlaubte Karte — nichts zu entscheiden.</div>';
    return;
  }

  const byCard = new Map(options.map((o) => [o.card, o]));
  const best = options.reduce((a, b) => (b.value > a.value ? b : a));
  const mineOpt = byCard.get(chosen);
  if (!mineOpt) { body.innerHTML = ""; return; }

  // Values are point differences over the whole remaining play, so halving them
  // gives the loss for your side, the same convention the offline coach uses.
  const loss = Math.max(0, (best.value - mineOpt.value) / 2);
  const noise = mineOpt.se / 2;
  G.losses.push(loss);
  const v = verdictFor(loss, noise);

  const rows = options
    .slice()
    .sort((a, b) => b.value - a.value)
    .map((o) => {
      const d = (best.value - o.value) / 2;
      const mark = o.card === chosen ? " ← gespielt" : "";
      return `<tr><td>${cardName(o.card)}${mark}</td>` +
             `<td class="num">${o.card === best.card ? "beste" : "−" + d.toFixed(1)}</td>` +
             `<td class="num">±${(o.se / 2).toFixed(1)}</td></tr>`;
    }).join("");

  body.innerHTML =
    `<div><span class="verdict ${v.cls}">${v.text}</span>` +
    (loss >= 1 && loss > 2 * noise
      ? ` — ${cardName(best.card)} war ~${loss.toFixed(1)} ±${noise.toFixed(1)} Punkte besser.`
      : (loss >= 1 ? ` — ${cardName(best.card)} war knapp besser, aber im Rauschen.` : "")) +
    `</div><table>${rows}</table>`;

  // highlight the best card in the hand, if it is still there
  const el = $("hand").querySelector(`[data-card="${best.card}"]`);
  if (el) el.classList.add("best");
}

async function coachTrump(chosen) {
  if (!G.samples) return;
  const panel = $("coach"), body = $("coachbody");
  panel.hidden = false;
  body.innerHTML = '<div class="thinking">rechnet …</div>';

  let res;
  try {
    res = await call("adviseTrump", { samples: Math.max(16, G.samples >> 2), seed: seed() });
  } catch (e) { body.innerHTML = ""; return; }
  if (!res) { body.innerHTML = ""; return; }

  const { values, human } = res;
  const allowed = G.state.pushedAtCall ? [0, 1, 2, 3, 4, 5] : [0, 1, 2, 3, 4, 5, 6];
  const names = [...TRUMP_NAMES, "Schieben"];
  const idx = chosen === ACT_PUSH ? 6 : chosen - ACT_TRUMP;
  const best = allowed.reduce((a, b) => (values[b] > values[a] ? b : a), allowed[0]);
  const loss = Math.max(0, (values[best] - values[idx]) / 2);
  G.losses.push(loss);
  const v = loss < 1 ? { cls: "good", text: "✓ beste Wahl" }
                     : verdictFor(loss, 0);

  const rows = allowed
    .slice()
    .sort((a, b) => values[b] - values[a])
    .map((m) => {
      const d = (values[best] - values[m]) / 2;
      const mark = m === idx ? " ← gewählt" : "";
      const h = human ? `<td class="num">${(human[m] * 100).toFixed(0)} %</td>` : "";
      return `<tr><td>${names[m]}${mark}</td>` +
             `<td class="num">${m === best ? "beste" : "−" + d.toFixed(1)}</td>${h}</tr>`;
    }).join("");

  body.innerHTML =
    `<div><span class="verdict ${v.cls}">${v.text}</span>` +
    (loss >= 1 ? ` — ${names[best]} war ~${loss.toFixed(0)} Punkte besser.` : "") +
    `</div><table>${rows}</table>` +
    (human ? '<div class="thinking" style="margin-top:.4rem">Rechte Spalte: wie oft Swisslos-Spieler so ansagen.</div>' : "");
}

/* ------------------------------------------------------------------ *
 * Turn loop
 * ------------------------------------------------------------------ */
async function humanTrump(action) {
  if (G.busy) return;
  G.busy = true;
  try {
    G.state.pushedAtCall = G.state.pushed;
    const label = action === ACT_PUSH ? "schiebt" : TRUMP_NAMES[action - ACT_TRUMP];
    const who = SEAT_NAMES[G.state.toMove];
    await coachTrump(action);
    setState(await call("play", { action }));
    log(`${who}: ${label}`);
    render();
    await advance();
  } catch (e) { showError(e.message); }
  finally { G.busy = false; }
}

async function humanPlays(card) {
  if (G.busy) return;
  G.busy = true;
  try {
    const who = SEAT_NAMES[G.state.toMove];
    // Put the card on the table straight away. The coach may take up to a second
    // on the first trick, and waiting for it before showing the move feels broken.
    G.pending = { card, seat: G.state.toMove };
    render();
    // Both requests are queued now, in this order, so the advice is still
    // computed on the position before the move.
    const advice = coachCard(card);
    const next = await call("play", { action: card });
    G.pending = null;
    setState(next);
    log(`${who} spielt ${cardName(card)}`);
    render();
    await advice;
    await advance();
  } catch (e) { G.pending = null; showError(e.message); }
  finally { G.busy = false; }
}

/* Runs engine seats (and forced single-card moves) until it is the human's turn
   again or the round is over. */
async function advance() {
  for (let guard = 0; guard < 80; guard++) {
    const s = G.state;
    if (s.done) return finish();

    // Let a freshly completed trick sit on the table before play moves on.
    if (G.lastTrick && !G.lastTrick.shown) {
      G.lastTrick.shown = true;
      render();
      await sleep(900);
    }

    if (s.isMine) {
      // A single legal card is not a decision; play it and say so.
      if (s.phase === "play" && s.legal.length === 1) {
        const c = s.legal[0];
        log(`${SEAT_NAMES[s.toMove]} spielt ${cardName(c)} (einzige erlaubte Karte)`, "sys");
        setState(await call("play", { action: c }));
        render();
        await sleep(280);
        continue;
      }
      render();
      return;                      // wait for a click
    }

    // engine seat
    setStatus(`${SEAT_NAMES[s.toMove]} überlegt …`);
    const before = performance.now();
    const res = await call("bot", { spec: G.spec });
    const took = performance.now() - before;
    const label = s.phase === "trump"
      ? (res.action === ACT_PUSH ? "schiebt" : TRUMP_NAMES[res.action - ACT_TRUMP])
      : `spielt ${cardName(res.action)}`;
    log(`${SEAT_NAMES[res.seat]} ${label}`);
    setStatus(`${SEAT_NAMES[res.seat]}: ${Math.round(took)} ms`);
    setState(res);
    render();
    const justFinishedTrick = G.state.nPlayed % 4 === 0 && G.state.nPlayed > 0 && !G.state.done;
    await sleep(justFinishedTrick ? 1100 : Math.max(0, 420 - took));
  }
}

function finish() {
  const s = G.state;
  render();
  const myTeam = teamOf(G.mine[0]);
  const mineScore = s.finalScore[myTeam];
  const theirs = s.finalScore[1 - myTeam];
  const box = $("result");
  const totalLoss = G.losses.reduce((a, b) => a + b, 0);
  box.innerHTML =
    `<div class="result"><h3>${mineScore > theirs ? "Gewonnen \u{1F389}" : mineScore === theirs ? "Unentschieden" : "Verloren"}</h3>` +
    `<div class="score">${mineScore} : ${theirs}</div>` +
    (G.samples && G.losses.length
      ? `<div style="margin-top:.5rem;font-size:.88rem">Coach: <b>${totalLoss.toFixed(1)}</b> Punkte erwarteter Verlust über ${G.losses.length} Entscheidungen.</div>`
      : "") +
    `</div>`;
  setStatus("Runde fertig.");
  $("trumpchoice").innerHTML = "";
}

/* ------------------------------------------------------------------ *
 * Setup
 * ------------------------------------------------------------------ */
const AGENT_HINTS = {
  "pimc:roll=strong": "Sucht über gesampelten Verteilungen und spielt sie mit dem destillierten Netz aus. Stärkster Gegner, ~100 ms pro Zug.",
  "pimc": "Sucht über gesampelten Verteilungen, Rollouts vom Imitationsnetz. ~100 ms pro Zug.",
  "net:strong": "Reines Netz, aus der Suche destilliert. Antwortet sofort.",
  "net": "Reines Imitationsnetz — spielt wie der Durchschnitt von 65.6 M Swisslos-Zügen. Sofort.",
  "heuristic": "Handgeschriebene Regeln, ohne Netz. Schwächster Gegner, aber sofort.",
};

const MODE_HINTS = {
  solo: "Klassisch: du sitzt auf einem Sitz, die Engine spielt beide Gegner — und deinen Partner.",
  team: "Du entscheidest für dein ganzes Team, siehst also auch die Hand des Partners. Gegen zwei Engine-Gegner.",
};

function syncHints() {
  $("agent-hint").textContent = AGENT_HINTS[$("agent").value] || "";
  $("mode-hint").textContent = MODE_HINTS[$("mode").value] || "";
}

$("agent").onchange = syncHints;
$("mode").onchange = syncHints;
syncHints();

$("start").onclick = async () => {
  showError("");
  G.spec = $("agent").value;
  G.mode = $("mode").value;
  G.rules = Number($("rules").value);
  G.samples = Number($("samples").value);
  G.mine = G.mode === "team" ? [0, 2] : [0];
  G.losses = [];

  $("start").disabled = true;
  $("loading").hidden = false;
  $("log").innerHTML = "";
  $("result").innerHTML = "";
  $("coach").hidden = true;
  setStatus("Engine startet …");

  try {
    G.lastTrick = null;
    setState(await call("newGame", { seed: seed(), rules: G.rules, seats: G.mine }));
    $("game").hidden = false;
    $("loading").hidden = true;
    setStatus("");
    log(`Neue Runde — Geber: ${SEAT_NAMES[G.state.dealer]}, Gegner: ${G.spec}`, "sys");
    render();
    await advance();
  } catch (e) {
    $("loading").hidden = true;
    showError(`Engine konnte nicht starten: ${e.message}`);
  } finally {
    $("start").disabled = false;
    $("start").textContent = "Neue Runde";
  }
};

/* Exposed for debugging and for the browser test harness; it only ever holds
   the seats the human plays, never the engine hands. */
window.G = G;

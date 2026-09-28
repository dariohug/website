/* Swiss-German Jass card faces, drawn as inline SVG.
 *
 * The four suits are Eichel (acorns), Rosen (roses), Schilten (shields) and
 * Schellen (bells), in the colours a Deutschschweizer deck actually uses:
 * brown acorns, red roses, blue shields, gold bells. The ranks are the Swiss
 * ones too — As, König, Ober, Under, Banner, then 9 down to 6.
 *
 * The shapes are drawn here rather than taken from an existing deck: the card
 * art you can find online is either still in copyright or ShareAlike-licensed,
 * and neither belongs on a personal site by accident.
 *
 * Engine encoding: card = suit * 9 + rank, suits D/H/S/C in the order
 * Eichel, Rosen, Schilten, Schellen; ranks A K O U 10 9 8 7 6.
 */
"use strict";

const SUIT_INFO = [
  { key: "eichel",   name: "Eichel",   ink: "#6b4a23", accent: "#4f7233", tint: "#f6efe2" },
  { key: "rosen",    name: "Rosen",    ink: "#b3122b", accent: "#2f7d38", tint: "#fbecec" },
  { key: "schilten", name: "Schilten", ink: "#1d4e89", accent: "#e8b53a", tint: "#eaf0f8" },
  { key: "schellen", name: "Schellen", ink: "#c98209", accent: "#8a4b12", tint: "#fdf3df" },
];

const GOLD = "#d9b23c", GOLD_DARK = "#8a6a14";

const RANK_LABEL = ["A", "K", "O", "U", "B", "9", "8", "7", "6"];
const RANK_NAME  = ["As", "König", "Ober", "Under", "Banner", "9", "8", "7", "6"];

/* ------------------------------------------------------------------ *
 * The four suit symbols, each drawn in a 100x100 box.
 * ------------------------------------------------------------------ */
function suitSvg(suit) {
  const s = SUIT_INFO[suit];
  switch (suit) {
    case 0: // Eichel: an acorn, cap on top, little stalk
      return `
        <path d="M50 8c-3 0-5 2-5 5 0 2 1 4 3 5h4c2-1 3-3 3-5 0-3-2-5-5-5z" fill="${s.accent}"/>
        <path d="M24 30c0-8 12-14 26-14s26 6 26 14c0 7-5 11-13 12H37c-8-1-13-5-13-12z" fill="${s.ink}"/>
        <path d="M27 26h46" stroke="${s.accent}" stroke-width="3" stroke-linecap="round" opacity=".55"/>
        <path d="M31 42c0 22 7 46 19 46s19-24 19-46z" fill="${s.ink}" opacity=".82"/>
        <path d="M39 50c-1 14 1 26 5 32" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".28" fill="none"/>`;
    case 1: // Rosen: a heraldic five-petal rose
      return `
        <g fill="${s.ink}">
          <circle cx="50" cy="24" r="17"/><circle cx="74" cy="42" r="17"/>
          <circle cx="65" cy="71" r="17"/><circle cx="35" cy="71" r="17"/>
          <circle cx="26" cy="42" r="17"/>
        </g>
        <circle cx="50" cy="50" r="13" fill="${s.accent}"/>
        <circle cx="50" cy="50" r="6" fill="#f4d64e"/>`;
    case 2: // Schilten: a shield
      return `
        <path d="M20 14h60v34c0 20-13 32-30 40-17-8-30-20-30-40z" fill="${s.ink}"/>
        <path d="M28 22h44v26c0 15-9 24-22 31-13-7-22-16-22-31z" fill="none" stroke="${s.accent}" stroke-width="4"/>`;
    case 3: // Schellen: a bell
      return `
        <path d="M50 10c-4 0-7 3-7 7 0 1 0 2 1 3-11 6-17 18-17 32 0 9-2 14-6 18h58c-4-4-6-9-6-18 0-14-6-26-17-32 1-1 1-2 1-3 0-4-3-7-7-7z" fill="${s.ink}"/>
        <path d="M38 30c-4 7-6 16-6 24" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".3" fill="none"/>
        <circle cx="50" cy="80" r="8" fill="${s.accent}"/>`;
  }
  return "";
}

/* Pip positions for the numeral cards, in percent of the face. */
const PIPS = {
  4: [[50, 22], [50, 41], [50, 59], [50, 78]],                             // 9 shows 4+4+1 below
  6: [[32, 22], [68, 22], [32, 50], [68, 50], [32, 78], [68, 78]],
  7: [[32, 20], [68, 20], [32, 44], [68, 44], [50, 32], [32, 72], [68, 72]],
  8: [[32, 18], [68, 18], [32, 40], [68, 40], [32, 62], [68, 62], [32, 84], [68, 84]],
  9: [[32, 17], [68, 17], [32, 36], [68, 36], [50, 50], [32, 64], [68, 64], [32, 83], [68, 83]],
};

function pipLayout(rank) {
  if (rank === 5) return PIPS[9];      // 9
  if (rank === 6) return PIPS[8];      // 8
  if (rank === 7) return PIPS[7];      // 7
  if (rank === 8) return PIPS[6];      // 6
  return null;
}

/* The centre of a face: pips for numerals, a banner for the Banner, one big
   symbol for the As, and a simple figure panel for Under / Ober / König. */
function faceCentre(suit, rank) {
  const s = SUIT_INFO[suit];
  const sym = (x, y, size, extra = "") =>
    `<svg class="pip" viewBox="0 0 100 100" style="left:${x}%;top:${y}%;width:${size}%" ${extra}>${suitSvg(suit)}</svg>`;

  const pips = pipLayout(rank);
  if (pips) return pips.map(([x, y]) => sym(x, y, 26)).join("");

  if (rank === 0) return sym(50, 50, 82);                     // As: one big symbol

  if (rank === 4) {                                            // Banner
    return `<div class="banner">
        <svg viewBox="0 0 100 74" preserveAspectRatio="none" class="flag">
          <path d="M14 5h82v44c-14 8-27 1-41 8S28 60 14 52z" fill="#fffaf0"
                stroke="${s.ink}" stroke-width="5" stroke-linejoin="round"/>
          <path d="M11 2v70" stroke="${GOLD_DARK}" stroke-width="6" stroke-linecap="round"/>
        </svg>${sym(57, 40, 34)}</div>`;
  }

  // Under, Ober, König carry a rank motif above the suit, in heraldic gold — the
  // suit accent would otherwise put a green crown on the Eichel König.
  const crown = rank === 1                                     // König: a crown
    ? `<path d="M20 42l5-24 12 13 13-19 13 19 12-13 5 24z" fill="${GOLD}" stroke="${GOLD_DARK}" stroke-width="3" stroke-linejoin="round"/>`
    : rank === 2                                               // Ober: a plumed helm
      ? `<path d="M22 44c0-16 12-26 28-26s28 10 28 26z" fill="${GOLD}" stroke="${GOLD_DARK}" stroke-width="3"/><path d="M50 18v26" stroke="${GOLD_DARK}" stroke-width="3"/>`
      : `<path d="M26 44l24-24 24 24z" fill="${GOLD}" stroke="${GOLD_DARK}" stroke-width="3" stroke-linejoin="round"/>`;
  return `<div class="figure">
      <svg viewBox="0 0 100 60" class="crown">${crown}</svg>
      ${sym(50, 64, 52)}
    </div>`;
}

/* ------------------------------------------------------------------ *
 * Public API
 * ------------------------------------------------------------------ */
function cardFace(card) {
  const suit = Math.floor(card / 9), rank = card % 9;
  const s = SUIT_INFO[suit];
  const el = document.createElement("div");
  el.className = `card suit-${suit}`;
  el.style.setProperty("--ink", s.ink);
  el.style.setProperty("--accent", s.accent);
  el.style.setProperty("--tint", s.tint);
  el.innerHTML =
    `<span class="idx tl">${RANK_LABEL[rank]}</span>` +
    `<div class="face">${faceCentre(suit, rank)}</div>`;
  el.title = cardTitle(card);
  return el;
}

function cardTitle(card) {
  return `${SUIT_INFO[Math.floor(card / 9)].name} ${RANK_NAME[card % 9]}`;
}

function cardBack() {
  const el = document.createElement("div");
  el.className = "card back";
  el.innerHTML = `<div class="back-art"></div>`;
  return el;
}

window.JassCards = { cardFace, cardTitle, cardBack, SUIT_INFO, RANK_LABEL, RANK_NAME };

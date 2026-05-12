#!/usr/bin/env python3
"""
Generate a self-contained flashcard HTML artifact implementing
Prerequisite-Aware Spaced Repetition with TD Credit Assignment.

Algorithm
---------
  Each card has a mastery estimate V(s) ∈ [0,1] — the TD value function.

  On each recall attempt:
    1. Student rates recall quality (0=forgot, 1=hard, 2=good, 3=easy).
    2. TD error  δ = actual_score − V(card)
    3. Own mastery updated: V(card) += α * δ  (α = 0.15, the TD step size)
    4. Credit/blame propagated through the prerequisite graph:
         Fail (δ < 0): backward BFS — blame ancestors by δ * 0.5^hop
         Pass (δ > 0): forward BFS  — boost dependents by δ * 0.3^hop
    5. SM-2 scheduling updates the next-review interval.

  Card selection uses deliberate practice:
    - Due cards ordered by mastery ascending (weakest first)
    - Then frontier cards (unmastered, but all prereqs ≥ 0.6)
    - Then globally weakest card

  All state (mastery scores, intervals, due times) is stored in localStorage.
  No server required — open the HTML file directly in any browser.

Usage
-----
  uv run python scripts/flashcard_generator.py generate
  uv run python scripts/flashcard_generator.py generate --doc-id notes_credit_assignment
  uv run python scripts/flashcard_generator.py generate --module 1 2 3 --slug module_123
  uv run python scripts/flashcard_generator.py generate --type all --slug full_deck
"""

from __future__ import annotations

import argparse
import json
import sqlite3

import _bootstrap  # noqa: F401
from ontology_core.paths import ARTIFACTS_DIR, DB_PATH, WEB_DIR


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------

def fetch_cards(
    doc_ids: list[str] | None = None,
    modules: list[int] | None = None,
    node_type: str = "concept",
) -> tuple[list[dict], list[tuple[str, str]]]:
    """Return (cards, edges) filtered by the given scope.

    cards : [{id, label, description, module}]
    edges : [(source_id, target_id)]  — prerequisite graph
    """
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Build concept filter
    if node_type == "all":
        type_clause = ""
        type_params: list = []
    else:
        types = node_type.split(",") if "," in node_type else [node_type]
        type_clause = f"AND n.node_type IN ({','.join('?' * len(types))})"
        type_params = types

    if doc_ids:
        placeholders = ",".join("?" * len(doc_ids))
        cur.execute(f"""
            SELECT DISTINCT n.id, n.label, n.description,
                            COALESCE(MIN(d.course_order), 999) AS module_order
            FROM nodes n
            LEFT JOIN source_documents sd ON sd.node_id = n.id
            LEFT JOIN documents d         ON d.doc_id   = sd.doc_id
            WHERE sd.doc_id IN ({placeholders}) {type_clause}
            GROUP BY n.id
            ORDER BY module_order, n.label
        """, doc_ids + type_params)
    elif modules:
        placeholders = ",".join("?" * len(modules))
        cur.execute(f"""
            SELECT n.id, n.label, n.description,
                   COALESCE(MIN(d.course_order), 999) AS module_order
            FROM nodes n
            LEFT JOIN source_documents sd ON sd.node_id = n.id
            LEFT JOIN documents d         ON d.doc_id   = sd.doc_id
            WHERE 1=1 {type_clause}
            GROUP BY n.id
            HAVING module_order IN ({placeholders})
            ORDER BY module_order, n.label
        """, type_params + modules)
    else:
        cur.execute(f"""
            SELECT n.id, n.label, n.description,
                   COALESCE(MIN(d.course_order), 999) AS module_order
            FROM nodes n
            LEFT JOIN source_documents sd ON sd.node_id = n.id
            LEFT JOIN documents d         ON d.doc_id   = sd.doc_id
            WHERE 1=1 {type_clause}
            GROUP BY n.id
            ORDER BY module_order, n.label
        """, type_params)

    rows = cur.fetchall()
    cards = [
        {"id": r[0], "label": r[1], "description": r[2] or "", "module": r[3]}
        for r in rows
    ]
    card_ids = {c["id"] for c in cards}

    # Fetch edges where both endpoints are in our card set
    cur.execute("SELECT source_id, target_id FROM relations")
    edges = [
        (r[0], r[1]) for r in cur.fetchall()
        if r[0] in card_ids and r[1] in card_ids
    ]

    conn.close()
    return cards, edges


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
__THEME_CSS__

  body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 20px 80px;
  }

  .container { position: relative; z-index: 1; width: 100%; max-width: 720px; }

  /* ---- Header ---- */
  header { text-align: center; margin-bottom: 40px; }
  .eyebrow {
    font-size: 11px; font-weight: 300; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 10px;
  }
  h1 {
    font-family: var(--font-display);
    font-size: clamp(22px, 4vw, 32px);
    font-weight: 700; line-height: 1.2; margin-bottom: 14px;
  }
  .session-stats {
    display: flex; justify-content: center; gap: 24px;
    font-size: 13px; color: var(--text-muted);
  }
  .stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
  .stat-num {
    font-family: var(--font-display);
    font-size: 20px; color: var(--accent); line-height: 1;
  }
  .stat-label { font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; }

  /* ---- Mastery overview bar ---- */
  .mastery-overview {
    margin-bottom: 28px;
    display: flex; align-items: center; gap: 16px;
  }
  .mastery-ring-wrap { position: relative; flex-shrink: 0; }
  .mastery-ring-wrap svg { transform: rotate(-90deg); }
  .mastery-ring-wrap circle { fill: none; stroke-width: 6; stroke-linecap: round; }
  .ring-track { stroke: var(--border); }
  .ring-fill { stroke: var(--accent); transition: stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1); }
  .ring-center {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
  }
  .ring-pct { font-family: var(--font-display); font-size: 15px; color: var(--accent); line-height: 1; }
  .ring-sub { font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-muted); }

  .mastery-bars { flex: 1; }
  .mastery-bar-row {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 3px; font-size: 11px; color: var(--text-muted);
  }
  .mastery-bar-label { width: 64px; text-align: right; flex-shrink: 0; }
  .mastery-bar-track { flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }
  .mastery-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
  .mastery-bar-count { width: 28px; font-size: 10px; }

  /* ---- Card ---- */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 36px 40px;
    margin-bottom: 16px;
    animation: fadeUp 0.3s ease both;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .module-badge {
    display: inline-block;
    font-size: 10px; font-weight: 300; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--accent);
    background: var(--accent-dim);
    border: 1px solid rgba(201,149,74,0.25);
    border-radius: 20px; padding: 2px 10px;
    margin-bottom: 14px;
  }

  .card-label {
    font-family: var(--font-display);
    font-size: clamp(18px, 3vw, 26px);
    font-weight: 700; line-height: 1.25;
    color: var(--text); margin-bottom: 18px;
  }

  /* Mastery micro-bar */
  .micro-mastery { margin-bottom: 24px; }
  .micro-mastery-head {
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--text-muted);
    letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 5px;
  }
  .micro-track { height: 3px; background: var(--border); border-radius: 2px; overflow: hidden; }
  .micro-fill { height: 100%; border-radius: 2px; transition: width 0.4s ease; background: var(--accent); }

  .btn-reveal {
    width: 100%; padding: 14px;
    background: transparent;
    border: 1px solid var(--accent);
    border-radius: 8px;
    color: var(--accent);
    font-family: var(--font-body); font-size: 15px;
    letter-spacing: 0.04em; cursor: pointer;
    transition: background 0.18s, color 0.18s;
  }
  .btn-reveal:hover { background: var(--accent); color: var(--bg); }

  /* Back of card */
  .definition {
    font-size: 15px; line-height: 1.75;
    color: var(--text); margin-bottom: 28px;
    border-top: 1px solid var(--border); padding-top: 20px;
  }

  .rating-prompt {
    font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 12px; text-align: center;
  }
  .rating-btns { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }

  .btn-rate {
    padding: 12px 6px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface2);
    color: var(--text);
    font-family: var(--font-body); font-size: 13px;
    cursor: pointer; transition: border-color 0.15s, background 0.15s, transform 0.1s;
    text-align: center; line-height: 1.3;
  }
  .btn-rate:hover { transform: translateY(-2px); }
  .btn-rate.fail:hover  { border-color: var(--wrong);   background: var(--wrong-bg); }
  .btn-rate.hard:hover  { border-color: var(--warn);    background: var(--warn-bg); }
  .btn-rate.good:hover  { border-color: var(--accent);  background: var(--accent-dim); }
  .btn-rate.easy:hover  { border-color: var(--correct); background: var(--correct-bg); }

  .btn-rate .rate-label { font-size: 11px; color: var(--text-muted); display: block; margin-top: 3px; }

  /* Next interval hint */
  .interval-hints {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
    margin-top: 6px;
  }
  .interval-hint {
    text-align: center; font-size: 10px;
    color: var(--text-muted); letter-spacing: 0.06em;
  }

  /* ---- Credit propagation panel ---- */
  .credit-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 32px;
    margin-bottom: 16px;
    animation: fadeUp 0.3s ease both;
  }
  .credit-title {
    font-family: var(--font-display);
    font-size: 14px; font-weight: 600;
    margin-bottom: 14px;
    display: flex; align-items: center; gap: 10px;
  }
  .credit-title .delta-badge {
    font-family: var(--font-body);
    font-size: 11px; padding: 2px 8px;
    border-radius: 20px;
  }
  .credit-title.negative .delta-badge { background: var(--wrong-bg); color: #c46060; border: 1px solid rgba(139,64,64,0.3); }
  .credit-title.positive .delta-badge { background: var(--correct-bg); color: #6aaa7e; border: 1px solid rgba(74,124,89,0.3); }
  .credit-title.neutral  .delta-badge { background: var(--accent-dim); color: var(--accent); border: 1px solid rgba(201,149,74,0.2); }

  .credit-entries { display: flex; flex-direction: column; gap: 6px; }
  .credit-entry {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 12px; border-radius: 6px;
    font-size: 13px; animation: fadeUp 0.2s ease both;
  }
  .credit-entry.backward { background: var(--wrong-bg); }
  .credit-entry.forward  { background: var(--correct-bg); }
  .credit-arrow { font-size: 14px; flex-shrink: 0; }
  .credit-concept { flex: 1; color: var(--text); }
  .credit-delta {
    font-family: var(--font-display);
    font-size: 12px; font-weight: 600; flex-shrink: 0;
  }
  .credit-delta.neg { color: #c46060; }
  .credit-delta.pos { color: #6aaa7e; }
  .credit-hop { font-size: 10px; color: var(--text-muted); flex-shrink: 0; }
  .credit-none { font-size: 13px; color: var(--text-muted); font-style: italic; }

  .btn-next {
    width: 100%; padding: 13px;
    background: transparent;
    border: 1px solid var(--accent);
    border-radius: 8px; color: var(--accent);
    font-family: var(--font-body); font-size: 15px;
    letter-spacing: 0.04em; cursor: pointer; margin-top: 12px;
    transition: background 0.18s, color 0.18s;
  }
  .btn-next:hover { background: var(--accent); color: var(--bg); }

  /* ---- Bottom dashboard ---- */
  .dashboard {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 4px;
  }
  .dash-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
  }
  .dash-title {
    font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 14px;
  }

  .weakest-entry {
    display: flex; align-items: center; gap: 10px;
    padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 12px;
  }
  .weakest-entry:last-child { border-bottom: none; }
  .weakest-label { flex: 1; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .weakest-bar-wrap { width: 48px; height: 4px; background: var(--border); border-radius: 2px; flex-shrink: 0; }
  .weakest-bar-fill { height: 100%; border-radius: 2px; background: var(--accent); }
  .weakest-pct { width: 28px; text-align: right; color: var(--text-muted); font-size: 11px; flex-shrink: 0; }

  .due-entry {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 12px;
  }
  .due-entry:last-child { border-bottom: none; }
  .due-label { color: var(--text); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .due-tag {
    font-size: 10px; padding: 2px 7px; border-radius: 12px; flex-shrink: 0; margin-left: 8px;
    letter-spacing: 0.06em; text-transform: uppercase;
  }
  .due-tag.overdue  { background: var(--wrong-bg);   color: #c46060; }
  .due-tag.today    { background: var(--accent-dim);  color: var(--accent); }
  .due-tag.tomorrow { background: var(--surface2);    color: var(--text-muted); }

  .reset-btn {
    margin-top: 16px; width: 100%; padding: 9px;
    background: transparent; border: 1px solid var(--border);
    border-radius: 6px; color: var(--text-muted);
    font-family: var(--font-body); font-size: 12px;
    cursor: pointer; transition: border-color 0.15s, color 0.15s;
  }
  .reset-btn:hover { border-color: var(--wrong); color: #c46060; }

  .hidden { display: none !important; }

  @media (max-width: 520px) {
    .card { padding: 24px 20px; }
    .rating-btns { grid-template-columns: repeat(2, 1fr); }
    .dashboard { grid-template-columns: 1fr; }
    .mastery-overview { flex-direction: column; align-items: flex-start; }
  }
</style>
</head>
<body>
<div class="container">

  <header>
    <div class="eyebrow">FAB 2026 — Flashcards</div>
    <h1 id="deck-title">__TITLE__</h1>
    <div class="session-stats">
      <div class="stat">
        <span class="stat-num" id="stat-due">0</span>
        <span class="stat-label">due now</span>
      </div>
      <div class="stat">
        <span class="stat-num" id="stat-mastered">0</span>
        <span class="stat-label">mastered</span>
      </div>
      <div class="stat">
        <span class="stat-num" id="stat-session">0</span>
        <span class="stat-label">this session</span>
      </div>
      <div class="stat">
        <span class="stat-num" id="stat-total">__CARD_COUNT__</span>
        <span class="stat-label">total cards</span>
      </div>
    </div>
  </header>

  <!-- Mastery overview -->
  <div class="mastery-overview">
    <div class="mastery-ring-wrap">
      <svg viewBox="0 0 80 80" width="80" height="80">
        <circle class="ring-track" cx="40" cy="40" r="34"/>
        <circle class="ring-fill" id="ring-fill" cx="40" cy="40" r="34"/>
      </svg>
      <div class="ring-center">
        <span class="ring-pct" id="ring-pct">0%</span>
        <span class="ring-sub">done</span>
      </div>
    </div>
    <div class="mastery-bars" id="mastery-bars"></div>
  </div>

  <!-- Flashcard (front) -->
  <div class="card" id="card-front">
    <div class="module-badge" id="card-module">Module —</div>
    <div class="card-label" id="card-label">Loading…</div>
    <div class="micro-mastery">
      <div class="micro-mastery-head">
        <span>Mastery estimate</span>
        <span id="card-mastery-pct">—</span>
      </div>
      <div class="micro-track"><div class="micro-fill" id="card-mastery-fill" style="width:0%"></div></div>
    </div>
    <button class="btn-reveal" onclick="flipCard()">Reveal Definition →</button>
  </div>

  <!-- Flashcard (back) -->
  <div class="card hidden" id="card-back">
    <div class="module-badge" id="card-module-back">Module —</div>
    <div class="card-label" id="card-label-back"></div>
    <p class="definition" id="card-definition"></p>
    <div class="rating-prompt">How well did you recall this?</div>
    <div class="rating-btns">
      <button class="btn-rate fail" onclick="rate(0)">✗<span class="rate-label">Forgot</span></button>
      <button class="btn-rate hard" onclick="rate(1)">≈<span class="rate-label">Hard</span></button>
      <button class="btn-rate good" onclick="rate(2)">✓<span class="rate-label">Good</span></button>
      <button class="btn-rate easy" onclick="rate(3)">★<span class="rate-label">Easy</span></button>
    </div>
    <div class="interval-hints" id="interval-hints"></div>
  </div>

  <!-- Credit propagation panel -->
  <div class="card credit-panel hidden" id="credit-panel">
    <div class="credit-title" id="credit-title"></div>
    <div class="credit-entries" id="credit-entries"></div>
    <button class="btn-next" onclick="nextCard()">Next Card →</button>
  </div>

  <!-- Dashboard -->
  <div class="dashboard">
    <div class="dash-panel">
      <div class="dash-title">Weakest Concepts</div>
      <div id="weakest-list"></div>
    </div>
    <div class="dash-panel">
      <div class="dash-title">Coming Up</div>
      <div id="due-list"></div>
      <button class="reset-btn" onclick="confirmReset()">Reset all progress</button>
    </div>
  </div>

</div>

<script>
// ============================================================
// DATA (embedded by flashcard_generator.py)
// ============================================================
const CARDS = __CARDS_JSON__;
const ALL_EDGES = __EDGES_JSON__;

// Build adjacency: PREREQS[id] = [ids that point TO id]   (predecessors)
//                 DEPENDENTS[id] = [ids that id points TO] (successors)
const PREREQS    = {};
const DEPENDENTS = {};
CARDS.forEach(c => { PREREQS[c.id] = []; DEPENDENTS[c.id] = []; });
ALL_EDGES.forEach(([src, tgt]) => {
  if (PREREQS[tgt]    !== undefined) PREREQS[tgt].push(src);
  if (DEPENDENTS[src] !== undefined) DEPENDENTS[src].push(tgt);
});

const CARD_MAP = {};
CARDS.forEach(c => { CARD_MAP[c.id] = c; });

// ============================================================
// STATE  (persisted in localStorage)
// ============================================================
const STORAGE_KEY = 'fab2026_fc_v1___SLUG__';

function defaultCardState() {
  return { mastery: 0.5, ease: 2.5, interval: 1, dueTime: Date.now(), reviews: 0, streak: 0 };
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch(e) {}
  return null;
}

function initState() {
  const saved = loadState();
  const cards = {};
  CARDS.forEach(c => {
    cards[c.id] = (saved && saved.cards && saved.cards[c.id]) || defaultCardState();
  });
  return {
    cards,
    session: { reviewed: 0, correct: 0, startTime: Date.now() }
  };
}

function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch(e) {}
}

let state = initState();

// ============================================================
// ALGORITHMS
// ============================================================

// --- TD Credit Propagation ---
// α: TD step size (learning rate)
// backwardDecay: blame decay per hop when failing
// forwardDecay:  credit decay per hop when passing
// maxDepth: max BFS depth for propagation
const TD_ALPHA      = 0.15;
const BACKWARD_DECAY = 0.5;
const FORWARD_DECAY  = 0.3;
const MAX_DEPTH      = 3;
const MASTERY_THRESHOLD = 0.7; // above this = "mastered"

// Rating → score mapping: 0=forgot, 1=hard, 2=good, 3=easy
const RATING_SCORES = [0.0, 0.4, 0.7, 1.0];

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function propagateCredit(cardId, delta) {
  const log = [];

  if (delta < 0) {
    // FAIL: blame propagates backward through PREREQS (ancestors)
    const visited = new Set([cardId]);
    const queue = [[cardId, 1]];
    while (queue.length) {
      const [nodeId, depth] = queue.shift();
      if (depth > MAX_DEPTH) continue;
      for (const predId of (PREREQS[nodeId] || [])) {
        if (visited.has(predId) || !state.cards[predId]) continue;
        visited.add(predId);
        const blame = delta * Math.pow(BACKWARD_DECAY, depth);
        const prev = state.cards[predId].mastery;
        state.cards[predId].mastery = clamp(prev + TD_ALPHA * blame, 0, 1);
        log.push({ id: predId, label: CARD_MAP[predId].label, delta: blame, depth, dir: 'backward' });
        queue.push([predId, depth + 1]);
      }
    }
  } else if (delta > 0) {
    // PASS: credit propagates forward through DEPENDENTS (successors)
    const visited = new Set([cardId]);
    const queue = [[cardId, 1]];
    while (queue.length) {
      const [nodeId, depth] = queue.shift();
      if (depth > MAX_DEPTH) continue;
      for (const depId of (DEPENDENTS[nodeId] || [])) {
        if (visited.has(depId) || !state.cards[depId]) continue;
        visited.add(depId);
        const boost = delta * Math.pow(FORWARD_DECAY, depth);
        const prev = state.cards[depId].mastery;
        state.cards[depId].mastery = clamp(prev + TD_ALPHA * boost, 0, 1);
        log.push({ id: depId, label: CARD_MAP[depId].label, delta: boost, depth, dir: 'forward' });
        queue.push([depId, depth + 1]);
      }
    }
  }

  return log;
}

// --- SM-2 Scheduling ---
function nextIntervals(cardId) {
  const s = state.cards[cardId];
  return [
    1,                                                           // 0=forgot
    Math.max(1, Math.round(s.interval * 1.2)),                  // 1=hard
    Math.max(1, Math.round(s.interval * s.ease)),               // 2=good
    Math.max(1, Math.round(s.interval * s.ease * 1.3)),         // 3=easy
  ];
}

function updateSchedule(cardId, rating) {
  const s = state.cards[cardId];
  const actualScore = RATING_SCORES[rating];
  const delta = actualScore - s.mastery;

  // Update own mastery (TD update)
  s.mastery = clamp(s.mastery + TD_ALPHA * delta, 0, 1);

  // SM-2 interval update
  if (rating === 0) {       // forgot
    s.interval = 1;
    s.ease = Math.max(1.3, s.ease - 0.2);
    s.streak = 0;
  } else if (rating === 1) { // hard
    s.interval = Math.max(1, Math.round(s.interval * 1.2));
    s.ease = Math.max(1.3, s.ease - 0.15);
    s.streak = 0;
  } else if (rating === 2) { // good
    s.interval = Math.max(1, Math.round(s.interval * s.ease));
    s.streak++;
  } else {                   // easy
    s.interval = Math.max(1, Math.round(s.interval * s.ease * 1.3));
    s.ease = Math.min(3.0, s.ease + 0.1);
    s.streak++;
  }

  s.dueTime = Date.now() + s.interval * 24 * 60 * 60 * 1000;
  s.reviews++;

  // Propagate credit through prerequisite graph
  const propagationLog = propagateCredit(cardId, delta);

  // Update session stats
  state.session.reviewed++;
  if (rating >= 2) state.session.correct++;

  saveState();
  return { delta, actualScore, propagationLog };
}

// --- Card Selection (Deliberate Practice) ---
function isFrontier(cardId) {
  const prereqs = PREREQS[cardId] || [];
  if (!prereqs.length) return true;
  return prereqs.every(pid => state.cards[pid] && state.cards[pid].mastery >= MASTERY_THRESHOLD);
}

function selectNextCard() {
  const now = Date.now();

  // 1. Due cards: sorted by mastery ascending (weakest first)
  const due = CARDS.filter(c => state.cards[c.id].dueTime <= now)
                   .sort((a, b) => state.cards[a.id].mastery - state.cards[b.id].mastery);
  if (due.length) return due[0];

  // 2. Frontier cards (unlocked but not yet mastered)
  const frontier = CARDS.filter(c => !isMastered(c.id) && isFrontier(c.id))
                        .sort((a, b) => state.cards[a.id].mastery - state.cards[b.id].mastery);
  if (frontier.length) return frontier[0];

  // 3. Globally weakest card
  return CARDS.slice().sort((a, b) => state.cards[a.id].mastery - state.cards[b.id].mastery)[0];
}

function isMastered(cardId) { return state.cards[cardId].mastery >= MASTERY_THRESHOLD; }

// ============================================================
// UI RENDERING
// ============================================================
let currentCard = null;

function showFront(card) {
  currentCard = card;
  const s = state.cards[card.id];
  const pct = Math.round(s.mastery * 100);
  const col = masteryColor(s.mastery);

  document.getElementById('card-module').textContent = card.module < 900 ? `Module ${card.module}` : 'Misc';
  document.getElementById('card-label').textContent = card.label;
  document.getElementById('card-mastery-pct').textContent = pct + '%';
  const fill = document.getElementById('card-mastery-fill');
  fill.style.width = pct + '%';
  fill.style.background = col;

  // Interval hints on back
  const hints = nextIntervals(card.id);
  document.getElementById('interval-hints').innerHTML = hints.map((d, i) => {
    const labels = ['Forgot','Hard','Good','Easy'];
    return `<div class="interval-hint">${d}d</div>`;
  }).join('');

  show('card-front');
  hide('card-back');
  hide('credit-panel');
}

function flipCard() {
  if (!currentCard) return;
  const card = currentCard;
  const hints = nextIntervals(card.id);

  document.getElementById('card-module-back').textContent =
    document.getElementById('card-module').textContent;
  document.getElementById('card-label-back').textContent = card.label;
  document.getElementById('card-definition').textContent = card.description;
  document.getElementById('interval-hints').innerHTML = hints.map(d => `<div class="interval-hint">${d}d</div>`).join('');

  hide('card-front');
  show('card-back');
  hide('credit-panel');
}

function rate(r) {
  if (!currentCard) return;
  const { delta, actualScore, propagationLog } = updateSchedule(currentCard.id, r);
  renderCreditPanel(currentCard, r, delta, propagationLog);
  hide('card-back');
  show('credit-panel');
  refreshStats();
  refreshOverview();
  refreshDashboard();
}

function nextCard() {
  const next = selectNextCard();
  if (next) showFront(next);
}

function renderCreditPanel(card, rating, delta, log) {
  const titleEl = document.getElementById('credit-title');
  const entriesEl = document.getElementById('credit-entries');
  const ratingLabels = ['Forgot','Hard','Good','Easy'];
  const ratingIcons  = ['✗','≈','✓','★'];

  const own = Math.round(state.cards[card.id].mastery * 100);
  const deltaSign = delta >= 0 ? '+' : '';
  const cls = delta < 0 ? 'negative' : delta > 0 ? 'positive' : 'neutral';
  const icon = delta < 0 ? '← blame' : delta > 0 ? '→ credit' : '— no change';

  titleEl.className = `credit-title ${cls}`;
  titleEl.innerHTML = `
    ${ratingIcons[rating]} ${ratingLabels[rating]} — own mastery now ${own}%
    <span class="delta-badge">${icon} δ=${deltaSign}${(TD_ALPHA * delta).toFixed(3)}</span>
  `;

  if (!log.length) {
    entriesEl.innerHTML = `<div class="credit-none">No connected concepts affected (no edges in scope).</div>`;
    return;
  }

  // Sort by abs(delta) descending
  const sorted = log.slice().sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));
  entriesEl.innerHTML = sorted.map((e, i) => {
    const arrow = e.dir === 'backward' ? '←' : '→';
    const d = e.dir === 'backward' ? 'neg' : 'pos';
    const sign = e.delta >= 0 ? '+' : '';
    const adj = Math.round(state.cards[e.id].mastery * 100);
    return `<div class="credit-entry ${e.dir}" style="animation-delay:${i*0.05}s">
      <span class="credit-arrow">${arrow}</span>
      <span class="credit-concept">${e.label}</span>
      <span class="credit-delta ${d}">${sign}${(TD_ALPHA * e.delta).toFixed(3)}</span>
      <span class="credit-hop">${e.depth} hop${e.depth > 1 ? 's' : ''} · ${adj}%</span>
    </div>`;
  }).join('');
}

// ============================================================
// STATS & OVERVIEWS
// ============================================================
function masteryColor(v) {
  if (v >= 0.7) return '#4a7c59';      // mastered: green
  if (v >= 0.4) return '#c9954a';      // learning: amber
  return '#8b4040';                    // weak: red
}

function refreshStats() {
  const now = Date.now();
  const dueCount = CARDS.filter(c => state.cards[c.id].dueTime <= now).length;
  const masteredCount = CARDS.filter(c => isMastered(c.id)).length;
  document.getElementById('stat-due').textContent = dueCount;
  document.getElementById('stat-mastered').textContent = masteredCount;
  document.getElementById('stat-session').textContent = state.session.reviewed;
}

function refreshOverview() {
  const masteredCount = CARDS.filter(c => isMastered(c.id)).length;
  const pct = CARDS.length ? masteredCount / CARDS.length : 0;
  const C = 2 * Math.PI * 34;
  const ring = document.getElementById('ring-fill');
  ring.style.strokeDasharray = C;
  ring.style.strokeDashoffset = C * (1 - pct);
  document.getElementById('ring-pct').textContent = Math.round(pct * 100) + '%';

  // Histogram bars
  const buckets = [
    { label: '0–20%',  min: 0,   max: 0.2  },
    { label: '20–40%', min: 0.2, max: 0.4  },
    { label: '40–60%', min: 0.4, max: 0.6  },
    { label: '60–80%', min: 0.6, max: 0.8  },
    { label: '80–100%',min: 0.8, max: 1.01 },
  ];
  const colors = ['#8b4040','#7c6b3a','#c9954a','#5a8c6a','#4a7c59'];
  const maxCount = Math.max(...buckets.map(b =>
    CARDS.filter(c => state.cards[c.id].mastery >= b.min && state.cards[c.id].mastery < b.max).length
  ), 1);

  document.getElementById('mastery-bars').innerHTML = buckets.map((b, i) => {
    const count = CARDS.filter(c => state.cards[c.id].mastery >= b.min && state.cards[c.id].mastery < b.max).length;
    const w = Math.round(count / maxCount * 100);
    return `<div class="mastery-bar-row">
      <span class="mastery-bar-label">${b.label}</span>
      <div class="mastery-bar-track">
        <div class="mastery-bar-fill" style="width:${w}%; background:${colors[i]}"></div>
      </div>
      <span class="mastery-bar-count">${count}</span>
    </div>`;
  }).join('');
}

function refreshDashboard() {
  // Weakest concepts
  const weakest = CARDS.slice()
    .sort((a, b) => state.cards[a.id].mastery - state.cards[b.id].mastery)
    .slice(0, 8);
  document.getElementById('weakest-list').innerHTML = weakest.map(c => {
    const v = state.cards[c.id].mastery;
    const pct = Math.round(v * 100);
    return `<div class="weakest-entry">
      <span class="weakest-label" title="${c.label}">${c.label}</span>
      <div class="weakest-bar-wrap"><div class="weakest-bar-fill" style="width:${pct}%; background:${masteryColor(v)}"></div></div>
      <span class="weakest-pct">${pct}%</span>
    </div>`;
  }).join('');

  // Coming up
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;
  const upcoming = CARDS.slice()
    .sort((a, b) => state.cards[a.id].dueTime - state.cards[b.id].dueTime)
    .slice(0, 8);
  document.getElementById('due-list').innerHTML = upcoming.map(c => {
    const due = state.cards[c.id].dueTime;
    let tag, tagClass;
    if (due <= now) { tag = 'now'; tagClass = 'overdue'; }
    else if (due < now + dayMs) { tag = 'today'; tagClass = 'today'; }
    else {
      const days = Math.ceil((due - now) / dayMs);
      tag = `${days}d`; tagClass = 'tomorrow';
    }
    return `<div class="due-entry">
      <span class="due-label" title="${c.label}">${c.label}</span>
      <span class="due-tag ${tagClass}">${tag}</span>
    </div>`;
  }).join('');
}

// ============================================================
// HELPERS
// ============================================================
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

function confirmReset() {
  if (confirm('Reset all flashcard progress? This cannot be undone.')) {
    localStorage.removeItem(STORAGE_KEY);
    state = initState();
    saveState();
    refreshStats(); refreshOverview(); refreshDashboard();
    const next = selectNextCard();
    if (next) showFront(next);
  }
}

// ============================================================
// BOOT
// ============================================================
(function boot() {
  const C = 2 * Math.PI * 34;
  document.getElementById('ring-fill').style.strokeDasharray = C;
  document.getElementById('ring-fill').style.strokeDashoffset = C;

  refreshStats();
  refreshOverview();
  refreshDashboard();

  const first = selectNextCard();
  if (first) showFront(first);
})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def load_theme_css() -> str:
    return (WEB_DIR / "styles" / "theme.css").read_text(encoding="utf-8")


def cmd_generate(args: argparse.Namespace) -> None:
    doc_ids = args.doc_id or []
    modules = args.module or []

    cards, edges = fetch_cards(
        doc_ids=doc_ids if doc_ids else None,
        modules=modules if modules else None,
        node_type=args.type,
    )

    if not cards:
        print("No cards matched the given filters. Check --doc-id / --module / --type.")
        return

    # Build title
    if doc_ids:
        title = f"Flashcards — {', '.join(doc_ids)}"
    elif modules:
        title = f"Flashcards — Module{'s' if len(modules) > 1 else ''} {', '.join(str(m) for m in modules)}"
    else:
        title = "FAB 2026 — Full Deck Flashcards"

    slug = args.slug or (
        f"module_{'_'.join(str(m) for m in modules)}" if modules
        else f"doc_{'_'.join(doc_ids)}" if doc_ids
        else "full"
    )

    cards_json = json.dumps(cards, ensure_ascii=False)
    edges_json = json.dumps([[e[0], e[1]] for e in edges], ensure_ascii=False)

    html = (HTML_TEMPLATE
            .replace("__TITLE__", title)
            .replace("__THEME_CSS__", load_theme_css())
            .replace("__CARD_COUNT__", str(len(cards)))
            .replace("__SLUG__", slug)
            .replace("__CARDS_JSON__", cards_json)
            .replace("__EDGES_JSON__", edges_json))

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    out_path = ARTIFACTS_DIR / f"flashcards_{slug}.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"Generated: {out_path}")
    print(f"  Cards    : {len(cards)}")
    print(f"  Edges    : {len(edges)} prerequisite links in graph")
    print(f"  Scope    : {title}")
    print(f"\nOpen artifacts/flashcards_{slug}.html in any browser.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flashcard_generator",
        description="Generate prerequisite-aware spaced repetition flashcards for FAB 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="Generate flashcard HTML artifact")
    p.add_argument("--doc-id", metavar="DOC_ID", nargs="+",
                   help="Limit to concepts from these document IDs (e.g. notes_credit_assignment)")
    p.add_argument("--module", metavar="N", type=int, nargs="+",
                   help="Limit to concepts from these module numbers")
    p.add_argument("--type", choices=["concept", "person", "example", "all"], default="concept",
                   help="Node type filter (default: concept)")
    p.add_argument("--slug", metavar="SLUG",
                   help="Output filename slug (default: auto-derived from scope)")
    p.set_defaults(func=cmd_generate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

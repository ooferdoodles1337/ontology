# Subskill: Generate Quiz

Queries the ontology and course notes, generates multiple-choice questions, then writes
a self-contained HTML file the user can open in any browser.

---

## Step 1 — Parse Scope

From the user's request, determine:

| Parameter | Default | Examples |
|---|---|---|
| **Topic / module** | All nodes | "module 3", "search", "credit assignment" |
| **Question count** | 10 | any number 5–20 |
| **Output slug** | topic in snake_case | `search`, `module_3`, `credit_assignment` |

Infer from context rather than asking.

---

## Step 2 — Query the Ontology

Pull nodes and relations for the scope.

**Module-scoped:**
```bash
sqlite-utils query ontology.db "
  SELECT n.id, n.label, n.description
  FROM nodes n
  WHERE n.node_type = 'concept' AND n.module = <N>
  ORDER BY n.label
" --table

sqlite-utils query ontology.db "
  SELECT r.rel_type, r.source_id, r.target_id, r.note
  FROM relations r
  JOIN nodes ns ON ns.id = r.source_id
  JOIN nodes nt ON nt.id = r.target_id
  WHERE ns.module = <N> OR nt.module = <N>
" --table
```

**Keyword-scoped:**
```bash
sqlite-utils query ontology.db "
  SELECT id, label, description, module
  FROM nodes
  WHERE label LIKE '%keyword%' OR description LIKE '%keyword%'
" --table
```

**Broad (all):**
```bash
sqlite-utils query ontology.db "
  SELECT id, label, description, node_type, module
  FROM nodes
  WHERE node_type = 'concept'
  ORDER BY module, label
" --table
```

Also fetch relevant examples and people:
```bash
sqlite-utils query ontology.db "
  SELECT n.id, n.label, n.description, r.rel_type, r.note
  FROM relations r
  JOIN nodes n ON n.id = r.source_id
  WHERE n.node_type IN ('example', 'person')
" --table
```

---

## Step 3 — Query RAG

Run 2–3 targeted queries to surface course-note content:

```bash
uv run python scripts/rag.py query "<main topic>" --top-k 8
uv run python scripts/rag.py query "<contrasting or related concept>" --top-k 6
```

---

## Step 4 — Generate Questions

Using the DB results and RAG context, generate N multiple-choice questions.

### Quality rules

- Every question must be answerable from the gathered course material.
- Distractors (wrong options) must be plausible — related concepts, not obviously wrong.
- Mix question types:
  - **Definition** — "What does X mean in this course?"
  - **Relation** — "What is the relationship between X and Y?"
  - **Application** — "Which concept best explains the following situation…?"
  - **Attribution** — "Who introduced / is associated with…?"
  - **Contrast** — "How does X differ from Y?"
  - **Example** — "Which of the following is an example of X?"
- Explanations (shown after answering) must cite the relevant concept, relation, or note.
- Vary the correct-answer position — do not cluster correct answers at position A or B.

### Internal data structure (do not write to disk yet)

```js
const QUESTIONS = [
  {
    q: "Question text here?",
    opts: [
      "First option text",
      "Second option text",
      "Third option text",
      "Fourth option text"
    ],
    ans: 2,   // 0-indexed position of the correct option
    expl: "Brief explanation citing the source concept, relation, or note."
  },
  // ...
];
```

---

## Step 5 — Write the HTML File

Write a self-contained HTML file to `artifacts/quiz_<slug>.html` using the Write tool.
Never use shell redirection.

Substitute three placeholders in the template below:

| Placeholder | Replace with |
|---|---|
| `{{QUIZ_TITLE}}` | Descriptive title, e.g. "Search & Problem-Solving" |
| `{{QUESTION_COUNT}}` | Number of questions as a numeral |
| `{{QUESTIONS_JS}}` | The full `const QUESTIONS = [...];` array |

### HTML template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{QUIZ_TITLE}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #141210;
    --surface: #1e1b18;
    --surface2: #262320;
    --border: #3a3530;
    --text: #e2d9cc;
    --text-muted: #8a8078;
    --accent: #c9954a;
    --accent-dim: rgba(201,149,74,0.12);
    --correct: #4a7c59;
    --correct-bg: rgba(74,124,89,0.15);
    --wrong: #8b4040;
    --wrong-bg: rgba(139,64,64,0.15);
    --radius: 10px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 17px;
    line-height: 1.65;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48px 20px 80px;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    opacity: 0.4;
    z-index: 0;
  }

  .container {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 680px;
  }

  header { text-align: center; margin-bottom: 48px; }

  .eyebrow {
    font-size: 11px;
    font-weight: 300;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 12px;
  }

  h1 {
    font-family: 'Playfair Display', 'Times New Roman', serif;
    font-size: clamp(26px, 5vw, 38px);
    font-weight: 700;
    line-height: 1.2;
    color: var(--text);
    margin-bottom: 16px;
  }

  .meta { font-size: 14px; color: var(--text-muted); font-style: italic; }

  .progress-wrap { margin-bottom: 36px; }

  .progress-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .progress-track { height: 2px; background: var(--border); border-radius: 1px; overflow: hidden; }

  .progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 1px;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    width: 0%;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 36px 40px;
    margin-bottom: 20px;
    animation: fadeUp 0.35s ease both;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .q-number {
    font-size: 11px;
    font-weight: 300;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
  }

  .q-text { font-size: 18px; line-height: 1.6; color: var(--text); margin-bottom: 28px; }

  .options { display: flex; flex-direction: column; gap: 10px; }

  .opt {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 14px 18px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    transition: border-color 0.18s, background 0.18s, transform 0.1s;
    text-align: left;
    font-family: inherit;
    font-size: 15px;
    color: var(--text);
    line-height: 1.5;
    width: 100%;
  }

  .opt:hover:not(:disabled) { border-color: var(--accent); background: var(--accent-dim); transform: translateX(3px); }

  .opt-letter {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Playfair Display', serif;
    color: var(--text-muted);
    transition: background 0.18s, color 0.18s;
    margin-top: 1px;
  }

  .opt.correct { border-color: var(--correct); background: var(--correct-bg); }
  .opt.correct .opt-letter { background: var(--correct); color: #fff; }
  .opt.wrong { border-color: var(--wrong); background: var(--wrong-bg); }
  .opt.wrong .opt-letter { background: var(--wrong); color: #fff; }
  .opt.dim { opacity: 0.38; }

  .explanation {
    margin-top: 20px;
    padding: 16px 20px;
    background: var(--accent-dim);
    border-left: 3px solid var(--accent);
    border-radius: 0 6px 6px 0;
    font-size: 14px;
    font-style: italic;
    color: var(--text-muted);
    line-height: 1.6;
    display: none;
    animation: fadeUp 0.25s ease both;
  }

  .explanation.show { display: block; }

  .btn-next {
    width: 100%;
    margin-top: 20px;
    padding: 14px;
    background: transparent;
    border: 1px solid var(--accent);
    border-radius: 8px;
    color: var(--accent);
    font-family: 'Source Serif 4', serif;
    font-size: 15px;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: background 0.18s, color 0.18s;
    display: none;
  }

  .btn-next:hover { background: var(--accent); color: var(--bg); }
  .btn-next.show { display: block; }

  #score-screen { display: none; text-align: center; animation: fadeUp 0.4s ease both; }
  #score-screen.show { display: block; }
  #quiz-area.hidden { display: none; }

  .score-ring { width: 140px; height: 140px; margin: 0 auto 28px; position: relative; }
  .score-ring svg { transform: rotate(-90deg); }
  .score-ring circle { fill: none; stroke-width: 8; stroke-linecap: round; }
  .score-ring .track { stroke: var(--border); }
  .score-ring .fill { stroke: var(--accent); transition: stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1) 0.3s; }

  .score-num { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
  .score-big { font-family: 'Playfair Display', serif; font-size: 36px; font-weight: 700; color: var(--accent); line-height: 1; }
  .score-label { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-muted); margin-top: 4px; }

  .score-verdict { font-family: 'Playfair Display', serif; font-size: 24px; margin-bottom: 10px; }
  .score-sub { font-size: 15px; color: var(--text-muted); font-style: italic; margin-bottom: 36px; }

  .btn-restart {
    padding: 13px 32px;
    background: var(--accent);
    border: none;
    border-radius: 8px;
    color: var(--bg);
    font-family: 'Source Serif 4', serif;
    font-size: 15px;
    cursor: pointer;
    transition: opacity 0.18s;
  }

  .btn-restart:hover { opacity: 0.85; }

  @media (max-width: 520px) {
    .card { padding: 24px 20px; }
    .q-text { font-size: 16px; }
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="eyebrow">FAB 2026 — Study Quiz</div>
    <h1>{{QUIZ_TITLE}}</h1>
    <p class="meta">{{QUESTION_COUNT}} questions · shuffled each attempt</p>
  </header>

  <div id="quiz-area">
    <div class="progress-wrap">
      <div class="progress-label">
        <span id="prog-text">Question 1 of {{QUESTION_COUNT}}</span>
        <span id="prog-pct">0%</span>
      </div>
      <div class="progress-track"><div class="progress-fill" id="prog-bar"></div></div>
    </div>

    <div class="card" id="q-card">
      <div class="q-number" id="q-num">Question 1</div>
      <div class="q-text" id="q-text"></div>
      <div class="options" id="opts"></div>
      <div class="explanation" id="expl"></div>
    </div>

    <button class="btn-next" id="btn-next">Continue →</button>
  </div>

  <div id="score-screen">
    <div class="score-ring">
      <svg viewBox="0 0 120 120" width="140" height="140">
        <circle class="track" cx="60" cy="60" r="54"/>
        <circle class="fill" id="ring-fill" cx="60" cy="60" r="54"/>
      </svg>
      <div class="score-num">
        <div class="score-big" id="score-big">0</div>
        <div class="score-label">correct</div>
      </div>
    </div>
    <div class="score-verdict" id="score-verdict"></div>
    <div class="score-sub" id="score-sub"></div>
    <button class="btn-restart" onclick="restart()">Try Again</button>
  </div>
</div>

<script>
{{QUESTIONS_JS}}

const LETTERS = ['A','B','C','D'];
let current = 0, score = 0, answered = false;

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

const ORDER = shuffle(QUESTIONS.map((_, i) => i));

function render() {
  const q = QUESTIONS[ORDER[current]];
  const total = QUESTIONS.length;
  answered = false;

  document.getElementById('q-num').textContent = `Question ${current + 1}`;
  document.getElementById('q-text').textContent = q.q;
  document.getElementById('prog-text').textContent = `Question ${current + 1} of ${total}`;
  document.getElementById('prog-pct').textContent = `${Math.round(current / total * 100)}%`;
  document.getElementById('prog-bar').style.width = `${current / total * 100}%`;

  const expl = document.getElementById('expl');
  expl.textContent = q.expl;
  expl.classList.remove('show');

  const nextBtn = document.getElementById('btn-next');
  nextBtn.classList.remove('show');

  const optsEl = document.getElementById('opts');
  optsEl.innerHTML = '';
  q.opts.forEach((text, i) => {
    const btn = document.createElement('button');
    btn.className = 'opt';
    btn.innerHTML = `<span class="opt-letter">${LETTERS[i]}</span><span>${text}</span>`;
    btn.onclick = () => pick(i, q.ans);
    optsEl.appendChild(btn);
  });
}

function pick(chosen, correct) {
  if (answered) return;
  answered = true;
  if (chosen === correct) score++;

  document.querySelectorAll('.opt').forEach((el, i) => {
    el.disabled = true;
    if (i === correct)     el.classList.add('correct');
    else if (i === chosen) el.classList.add('wrong');
    else                   el.classList.add('dim');
  });

  document.getElementById('expl').classList.add('show');
  const nextBtn = document.getElementById('btn-next');
  nextBtn.textContent = current + 1 < QUESTIONS.length ? 'Continue →' : 'See Results';
  nextBtn.classList.add('show');
}

document.getElementById('btn-next').onclick = () => {
  current++;
  if (current < QUESTIONS.length) {
    const card = document.getElementById('q-card');
    card.style.animation = 'none';
    requestAnimationFrame(() => { card.style.animation = ''; render(); });
  } else {
    showScore();
  }
};

function showScore() {
  document.getElementById('quiz-area').classList.add('hidden');
  document.getElementById('score-screen').classList.add('show');

  const total = QUESTIONS.length;
  const pct = score / total;
  document.getElementById('score-big').textContent = `${score}/${total}`;

  const C = 2 * Math.PI * 54;
  const ring = document.getElementById('ring-fill');
  ring.style.strokeDasharray = C;
  ring.style.strokeDashoffset = C;
  setTimeout(() => { ring.style.strokeDashoffset = C * (1 - pct); }, 50);

  const [, verdict, sub] = [
    [0.9, "Outstanding",   "Your grasp of this material is exceptional."],
    [0.7, "Well done",     "A solid understanding with a few gaps to revisit."],
    [0.5, "Good effort",   "Review the explanations and try again."],
    [0,   "Keep studying", "Go back to the course notes and give this another go."],
  ].find(([t]) => pct >= t);

  document.getElementById('score-verdict').textContent = verdict;
  document.getElementById('score-sub').textContent = sub;
}

function restart() {
  current = 0; score = 0;
  shuffle(ORDER);
  document.getElementById('quiz-area').classList.remove('hidden');
  document.getElementById('score-screen').classList.remove('show');
  render();
}

render();
</script>
</body>
</html>
```

---

## Step 6 — Confirm

After writing the file, tell the user:
- The output path relative to project root (e.g. `artifacts/quiz_search.html`)
- How many questions were generated and what scope they cover
- One-line instruction: *"Open `artifacts/quiz_<slug>.html` in any browser."*

Do not paste the HTML into the chat.

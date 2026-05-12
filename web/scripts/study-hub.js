/* ═══════════════════════════════════════
   TAB SWITCHING
═══════════════════════════════════════ */
let kbInitialised    = false;
let notesInitialised = false;
let learnerInitialised = false;

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const panel = document.getElementById('tab-' + btn.dataset.tab);
    panel.classList.add('active');
    if (btn.dataset.tab === 'kb' && !kbInitialised) {
      kbInitialised = true;
      initKB();
    }
    if (btn.dataset.tab === 'notes' && !notesInitialised) {
      notesInitialised = true;
      initNotes();
    }
    if (btn.dataset.tab === 'learner' && !learnerInitialised) {
      learnerInitialised = true;
      initLearner();
    }
  });
});

/* ═══════════════════════════════════════
   MARKDOWN MODAL (Artifacts tab)
═══════════════════════════════════════ */
function renderMarkdown(text) {
  const lines = text.split('\n');
  let html = '', inList = null, inTable = false;

  function closeList() { if (inList) { html += `</${inList}>\n`; inList = null; } }
  function closeTable() { if (inTable) { html += '</tbody></table>\n'; inTable = false; } }

  function inline(s) {
    return s
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color:var(--accent)">$1</a>');
  }

  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trimEnd();
    if (/^#{1,6}\s/.test(line)) {
      closeList(); closeTable();
      const lv = line.match(/^(#+)/)[1].length;
      html += `<h${lv}>${inline(line.replace(/^#+\s+/, ''))}</h${lv}>\n`;
    } else if (/^(---+|\*\*\*+)$/.test(line.trim())) {
      closeList(); closeTable(); html += '<hr>\n';
    } else if (/^>\s?/.test(line)) {
      closeList(); closeTable();
      html += `<blockquote>${inline(line.replace(/^>\s?/, ''))}</blockquote>\n`;
    } else if (/^\|/.test(line)) {
      closeList();
      const cells = line.split('|').slice(1, -1).map(c => c.trim());
      if (cells.every(c => /^[-:]+$/.test(c))) { i++; continue; }
      if (!inTable) {
        html += '<table><thead><tr>';
        cells.forEach(c => { html += `<th>${inline(c)}</th>`; });
        html += '</tr></thead><tbody>\n'; inTable = true; i++; continue;
      }
      html += '<tr>'; cells.forEach(c => { html += `<td>${inline(c)}</td>`; }); html += '</tr>\n';
    } else if (/^[-*+]\s/.test(line)) {
      closeTable();
      if (inList !== 'ul') { closeList(); html += '<ul>\n'; inList = 'ul'; }
      const c = line.replace(/^[-*+]\s/, '');
      if (/^\[x\]/i.test(c)) html += `<li class="checked">${inline(c.replace(/^\[x\]\s?/i,''))}</li>\n`;
      else if (/^\[ \]/.test(c)) html += `<li>${inline(c.replace(/^\[ \]\s?/,''))}</li>\n`;
      else html += `<li>${inline(c)}</li>\n`;
    } else if (/^\d+\.\s/.test(line)) {
      closeTable();
      if (inList !== 'ol') { closeList(); html += '<ol>\n'; inList = 'ol'; }
      html += `<li>${inline(line.replace(/^\d+\.\s/, ''))}</li>\n`;
    } else {
      closeList(); closeTable();
      if (line.trim()) html += `<p>${inline(line)}</p>\n`;
    }
    i++;
  }
  closeList(); closeTable();
  return html;
}

const backdrop   = document.getElementById('modal-backdrop');
const modalTitle = document.getElementById('modal-title');
const modalEyebrow = document.getElementById('modal-eyebrow');
const modalContent = document.getElementById('modal-content');

function openMarkdownModal(key, title, eyebrow) {
  modalTitle.textContent = title;
  modalEyebrow.textContent = eyebrow;
  backdrop.classList.add('open');
  document.body.style.overflow = 'hidden';
  const el = document.getElementById('md-' + key);
  modalContent.innerHTML = el ? renderMarkdown(el.textContent)
    : '<p style="color:var(--text-muted);font-style:italic">Content not found.</p>';
}

function closeModal() {
  backdrop.classList.remove('open');
  document.body.style.overflow = '';
}

document.getElementById('modal-close').addEventListener('click', closeModal);
backdrop.addEventListener('click', e => { if (e.target === backdrop) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

document.querySelectorAll('.card[data-md]').forEach(card => {
  const key   = card.dataset.md;
  const title = card.querySelector('.card-title').textContent;
  const type  = key.includes('schedule') ? 'Schedule' : 'Report';
  card.addEventListener('click', () => openMarkdownModal(key, title, type));
  card.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openMarkdownModal(key, title, type); }
  });
});

/* ═══════════════════════════════════════
   KNOWLEDGE BASE BROWSER
═══════════════════════════════════════ */
let nodes = [], relations = [], schema = [];
let selectedId = null;
let editing = false;
let addingRel = false;
let showingNewNode = false;
let filterType = 'all';
let searchQuery = '';

function esc(s) {
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escA(s) {
  return String(s ?? '').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
}
function nodeType(n) { return n._type || (n.id.startsWith('ex_') ? 'example' : 'concept'); }
function nodeById(id) { return nodes.find(n => n.id === id); }
function nodeLabel(id) { const n = nodeById(id); return n ? n.label : id; }

function debounce(fn, ms) {
  let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

async function initKB() {
  document.getElementById('kb-retry-btn').textContent = 'Connecting…';
  try {
    [nodes, relations, schema] = await Promise.all([
      fetch('/api/nodes').then(r => { if (!r.ok) throw 0; return r.json(); }),
      fetch('/api/relations').then(r => r.json()),
      fetch('/api/schema').then(r => r.json()),
    ]);
    document.getElementById('kb-offline').style.display = 'none';
    const browser = document.getElementById('kb-browser');
    browser.style.display = 'flex';

    // wire up static controls
    document.getElementById('kb-search').addEventListener('input', debounce(e => {
      searchQuery = e.target.value;
      renderList();
    }, 120));

    document.querySelectorAll('.kb-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        filterType = chip.dataset.type;
        document.querySelectorAll('.kb-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        renderList();
      });
    });

    document.getElementById('kb-list').addEventListener('click', e => {
      const row = e.target.closest('.kb-row');
      if (row) selectNode(row.dataset.id);
    });

    renderList();
  } catch {
    document.getElementById('kb-offline').style.display = 'flex';
    document.getElementById('kb-browser').style.display = 'none';
    document.getElementById('kb-retry-btn').textContent = 'Retry connection';
  }
}

function filteredNodes() {
  return nodes.filter(n => {
    const t = nodeType(n);
    if (filterType !== 'all' && t !== filterType) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return n.id.includes(q) || (n.label||'').toLowerCase().includes(q) ||
             (n.description||'').toLowerCase().includes(q);
    }
    return true;
  });
}

function renderList() {
  const list = document.getElementById('kb-list');
  const count = document.getElementById('kb-count');
  const items = filteredNodes();
  count.textContent = `${items.length} of ${nodes.length} nodes`;
  list.innerHTML = items.map(n => `
    <div class="kb-row${n.id === selectedId ? ' selected' : ''}" data-id="${escA(n.id)}">
      <div class="kb-row-type ${nodeType(n)}">${nodeType(n)}</div>
      <div class="kb-row-label">${esc(n.label)}</div>
      <div class="kb-row-id">${esc(n.id)}</div>
    </div>
  `).join('');
}

function selectNode(id) {
  selectedId = id;
  editing = false;
  addingRel = false;
  showingNewNode = false;
  renderList();
  renderDetail();
  // scroll selected row into view
  const row = document.querySelector('.kb-row.selected');
  if (row) row.scrollIntoView({ block: 'nearest' });
}

function renderDetail() {
  const main = document.getElementById('kb-main');
  if (showingNewNode) { renderNewNodeForm(main); return; }
  if (!selectedId) {
    main.innerHTML = '<div class="kb-empty-state">Select a node to view details</div>';
    return;
  }
  const node = nodeById(selectedId);
  if (!node) { main.innerHTML = '<div class="kb-empty-state">Node not found</div>'; return; }
  if (editing) { renderEditForm(node, main); return; }
  renderNodeView(node, main);
}

function renderNodeView(node, container) {
  const type = nodeType(node);
  const out  = relations.filter(r => r.source === node.id);
  const inc  = relations.filter(r => r.target === node.id);
  const docs = (node.source_documents || []);

  const relCard = (r, isOut) => {
    const otherLabel = isOut ? esc(nodeLabel(r.target)) : esc(nodeLabel(r.source));
    const otherId    = isOut ? escA(r.target) : escA(r.source);
    const delArgs    = `'${escA(r.type)}','${escA(r.source)}','${escA(r.target)}'`;
    return `
      <div class="rel-card">
        <div class="rel-main">
          ${isOut ? `<span class="rel-type">${esc(r.type)}</span><span class="rel-arrow">→</span>` : ''}
          <span class="rel-node" onclick="selectNode('${otherId}')">${otherLabel}</span>
          ${!isOut ? `<span class="rel-arrow">→</span><span class="rel-type">${esc(r.type)}</span>` : ''}
          <button class="rel-del" onclick="deleteRelation(${delArgs})" title="Remove relation">×</button>
        </div>
        ${r.note ? `<div class="rel-note">${esc(r.note)}</div>` : ''}
      </div>`;
  };

  container.innerHTML = `
    <div class="detail-head">
      <div>
        <div class="detail-badge ${type}">${type}</div>
        <div class="detail-title">${esc(node.label)}</div>
        <div class="detail-id">${esc(node.id)}</div>
      </div>
      <div class="detail-actions">
        <button class="btn btn-ghost" onclick="startEdit()">Edit</button>
        <button class="btn btn-danger" onclick="deleteNode('${escA(node.id)}')">Delete</button>
      </div>
    </div>

    <div class="detail-body">
      <div>
        <div class="sect-label">Description</div>
        <div class="detail-desc">${esc(node.description || '')}</div>
      </div>

      ${docs.length ? `
      <div>
        <div class="sect-label">Source Documents</div>
        <div class="tags">${docs.map(d => `<span class="tag">${esc(d)}</span>`).join('')}</div>
      </div>` : ''}

      <div>
        <div class="sect-label-row">
          <span class="sect-label">Outgoing (${out.length})</span>
        </div>
        <div class="rel-list">
          ${out.length ? out.map(r => relCard(r, true)).join('') : '<div class="rel-empty">No outgoing relations</div>'}
        </div>
      </div>

      <div>
        <div class="sect-label-row">
          <span class="sect-label">Incoming (${inc.length})</span>
        </div>
        <div class="rel-list">
          ${inc.length ? inc.map(r => relCard(r, false)).join('') : '<div class="rel-empty">No incoming relations</div>'}
        </div>
      </div>

      <div id="add-rel-section">
        ${addingRel ? addRelFormHtml(node.id) : `<button class="btn-add-rel" onclick="toggleAddRel()">+ Add relation</button>`}
      </div>
    </div>`;

  if (addingRel) wireAddRelForm();
}

function renderEditForm(node, container) {
  const docs = (node.source_documents || []).join(', ');
  container.innerHTML = `
    <div class="detail-head">
      <div>
        <div class="detail-badge ${nodeType(node)}">${nodeType(node)}</div>
        <div class="detail-id">${esc(node.id)}</div>
      </div>
      <div class="detail-actions">
        <button class="btn btn-primary" onclick="saveEdit()">Save</button>
        <button class="btn btn-ghost" onclick="cancelEdit()">Cancel</button>
      </div>
    </div>
    <div class="detail-body">
      <div class="form-field">
        <label class="form-label">Label</label>
        <input id="edit-label" class="form-input" value="${escA(node.label)}">
      </div>
      <div class="form-field">
        <label class="form-label">Description</label>
        <textarea id="edit-desc" class="form-textarea" rows="6">${esc(node.description || '')}</textarea>
      </div>
      <div class="form-field">
        <label class="form-label">Source Documents <span style="color:var(--text-muted);font-weight:300;text-transform:none;letter-spacing:0">(comma-separated)</span></label>
        <input id="edit-docs" class="form-input" value="${escA(docs)}" placeholder="doc_id_1, doc_id_2">
      </div>
    </div>`;
}

function renderNewNodeForm(container) {
  container.innerHTML = `
    <div class="detail-head">
      <div>
        <div class="detail-badge node">new node</div>
        <div class="detail-title">Add Node</div>
      </div>
      <div class="detail-actions">
        <button class="btn btn-primary" onclick="submitNewNode()">Add</button>
        <button class="btn btn-ghost" onclick="cancelNewNode()">Cancel</button>
      </div>
    </div>
    <div class="detail-body">
      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">ID <span style="color:var(--text-muted);font-weight:300;text-transform:none;letter-spacing:0">(snake_case; prefix ex_ for examples)</span></label>
          <input id="new-id" class="form-input" placeholder="e.g. constraint_propagation">
        </div>
        <div class="form-field">
          <label class="form-label">Type</label>
          <select id="new-type" class="form-select">
            <option value="concept">Concept</option>
            <option value="person">Person / Institution</option>
            <option value="example">Example / Metaphor</option>
          </select>
        </div>
      </div>
      <div class="form-field">
        <label class="form-label">Label</label>
        <input id="new-label" class="form-input" placeholder="Human Readable Name">
      </div>
      <div class="form-field">
        <label class="form-label">Description</label>
        <textarea id="new-desc" class="form-textarea" rows="4" placeholder="One or two sentences."></textarea>
      </div>
      <div class="form-field">
        <label class="form-label">Source Documents <span style="color:var(--text-muted);font-weight:300;text-transform:none;letter-spacing:0">(comma-separated)</span></label>
        <input id="new-docs" class="form-input" placeholder="doc_id_1, doc_id_2">
      </div>
    </div>`;
}

function addRelFormHtml(currentId) {
  const schemaOpts = schema.map(s =>
    `<option value="${escA(s.name)}">${esc(s.name)}</option>`
  ).join('');
  const nodeOpts = nodes
    .filter(n => n.id !== currentId)
    .map(n => `<option value="${escA(n.id)}">${esc(n.label)} (${esc(n.id)})</option>`)
    .join('');
  return `
    <div class="add-rel-box">
      <div class="add-rel-title">Add Relation</div>
      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">Type</label>
          <select id="new-rel-type" class="form-select">
            <option value="">— select or type below —</option>
            ${schemaOpts}
          </select>
        </div>
        <div class="form-field">
          <label class="form-label">Custom type</label>
          <input id="new-rel-type-custom" class="form-input" placeholder="ENABLES">
        </div>
      </div>
      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">Direction</label>
          <select id="new-rel-dir" class="form-select">
            <option value="out">This node → other (outgoing)</option>
            <option value="in">Other → this node (incoming)</option>
          </select>
        </div>
        <div class="form-field">
          <label class="form-label">Other Node</label>
          <select id="new-rel-other" class="form-select">
            <option value="">— select —</option>
            ${nodeOpts}
          </select>
        </div>
      </div>
      <div class="form-field">
        <label class="form-label">Note</label>
        <textarea id="new-rel-note" class="form-textarea" rows="2" placeholder="Why does this relation hold?"></textarea>
      </div>
      <div class="form-field">
        <label class="form-label">Quote <span style="color:var(--text-muted);font-weight:300;text-transform:none;letter-spacing:0">(verbatim excerpt, or leave blank)</span></label>
        <textarea id="new-rel-quote" class="form-textarea" rows="2"></textarea>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" onclick="submitAddRel()">Add</button>
        <button class="btn btn-ghost" onclick="toggleAddRel()">Cancel</button>
      </div>
    </div>`;
}

function wireAddRelForm() { /* select elements set up in HTML; nothing extra needed */ }

/* ── Actions ── */

function startEdit() { editing = true; renderDetail(); }
function cancelEdit() { editing = false; renderDetail(); }

async function saveEdit() {
  const node = nodeById(selectedId);
  const label = document.getElementById('edit-label').value.trim();
  const desc  = document.getElementById('edit-desc').value.trim();
  const docs  = document.getElementById('edit-docs').value
    .split(',').map(s => s.trim()).filter(Boolean);
  const updated = { ...node, label, description: desc, source_documents: docs };
  await fetch(`/api/nodes/${selectedId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updated),
  });
  nodes = nodes.map(n => n.id === selectedId ? updated : n);
  editing = false;
  renderList();
  renderDetail();
}

async function deleteNode(id) {
  if (!confirm(`Delete node "${nodeLabel(id)}"?\n\nNote: its relations will not be removed automatically.`)) return;
  await fetch(`/api/nodes/${id}`, { method: 'DELETE' });
  nodes = nodes.filter(n => n.id !== id);
  selectedId = null;
  renderList();
  renderDetail();
}

function toggleAddRel() {
  addingRel = !addingRel;
  renderDetail();
}

async function submitAddRel() {
  const typeFromSelect = document.getElementById('new-rel-type').value;
  const typeCustom     = document.getElementById('new-rel-type-custom').value.trim().toUpperCase();
  const type  = typeCustom || typeFromSelect;
  const dir   = document.getElementById('new-rel-dir').value;
  const other = document.getElementById('new-rel-other').value.trim();
  const note  = document.getElementById('new-rel-note').value.trim();
  const quoteRaw = document.getElementById('new-rel-quote').value.trim();
  const quote = quoteRaw || null;

  if (!type)  { alert('Please select or enter a relation type.'); return; }
  if (!other) { alert('Please select the other node.'); return; }

  const rel = {
    type,
    source: dir === 'out' ? selectedId : other,
    target: dir === 'out' ? other : selectedId,
    note,
    quote,
  };
  await fetch('/api/relations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rel),
  });
  relations.push(rel);
  addingRel = false;
  renderDetail();
}

async function deleteRelation(type, source, target) {
  if (!confirm(`Remove relation ${type}: ${source} → ${target}?`)) return;
  await fetch('/api/relations', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, source, target }),
  });
  relations = relations.filter(r =>
    !(r.type === type && r.source === source && r.target === target)
  );
  renderDetail();
}

function showNewNodeForm() {
  selectedId = null;
  editing = false;
  addingRel = false;
  showingNewNode = true;
  renderList();
  renderDetail();
}

function cancelNewNode() {
  showingNewNode = false;
  renderDetail();
}

async function submitNewNode() {
  const id    = document.getElementById('new-id').value.trim();
  const label = document.getElementById('new-label').value.trim();
  const desc  = document.getElementById('new-desc').value.trim();
  const docs  = document.getElementById('new-docs').value
    .split(',').map(s => s.trim()).filter(Boolean);
  const type  = document.getElementById('new-type').value;

  if (!id)    { alert('ID is required.'); return; }
  if (!label) { alert('Label is required.'); return; }
  if (!/^[a-z][a-z0-9_]*$/.test(id)) {
    alert('ID must be snake_case lowercase (letters, digits, underscores).'); return;
  }

  const node = { id, label, description: desc, source_documents: docs, _type: type };
  const res = await fetch('/api/nodes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(node),
  });
  if (res.status === 409) { alert(`ID "${id}" already exists.`); return; }

  nodes.push(node);
  showingNewNode = false;
  selectedId = id;
  renderList();
  renderDetail();
}

/* ═══════════════════════════════════════
   LEARNER MODEL
═══════════════════════════════════════ */
let learnerProfile = {};
let learnerBeliefs = [];
let learnerRecommendations = [];
let learnerEvents = [];
let learnerNodes = [];

async function initLearner() {
  const retryBtn = document.getElementById('learner-retry-btn');
  retryBtn.textContent = 'Connecting…';
  try {
    [learnerProfile, learnerBeliefs, learnerRecommendations, learnerEvents, learnerNodes] = await Promise.all([
      fetch('/api/learner/profile').then(r => { if (!r.ok) throw 0; return r.json(); }),
      fetch('/api/learner/beliefs').then(r => r.json()),
      fetch('/api/learner/recommendations?limit=8').then(r => r.json()),
      fetch('/api/learner/events?limit=40').then(r => r.json()),
      fetch('/api/nodes').then(r => r.json()),
    ]);
    document.getElementById('learner-offline').style.display = 'none';
    document.getElementById('learner-app').style.display = 'flex';
    wireLearnerControls();
    renderLearner();
  } catch (_) {
    retryBtn.textContent = 'Retry connection';
    document.getElementById('learner-offline').style.display = 'flex';
    document.getElementById('learner-app').style.display = 'none';
  }
}

function wireLearnerControls() {
  if (wireLearnerControls.done) return;
  wireLearnerControls.done = true;
  document.getElementById('learner-save-profile').addEventListener('click', saveLearnerProfile);
  document.getElementById('learner-add-event').addEventListener('click', appendLearnerEvent);
  document.getElementById('learner-beliefs').addEventListener('click', e => {
    const row = e.target.closest('[data-belief-id]');
    if (row) showLearnerExplanation(row.dataset.beliefId);
  });
  document.getElementById('learner-struggles').addEventListener('click', e => {
    const row = e.target.closest('[data-belief-id]');
    if (row) showLearnerExplanation(row.dataset.beliefId);
  });
  document.getElementById('learner-recommendations').addEventListener('click', e => {
    const row = e.target.closest('[data-belief-id]');
    if (row) showLearnerExplanation(row.dataset.beliefId);
  });
}

function learnerLabel(id) {
  const node = learnerNodes.find(n => n.id === id);
  return node ? node.label : id;
}

function renderLearner() {
  renderLearnerProfile();
  renderLearnerConcepts();
  renderLearnerRecommendations();
  renderLearnerStruggles();
  renderLearnerBeliefs();
}

function renderLearnerProfile() {
  const prefs = learnerProfile.session_preferences || {};
  document.getElementById('learner-student-name').value = learnerProfile.student_name || '';
  document.getElementById('learner-exam-date').value = learnerProfile.exam_date || '';
  document.getElementById('learner-target-outcome').value = learnerProfile.target_outcome || '';
  document.getElementById('learner-sessions-per-day').value = prefs.sessions_per_day || 2;
  document.getElementById('learner-concepts-per-session').value = prefs.concepts_per_session || 4;
}

function renderLearnerConcepts() {
  const datalist = document.getElementById('learner-concepts');
  datalist.innerHTML = learnerNodes
    .filter(n => nodeType(n) === 'concept')
    .map(n => `<option value="${escA(n.id)}">${esc(n.label)}</option>`)
    .join('');
}

function learnerConfidence(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function learnerBeliefButton(belief, compact=false) {
  const label = belief.subject_label || learnerLabel(belief.subject);
  return `
    <button class="learner-belief-row ${belief.status}" data-belief-id="${escA(belief.id)}">
      <span>
        <strong>${esc(label)}</strong>
        ${compact ? '' : `<em>${esc(belief.id)}</em>`}
      </span>
      <span class="learner-status">
        <b>${esc(belief.status)}</b>
        ${learnerConfidence(belief.confidence)}
      </span>
    </button>`;
}

function renderLearnerRecommendations() {
  const container = document.getElementById('learner-recommendations');
  if (!learnerRecommendations.length) {
    container.innerHTML = '<div class="learner-empty">No active recommendations.</div>';
    return;
  }
  container.innerHTML = learnerRecommendations
    .map(belief => learnerBeliefButton(belief, true))
    .join('');
}

function renderLearnerStruggles() {
  const struggles = learnerBeliefs
    .filter(b => b.kind === 'struggling_with' && b.status === 'in')
    .sort((a, b) => b.confidence - a.confidence);
  const container = document.getElementById('learner-struggles');
  container.innerHTML = struggles.length
    ? struggles.map(belief => learnerBeliefButton(belief)).join('')
    : '<div class="learner-empty">No active struggle assumptions.</div>';
}

function renderLearnerBeliefs() {
  const groups = learnerBeliefs.reduce((acc, belief) => {
    (acc[belief.kind] ||= []).push(belief);
    return acc;
  }, {});
  const container = document.getElementById('learner-beliefs');
  const keys = Object.keys(groups).sort();
  if (!keys.length) {
    container.innerHTML = '<div class="learner-empty">No generated beliefs yet.</div>';
    return;
  }
  container.innerHTML = keys.map(kind => `
    <div class="learner-belief-group">
      <div class="learner-kind">${esc(kind.replace(/_/g, ' '))}</div>
      ${groups[kind]
        .sort((a, b) => (b.status === 'in') - (a.status === 'in') || b.confidence - a.confidence)
        .map(belief => learnerBeliefButton(belief))
        .join('')}
    </div>
  `).join('');
}

async function refreshLearnerData() {
  [learnerBeliefs, learnerRecommendations, learnerEvents] = await Promise.all([
    fetch('/api/learner/beliefs').then(r => r.json()),
    fetch('/api/learner/recommendations?limit=8').then(r => r.json()),
    fetch('/api/learner/events?limit=40').then(r => r.json()),
  ]);
  renderLearner();
}

async function saveLearnerProfile() {
  const profile = {
    ...learnerProfile,
    student_name: document.getElementById('learner-student-name').value.trim() || null,
    exam_date: document.getElementById('learner-exam-date').value || null,
    target_outcome: document.getElementById('learner-target-outcome').value.trim() || null,
    session_preferences: {
      ...(learnerProfile.session_preferences || {}),
      sessions_per_day: Number(document.getElementById('learner-sessions-per-day').value || 1),
      concepts_per_session: Number(document.getElementById('learner-concepts-per-session').value || 1),
    },
  };
  learnerProfile = await fetch('/api/learner/profile', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  }).then(r => r.json());
  await refreshLearnerData();
}

async function appendLearnerEvent() {
  const type = document.getElementById('learner-event-type').value;
  const conceptId = document.getElementById('learner-event-concept').value.trim();
  const rating = Number(document.getElementById('learner-event-rating').value);
  const polarity = document.getElementById('learner-event-polarity').value;
  const text = document.getElementById('learner-event-text').value.trim();
  const event = { type, source: 'study_hub' };

  if (type !== 'goal_set') {
    if (!conceptId) { alert('Concept is required for this event.'); return; }
    event.concept_id = conceptId;
  }
  if (type === 'flashcard_rating') event.rating = rating;
  if (type === 'quiz_answer') event.score = ({0: 0, 1: 0.33, 2: 0.66, 3: 1})[rating];
  if (type === 'self_report') {
    event.polarity = polarity;
    if (text) event.text = text;
  }
  if (type === 'mastery_mark') event.mastered = true;
  if (type === 'goal_set') {
    event.goal_id = 'exam_pass';
    event.exam_date = document.getElementById('learner-exam-date').value || undefined;
    event.target_outcome = document.getElementById('learner-target-outcome').value.trim() || undefined;
    if (text) event.text = text;
  }

  await fetch('/api/learner/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  });
  document.getElementById('learner-event-text').value = '';
  await refreshLearnerData();
}

function explainItemHtml(item) {
  const data = item.data;
  if (!data) return `<div class="learner-ref"><code>${esc(item.ref)}</code></div>`;
  if (item.kind === 'event') {
    const bits = [data.type, data.concept_id, data.rating !== undefined ? `rating ${data.rating}` : '', data.polarity]
      .filter(Boolean).join(' · ');
    return `<div class="learner-ref"><code>${esc(item.ref)}</code><span>${esc(bits)}</span>${data.text ? `<p>${esc(data.text)}</p>` : ''}</div>`;
  }
  if (item.kind === 'justification') {
    const measure = data.measure ? ` · ${esc(JSON.stringify(data.measure))}` : '';
    return `<div class="learner-ref"><code>${esc(item.ref)}</code><span>${esc(data.rule_id || '')}${measure}</span></div>`;
  }
  if (item.kind === 'relation') {
    return `<div class="learner-ref"><code>${esc(item.ref)}</code><span>${esc(data.source_label || data.source_id)} → ${esc(data.rel_type)} → ${esc(data.target_label || data.target_id)}</span>${data.note ? `<p>${esc(data.note)}</p>` : ''}</div>`;
  }
  if (item.kind === 'belief') {
    return `<div class="learner-ref"><code>${esc(item.ref)}</code><span>${esc(data.id)} · ${esc(data.status)} · ${learnerConfidence(data.confidence)}</span></div>`;
  }
  if (item.kind === 'schedule') {
    const concept = data.concept || {};
    return `<div class="learner-ref"><code>${esc(item.ref)}</code><span>${esc(data.date)} · ${esc(concept.label || data.concept_id || '')}</span></div>`;
  }
  if (item.kind === 'priority') {
    return `<div class="learner-ref"><code>${esc(item.ref)}</code><span>rank ${esc(data.rank)} · centrality ${esc(data.centrality || '')}</span></div>`;
  }
  return `<div class="learner-ref"><code>${esc(item.ref)}</code></div>`;
}

async function showLearnerExplanation(beliefId) {
  const data = await fetch(`/api/learner/explain/${encodeURIComponent(beliefId)}`).then(r => r.json());
  const container = document.getElementById('learner-explain');
  if (data.error) {
    container.innerHTML = '<div class="learner-empty">Belief not found.</div>';
    return;
  }
  const belief = data.belief;
  container.innerHTML = `
    <div class="learner-explain-head">
      <div>
        <div class="learner-kind">${esc(belief.kind.replace(/_/g, ' '))}</div>
        <h3>${esc(belief.subject_label || learnerLabel(belief.subject))}</h3>
        <code>${esc(belief.id)}</code>
      </div>
      <span class="learner-status ${esc(belief.status)}"><b>${esc(belief.status)}</b>${learnerConfidence(belief.confidence)}</span>
    </div>
    ${belief.reason ? `<p class="learner-reason">${esc(belief.reason)}</p>` : ''}
    <div class="learner-proof">
      <div>
        <div class="sect-label">Support</div>
        ${data.support.length ? data.support.map(explainItemHtml).join('') : '<div class="learner-empty">No support.</div>'}
      </div>
      <div>
        <div class="sect-label">Opposition</div>
        ${data.opposition.length ? data.opposition.map(explainItemHtml).join('') : '<div class="learner-empty">No opposition.</div>'}
      </div>
    </div>
  `;
}

/* ═══════════════════════════════════════
   NOTES READER
═══════════════════════════════════════ */
const noteNodeMap     = new Map(); // id → node
const noteRelCount    = new Map(); // id → relation count
const noteDocsData    = new Map(); // docId → {title, sections[]}
let   noteAnnRe       = null;
let   noteAnnIdMap    = {};        // lowercase label → node.id
let   activeNoteDocId = null;
let   noteScrollWired = false;
let   notePdfjsPromise = null;
let   notePdfRenderToken = 0;
let   noteActivePageNumber = 1;
let   noteSelectedTermId = null;
const notePageTerms = new Map(); // page number -> node[]

async function initNotes() {
  const retryBtn = document.getElementById('notes-retry-btn');
  retryBtn.textContent = 'Connecting…';
  try {
    const [docsData, nodesData, relsData] = await Promise.all([
      fetch('/api/docs').then(r => { if (!r.ok) throw 0; return r.json(); }),
      fetch('/api/nodes').then(r => r.json()),
      fetch('/api/relations').then(r => r.json()),
    ]);
    nodesData.forEach(n => noteNodeMap.set(n.id, n));
    relsData.forEach(r => {
      noteRelCount.set(r.source, (noteRelCount.get(r.source) || 0) + 1);
      noteRelCount.set(r.target, (noteRelCount.get(r.target) || 0) + 1);
    });
    _buildNoteAnnotationIndex(nodesData);
    document.getElementById('notes-offline').style.display = 'none';
    const reader = document.getElementById('notes-reader');
    reader.style.display = 'flex';
    _wireNoteScrollSpy();
    _renderNoteDocList(docsData);
  } catch (_) {
    retryBtn.textContent = 'Retry connection';
  }
}

function _buildNoteAnnotationIndex(nodesList) {
  const sorted = [...nodesList].sort((a, b) => b.label.length - a.label.length);
  noteAnnIdMap = {};
  const patterns = [];
  sorted.forEach(n => {
    const key = n.label.toLowerCase();
    if (!noteAnnIdMap[key]) {
      noteAnnIdMap[key] = n.id;
      patterns.push(n.label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    }
  });
  noteAnnRe = patterns.length ? new RegExp('\\b(' + patterns.join('|') + ')\\b', 'gi') : null;
}

async function _loadPdfJs() {
  if (!notePdfjsPromise) {
    notePdfjsPromise = import('/lib/pdfjs/pdf.mjs').then(pdfjs => {
      pdfjs.GlobalWorkerOptions.workerSrc = '/lib/pdfjs/pdf.worker.mjs';
      return pdfjs;
    });
  }
  return notePdfjsPromise;
}

function _termsFromPdfText(text) {
  if (!noteAnnRe || !text) return [];
  const seen = new Set();
  const terms = [];
  noteAnnRe.lastIndex = 0;
  let match;
  while ((match = noteAnnRe.exec(text)) !== null) {
    const nodeId = noteAnnIdMap[match[0].toLowerCase()];
    const node = nodeId ? noteNodeMap.get(nodeId) : null;
    if (!node || seen.has(node.id)) continue;
    seen.add(node.id);
    terms.push(node);
  }
  return terms;
}

function _renderNoteTermPanel(force = false) {
  const panel = document.getElementById('notes-term-panel');
  if (!panel) return;

  const terms = notePageTerms.get(noteActivePageNumber) || [];
  if (!terms.some(term => term.id === noteSelectedTermId)) {
    noteSelectedTermId = terms[0]?.id || null;
  }
  if (!force && panel.dataset.page === String(noteActivePageNumber) && panel.dataset.selected === String(noteSelectedTermId || '')) {
    return;
  }

  const selected = noteSelectedTermId ? noteNodeMap.get(noteSelectedTermId) : null;
  const relCount = selected ? (noteRelCount.get(selected.id) || 0) : 0;
  panel.dataset.page = String(noteActivePageNumber);
  panel.dataset.selected = String(noteSelectedTermId || '');
  panel.innerHTML = `
    <div class="notes-term-top">
      <div>
        <div class="sect-label">Page ${noteActivePageNumber}</div>
        <h3>Terms</h3>
      </div>
      <span class="notes-term-count">${terms.length}</span>
    </div>
    <div class="notes-term-chips">
      ${terms.length ? terms.map(term => `
        <button class="notes-term-chip ${term.id === noteSelectedTermId ? 'active' : ''}" data-node-id="${escA(term.id)}">
          ${esc(term.label)}
        </button>
      `).join('') : '<div class="notes-term-empty">No indexed terms on this page.</div>'}
    </div>
    ${selected ? `
      <div class="notes-term-detail">
        <div class="notes-term-type ${esc(selected._type || 'concept')}">${esc(selected._type || 'concept')}</div>
        <h4>${esc(selected.label)}</h4>
        <p>${esc(selected.description || '')}</p>
        <div class="notes-term-meta">${relCount} relation${relCount !== 1 ? 's' : ''} in the graph</div>
      </div>
    ` : ''}
  `;
}

function _setNoteActivePage(pageNumber, force = false) {
  if (!force && noteActivePageNumber === pageNumber) return;
  noteActivePageNumber = pageNumber;
  _renderNoteTermPanel(force);
}

function _wireNoteScrollSpy() {
  if (noteScrollWired) return;
  noteScrollWired = true;
  const main = document.getElementById('notes-main');
  main.addEventListener('scroll', debounce(() => {
    if (activeNoteDocId) _syncNoteActiveSection(activeNoteDocId);
  }, 80));
  main.addEventListener('click', e => {
    const chip = e.target.closest('.notes-term-chip');
    if (!chip) return;
    noteSelectedTermId = chip.dataset.nodeId;
    _renderNoteTermPanel(true);
  });
}

function _renderNoteDocList(docs) {
  const sidebar = document.getElementById('notes-sidebar-list');
  sidebar.innerHTML = docs.map(doc => `
    <div>
      <button class="notes-doc-btn" data-doc-id="${esc(doc.id)}">
        <span>${esc(doc.title)}</span>
        <span class="notes-doc-caret">›</span>
      </button>
      <div class="notes-sections" id="nsecs-${esc(doc.id)}"></div>
    </div>
  `).join('');

  sidebar.onclick = async e => {
    const docBtn = e.target.closest('.notes-doc-btn');
    const secBtn = e.target.closest('.notes-sec-btn');
    if (secBtn) {
      await _jumpToNoteSection(secBtn.dataset.docId, +secBtn.dataset.secIdx);
      return;
    }
    if (docBtn) {
      const docId  = docBtn.dataset.docId;
      const secsEl = document.getElementById('nsecs-' + docId);
      document.querySelectorAll('.notes-sections.open').forEach(el => el.classList.remove('open'));
      document.querySelectorAll('.notes-doc-btn.open').forEach(el => el.classList.remove('open'));
      docBtn.classList.add('open');
      secsEl.classList.add('open');
      const data = await _ensureNoteDocLoaded(docId, secsEl);
      if (data) await _renderNoteDocument(docId);
    }
  };
}

async function _ensureNoteDocLoaded(docId, secsEl) {
  if (noteDocsData.has(docId)) return noteDocsData.get(docId);
  secsEl.innerHTML = '<div class="notes-status">Loading…</div>';
  const data = await fetch(`/api/docs/${docId}/sections`).then(r => r.json()).catch(() => null);
  if (!data || data.error) {
    secsEl.innerHTML = '<div class="notes-status">Failed to load.</div>';
    return null;
  }
  noteDocsData.set(docId, data);
  secsEl.innerHTML = data.sections.map((s, i) =>
    `<button class="notes-sec-btn level-${s.level}" data-doc-id="${escA(docId)}" data-sec-idx="${i}">${esc(s.title)}</button>`
  ).join('');
  return data;
}

function _noteSectionId(docId, secIdx) {
  const data = noteDocsData.get(docId);
  const section = data && data.sections[secIdx];
  const page = section ? section.page_start : 1;
  return `note-page-${docId}-${page}`;
}

function _setNoteSectionActive(docId, secIdx) {
  document.querySelectorAll('.notes-sec-btn').forEach(b => b.classList.remove('active'));
  const secsEl = document.getElementById('nsecs-' + docId);
  const btn    = secsEl ? secsEl.querySelector(`[data-sec-idx="${secIdx}"]`) : null;
  if (btn) btn.classList.add('active');
}

function _sectionIndexForPdfPage(docId, pageNumber) {
  const data = noteDocsData.get(docId);
  if (!data || !data.sections.length) return 0;

  let sectionIndex = 0;
  data.sections.forEach((section, index) => {
    if (section.page_start <= pageNumber) sectionIndex = index;
  });
  return sectionIndex;
}

async function _renderPdfPage(pdfjs, pdfDoc, pageNumber, container, scale, token) {
  if (token !== notePdfRenderToken) return;

  const page = await pdfDoc.getPage(pageNumber);
  if (token !== notePdfRenderToken) return;

  const viewport = page.getViewport({ scale });
  const pageEl = container.querySelector(`[data-page-number="${pageNumber}"]`);
  if (!pageEl) return;

  const canvas = pageEl.querySelector('canvas');
  const outputScale = window.devicePixelRatio || 1;

  pageEl.style.width = `${viewport.width}px`;
  pageEl.style.height = `${viewport.height}px`;
  pageEl.style.setProperty('--total-scale-factor', String(scale));
  canvas.width = Math.floor(viewport.width * outputScale);
  canvas.height = Math.floor(viewport.height * outputScale);
  canvas.style.width = `${Math.floor(viewport.width)}px`;
  canvas.style.height = `${Math.floor(viewport.height)}px`;

  const context = canvas.getContext('2d', { alpha: false });
  const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null;
  await page.render({ canvasContext: context, transform, viewport }).promise;
  if (token !== notePdfRenderToken) return;

  const textContent = await page.getTextContent();
  if (token !== notePdfRenderToken) return;
  const pageText = textContent.items.map(item => item.str || '').join(' ');
  notePageTerms.set(pageNumber, _termsFromPdfText(pageText));
  if (pageNumber === noteActivePageNumber) _renderNoteTermPanel(true);
  pageEl.classList.add('rendered');
}

async function _renderNoteDocument(docId) {
  const data = noteDocsData.get(docId);
  if (!data) return;
  activeNoteDocId = docId;
  const token = ++notePdfRenderToken;
  noteActivePageNumber = 1;
  noteSelectedTermId = null;
  notePageTerms.clear();

  const main = document.getElementById('notes-main');
  main.innerHTML = `
    <div class="notes-content-inner">
      <div class="notes-document-head">
        <div class="eyebrow">Course Notes</div>
        <h2 class="notes-document-title">${esc(data.title)}</h2>
        <div class="notes-document-meta">Loading PDF · ${data.sections.length} sections</div>
      </div>
      <aside class="notes-term-panel" id="notes-term-panel"></aside>
      <div class="notes-pdf-pages" id="notes-pdf-pages"></div>
    </div>
  `;
  main.scrollTop = 0;
  _setNoteSectionActive(docId, 0);
  _renderNoteTermPanel(true);

  try {
    const pdfjs = await _loadPdfJs();
    if (token !== notePdfRenderToken) return;

    const pdfDoc = await pdfjs.getDocument({ url: `/api/docs/${encodeURIComponent(docId)}/pdf` }).promise;
    if (token !== notePdfRenderToken) return;

    const firstPage = await pdfDoc.getPage(1);
    const baseViewport = firstPage.getViewport({ scale: 1 });
    const availableWidth = Math.max(420, Math.min(main.clientWidth - 96, 920));
    const scale = Math.max(0.62, Math.min(1.5, availableWidth / baseViewport.width));
    const pagesEl = document.getElementById('notes-pdf-pages');
    const metaEl = main.querySelector('.notes-document-meta');
    metaEl.textContent = `PDF view · ${pdfDoc.numPages} pages · ${data.sections.length} sections`;
    pagesEl.innerHTML = Array.from({ length: pdfDoc.numPages }, (_, index) => {
      const pageNumber = index + 1;
      return `
        <section class="notes-pdf-page" id="note-page-${escA(docId)}-${pageNumber}" data-page-number="${pageNumber}">
          <div class="notes-page-number">Page ${pageNumber}</div>
          <canvas></canvas>
        </section>
      `;
    }).join('');

    for (let pageNumber = 1; pageNumber <= pdfDoc.numPages; pageNumber++) {
      await _renderPdfPage(pdfjs, pdfDoc, pageNumber, pagesEl, scale, token);
    }
  } catch (err) {
    console.error('PDF render failed', err);
    if (token !== notePdfRenderToken) return;
    main.querySelector('.notes-document-meta').textContent = 'PDF failed to load';
    document.getElementById('notes-pdf-pages').innerHTML =
      '<div class="notes-pdf-error">Could not render this PDF. Try restarting the local server.</div>';
  }
}

async function _jumpToNoteSection(docId, secIdx) {
  if (activeNoteDocId !== docId) await _renderNoteDocument(docId);
  _setNoteSectionActive(docId, secIdx);

  const main = document.getElementById('notes-main');
  const target = document.getElementById(_noteSectionId(docId, secIdx));
  if (!target) return;
  main.scrollTo({ top: Math.max(target.offsetTop - 22, 0), behavior: 'smooth' });
}

function _syncNoteActiveSection(docId) {
  const main = document.getElementById('notes-main');
  const pages = [...main.querySelectorAll('.notes-pdf-page')];
  if (!pages.length) return;

  let currentPage = Number(pages[0].dataset.pageNumber || 1);
  const mainTop = main.getBoundingClientRect().top;
  for (const page of pages) {
    if (page.getBoundingClientRect().top - mainTop <= 140) currentPage = Number(page.dataset.pageNumber || 1);
    else break;
  }
  _setNoteSectionActive(docId, _sectionIndexForPdfPage(docId, currentPage));
  _setNoteActivePage(currentPage);
}

/* ── Annotation tooltip ── */
const annTip = document.getElementById('ann-tip');
let   annTipTimer;

document.addEventListener('mouseover', e => {
  const span = e.target.closest('.ann');
  if (!span) return;
  clearTimeout(annTipTimer);
  const node = noteNodeMap.get(span.dataset.id);
  if (!node) return;
  const rels  = noteRelCount.get(node.id) || 0;
  const type  = node._type || 'concept';
  const desc  = (node.description || '').slice(0, 200);
  annTip.innerHTML = `
    <div class="ann-tip-badge ${esc(type)}">${esc(type).toUpperCase()}</div>
    <div class="ann-tip-label">${esc(node.label)}</div>
    <div class="ann-tip-desc">${esc(desc)}${node.description && node.description.length > 200 ? '…' : ''}</div>
    <div class="ann-tip-rels">${rels} relation${rels !== 1 ? 's' : ''} in the graph</div>
  `;
  _moveTip(e);
  annTip.classList.add('visible');
});

document.addEventListener('mousemove', e => {
  if (e.target.closest('.ann')) _moveTip(e);
});

document.addEventListener('mouseout', e => {
  if (e.target.closest('.ann')) {
    annTipTimer = setTimeout(() => annTip.classList.remove('visible'), 80);
  }
});

function _moveTip(e) {
  const pad = 14;
  const tw  = annTip.offsetWidth  || 280;
  const th  = annTip.offsetHeight || 130;
  let x = e.clientX + pad;
  let y = e.clientY + pad;
  if (x + tw > window.innerWidth  - 8) x = e.clientX - tw - pad;
  if (y + th > window.innerHeight - 8) y = e.clientY - th - pad;
  annTip.style.left = x + 'px';
  annTip.style.top  = y + 'px';
}

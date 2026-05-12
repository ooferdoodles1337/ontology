/* ═══════════════════════════════════════
   TAB SWITCHING
═══════════════════════════════════════ */
let kbInitialised    = false;
let notesInitialised = false;

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
   NOTES READER
═══════════════════════════════════════ */
const noteNodeMap     = new Map(); // id → node
const noteRelCount    = new Map(); // id → relation count
const noteDocsData    = new Map(); // docId → {title, sections[]}
let   noteAnnRe       = null;
let   noteAnnIdMap    = {};        // lowercase label → node.id

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

function _annotateSection(text) {
  if (!noteAnnRe) return esc(text);
  const parts = [];
  let last = 0;
  noteAnnRe.lastIndex = 0;
  let m;
  while ((m = noteAnnRe.exec(text)) !== null) {
    if (m.index > last) parts.push(esc(text.slice(last, m.index)));
    const nodeId = noteAnnIdMap[m[0].toLowerCase()];
    const node   = nodeId ? noteNodeMap.get(nodeId) : null;
    if (node) {
      parts.push(`<span class="ann" data-id="${esc(node.id)}" data-type="${esc(node._type || 'concept')}">${esc(m[0])}</span>`);
    } else {
      parts.push(esc(m[0]));
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(esc(text.slice(last)));
  return parts.join('').replace(/\n/g, '<br>');
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

  sidebar.addEventListener('click', async e => {
    const docBtn = e.target.closest('.notes-doc-btn');
    const secBtn = e.target.closest('.notes-sec-btn');
    if (secBtn) {
      _selectNoteSection(secBtn.dataset.docId, +secBtn.dataset.secIdx);
      return;
    }
    if (docBtn) {
      const docId  = docBtn.dataset.docId;
      const secsEl = document.getElementById('nsecs-' + docId);
      const isOpen = secsEl.classList.contains('open');
      document.querySelectorAll('.notes-sections.open').forEach(el => el.classList.remove('open'));
      document.querySelectorAll('.notes-doc-btn.open').forEach(el => el.classList.remove('open'));
      if (!isOpen) {
        docBtn.classList.add('open');
        secsEl.classList.add('open');
        if (!noteDocsData.has(docId)) {
          secsEl.innerHTML = '<div style="padding:8px 14px 8px 22px;color:var(--text-muted);font-size:11px;">Loading…</div>';
          const data = await fetch(`/api/docs/${docId}/sections`).then(r => r.json()).catch(() => null);
          if (!data || data.error) {
            secsEl.innerHTML = '<div style="padding:8px 14px;color:var(--text-muted);font-size:11px;">Failed to load.</div>';
            return;
          }
          noteDocsData.set(docId, data);
          secsEl.innerHTML = data.sections.map((s, i) =>
            `<button class="notes-sec-btn level-${s.level}" data-doc-id="${esc(docId)}" data-sec-idx="${i}">${esc(s.title)}</button>`
          ).join('');
        }
      }
    }
  });
}

function _selectNoteSection(docId, secIdx) {
  document.querySelectorAll('.notes-sec-btn').forEach(b => b.classList.remove('active'));
  const secsEl = document.getElementById('nsecs-' + docId);
  const btn    = secsEl ? secsEl.querySelector(`[data-sec-idx="${secIdx}"]`) : null;
  if (btn) btn.classList.add('active');

  const data    = noteDocsData.get(docId);
  const section = data && data.sections[secIdx];
  if (!section) return;

  document.getElementById('notes-main').innerHTML = `
    <div class="notes-content-inner">
      <div class="notes-section-head">
        <h2 class="notes-section-title">${esc(section.title)}</h2>
        <div class="notes-section-meta">p. ${esc(String(section.page_start))} · ${esc(data.title)}</div>
      </div>
      <div class="notes-prose">${_annotateSection(section.text)}</div>
    </div>
  `;
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

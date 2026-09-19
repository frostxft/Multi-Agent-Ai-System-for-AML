'use strict';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const score = n => n == null ? '—' : Number(n).toFixed(3);
const pct = n => n == null ? '—' : (n * 100).toFixed(1) + '%';
let token = '', selected = null, activeTab = 'overview', graphFocus = null, caseList = [], health = null, experienceMode = 'judge', demoCollection = null, overviewData = null;
const tabs = [
  {id:'overview', label:'Overview'},
  {id:'network', label:'Network & Explanation'},
  {id:'evidence', label:'Evidence & Report'},
  {id:'review', label:'Review & Audit'}
];
function error(e) { $('error').textContent = e.message || String(e); $('error').hidden = false; }
async function api(path, options = {}) {
  $('error').hidden = true;
  const response = await fetch('/api' + path, {...options, headers: {'Content-Type':'application/json', ...(token ? {'Authorization':'Bearer ' + token} : {}), ...options.headers}});
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
  return data;
}
const badge = (text, cls = '') => `<span class="badge ${esc(cls)}">${esc(String(text).replaceAll('_',' '))}</span>`;
const citations = ids => ids.map(id => `<button class="citation" data-evidence="${esc(id)}">[${esc(id)}]</button>`).join(' ');
const jsonDetails = (title, value) => `<details class="disclosure"><summary>${esc(title)}</summary><div class="inner"><pre>${esc(JSON.stringify(value, null, 2))}</pre></div></details>`;

async function refresh() {
  try {
    health = await api('/health');
    $('mode').textContent = health.mode === 'loopback_demo' ? 'Local demonstration' : 'Role: ' + health.role;
    const [overview, cases, collection] = await Promise.all([api('/overview'), api('/cases'), api('/demo-collection')]);
    overviewData = overview;
    demoCollection = collection;
    $('start-investigation').disabled = collection.status !== 'available';
    $('start-note').textContent = collection.status === 'available' ? 'Open the recorded canonical case. No new case or decision is created.' : collection.reason;
    caseList = cases;
    const dataLabel = overview.data.kind === 'benchmark' ? 'Real Elliptic Bitcoin benchmark' : overview.data.kind === 'synthetic_test' ? 'SYNTHETIC TEST DATA — not benchmark performance' : 'UNVERIFIED INPUT — provenance not confirmed';
    $('data-notice').textContent = `Research prototype · ${dataLabel} · All narratives are drafts. Human approval does not file a SAR.`;
    $('evaluation-title').textContent = overview.data.kind === 'benchmark' ? 'Benchmark evaluation & methodology' : 'Synthetic / unverified evaluation — not benchmark results';
    const test = overview.evaluation.gat.test;
    $('technical-stats').innerHTML = [
      ['Transaction nodes', overview.data.nodes.toLocaleString(), `${overview.data.edges.toLocaleString()} directed payment flows`],
      ['Cases in review', cases.filter(c => ['awaiting_review','changes_requested'].includes(c.status)).length, `${cases.length} persisted cases`],
      ['Held-out average precision', test.pr_auc_average_precision.toFixed(3), 'GAT · minority illicit class'],
      ['Held-out recall', pct(test.recall), `Threshold ${test.threshold.toFixed(2)} · validation-selected`]
    ].map(([a,b,c]) => `<div class="card"><div class="stat-label">${a}</div><div class="stat-value">${b}</div><div class="stat-note">${c}</div></div>`).join('');
    renderQueue();
    const r = overview.evaluation;
    $('evaluation').innerHTML = `<p class="muted">${esc(r.methodology)}</p><table><thead><tr><th>Model / held-out test</th><th>Precision</th><th>Recall</th><th>Average precision</th><th>TN / FP / FN / TP</th></tr></thead><tbody>${[['GAT',r.gat.test],['Logistic baseline',r.baseline.test]].map(([n,m])=>`<tr><td>${n}</td><td>${pct(m.precision)}</td><td>${pct(m.recall)}</td><td>${m.pr_auc_average_precision.toFixed(3)}</td><td>${m.confusion_matrix_tn_fp_fn_tp.join(' / ')}</td></tr>`).join('')}</tbody></table><p class="warning">Measured research results. ${esc(r.false_positive_change.caveat)} Scores are uncalibrated. No business savings or real-world AML effectiveness is established.</p>${jsonDetails('Dataset profile and provenance',overview.data)}${jsonDetails('Complete evaluation',r)}`;
    if (overview.multiseed) {
      const study = overview.multiseed;
      $('evaluation').innerHTML += `<h3>Fixed three-seed replication / mean ± sample SD</h3><p class="muted">Separate from the original single run above. Reused held-out benchmark; no seed selected as winner.</p><table><tr><th>Model</th><th>Precision</th><th>Recall</th><th>Average Precision (AP)</th></tr>${Object.entries(study.summary).map(([model,values])=>`<tr><td>${esc(model)}</td>${['precision','recall','average_precision'].map(k=>`<td>${values[k].mean.toFixed(4)} ± ${values[k].sample_standard_deviation.toFixed(4)}</td>`).join('')}</tr>`).join('')}</table><p class="muted">Baseline wins precision and recall at validation-selected thresholds. GAT has higher mean AP. No matched-recall or business improvement is established.</p>${jsonDetails('Multi-seed protocol and per-seed results',study)}`;
    }
    Workstation.operatingExplorer(overview.validation_analysis);
    if (selected) await loadCase(selected.id);
    else if (Presentation.collection(caseList, demoCollection, experienceMode).length) await loadCase(Presentation.collection(caseList, demoCollection, experienceMode)[0].id);
  } catch(e) { error(e); }
}

function renderQueue() {
  const collection = Presentation.collection(caseList, demoCollection, experienceMode);
  const counts = Presentation.counts(collection);
  $('collection-scope').textContent = experienceMode === 'judge' ? `${collection.length} recorded demo cases · ${caseList.length} stored runs preserved in Technical Mode.` : `All ${caseList.length} stored runs, including historical/repeated transactions.`;
  $('queue-title').textContent = experienceMode === 'judge' ? 'Demo cases' : 'All case runs';
  const countEl = $('side-review-count');
  if (countEl) { countEl.textContent = counts.review; countEl.hidden = counts.review === 0; }
  $('stats').innerHTML = [
    ['Awaiting decision', counts.review, 'Open cases requiring an investigator'],
    ['High priority', counts.high, 'Open cases with high triage priority'],
    ['Evidence-ready', counts.evidence, 'Source-linked records pass traceability'],
    ['Review status', counts.ready + ' ready', counts.blocked + ' blocked · human decision required']
  ].map(([k,v,n]) => `<div class="card"><span class="stat-label">${k}</span><div class="stat-value">${v}</div><small>${n}</small></div>`).join('');
  const query = $('queue-search').value.toLowerCase(), status = $('queue-status').value, priority = $('queue-priority').value;
  const visible = collection.filter(c => (c.id+' '+c.transaction_id).toLowerCase().includes(query) && (!status||c.status===status) && (!priority||c.severity===priority) && (!$('queue-score').value||(c.score??-1)>=Number($('queue-score').value)) && (!$('queue-compliance').value||c.compliance_status===$('queue-compliance').value) && (!$('queue-provider').value||c.narrative_provider===$('queue-provider').value) && (!$('queue-readiness').value||(c.readiness??-1)>=Number($('queue-readiness').value)) && (!$('queue-date').value||new Date(c.created_at)>=new Date($('queue-date').value+'T00:00:00')));
  $('queue-count').textContent = visible.length + ' / ' + collection.length + ' cases';
  $('comparison').innerHTML = `<table><tr><th>Case / TX</th><th>Score</th><th>Priority</th><th>Nodes / evidence</th><th>Readiness</th><th>Provider</th><th>Review / compliance</th></tr>${visible.map(c=>`<tr><td><button class="quiet" data-case="${esc(c.id)}">${esc(c.id)}</button></td><td>${score(c.score)}</td><td>${esc(c.severity)}</td><td>${c.node_count} / ${c.evidence_count}</td><td>${c.readiness??'—'}</td><td>${esc(c.narrative_provider)}</td><td>${esc(c.status)} / ${esc(c.compliance_status)}</td></tr>`).join('')}</table>`;
  $('cases').innerHTML = visible.length ? visible.map(c => `<button class="case ${selected?.id===c.id?'selected':''}" data-case="${esc(c.id)}">
    <div class="case-top"><span class="tx">Transaction ${esc(c.transaction_id)}</span><span class="case-id">${esc(c.id)}</span></div>
    <div class="case-top" style="margin-top:6px">${badge((c.severity||'pending')+' priority', c.severity)}${badge(Presentation.statusLabel(c.status), c.status)}</div>
    <div class="case-meta"><span>Score <b>${score(c.score)}</b></span><span><b>${c.node_count}</b> connected</span><span><b>${c.evidence_count}</b> evidence</span></div>
    <div class="case-review">${esc(Presentation.review(c))}</div>
    ${experienceMode==='technical'?`<div class="case-id" style="margin-top:4px">${esc(c.data_kind)} · ${new Date(c.created_at).toLocaleDateString()} · rev ${c.revision}</div>`:''}
  </button>`).join('') : '<p class="muted">No matching cases. Adjust filters or use Technical Mode for historical runs.</p>';
  document.querySelectorAll('[data-case]').forEach(b => b.addEventListener('click', () => loadCase(b.dataset.case).catch(error)));
  renderDesk();
}

function renderDesk() {
  const el = $('desk-content');
  if (!el) return;
  const collection = Presentation.collection(caseList, demoCollection, experienceMode);
  const first = collection[0] || caseList[0];
  const card = first ? `<div class="selected-case">
    <div class="sc-top"><span class="eyebrow">Selected investigation</span>${badge((first.severity || 'pending') + ' priority', first.severity)}</div>
    <div class="sc-tx">Transaction <strong>${esc(first.transaction_id)}</strong><span class="muted"> · ${esc(first.id)}</span></div>
    <div class="sc-kpis">
      <div class="kpi"><div class="kpi-label">Model score</div><div class="kpi-value">${score(first.score)}</div><div class="kpi-note">not a probability</div></div>
      <div class="kpi"><div class="kpi-label">Connected</div><div class="kpi-value">${first.node_count}</div><div class="kpi-note">transactions</div></div>
      <div class="kpi"><div class="kpi-label">Evidence</div><div class="kpi-value">${first.evidence_count}</div><div class="kpi-note">records</div></div>
      <div class="kpi"><div class="kpi-label">Status</div><div class="kpi-value">${esc(Presentation.review(first))}</div><div class="kpi-note">human decision</div></div>
    </div>
    <div class="sc-actions"><button class="primary" data-desk-open="${esc(first.id)}">Open investigation</button><button class="quiet" data-desk-explore="${esc(first.id)}">Explore network</button></div>
  </div>` : '<div class="muted">No recorded case available.</div>';
  const stages = [
    { n: '01', label: 'Detection', desc: 'Identify high-risk transactions', sub: 'Transaction network · AI detection' },
    { n: '02', label: 'Risk triage', desc: 'Prioritise investigator attention', sub: 'Thresholds · network signals' },
    { n: '03', label: 'Investigation', desc: 'Gather network evidence and context', sub: 'Evidence · demo KYC/sanctions' },
    { n: '04', label: 'SAR narrative', desc: 'Prepare an evidence-grounded draft', sub: 'Draft suspicious activity report' },
    { n: '05', label: 'Compliance', desc: 'Validate traceability and provenance', sub: 'Checks · baseline cross-check' },
    { n: '06', label: 'Human review', desc: 'Investigator makes the decision', sub: 'Approve · request changes · reject · reopen' },
    { n: '07', label: 'Audit', desc: 'Record every action', sub: 'Persistent audit trail' }
  ];
  const flow = `<div class="flow">${stages.map((s, i) => `<div class="flow-step"><span class="flow-num">${s.n}</span><div class="flow-body"><h3>${s.label}</h3><p>${s.desc}</p><span class="flow-sub">${s.sub}</span></div></div>` + (i < stages.length - 1 ? '<span class="flow-arrow" aria-hidden="true">→</span>' : '')).join('')}</div>`;
  el.innerHTML = card + `<div class="section-title" style="margin-top:20px"><h2>How ZEN works</h2><span class="sub">Detection → Risk triage → Investigation → SAR narrative → Compliance → Human review → Audit</span></div>` + flow;
  el.querySelectorAll('[data-desk-open]').forEach(b => b.addEventListener('click', () => { activeTab = 'overview'; loadCase(b.dataset.deskOpen).then(() => $('detail').scrollIntoView({block:'start',behavior:'smooth'})).catch(error); }));
  el.querySelectorAll('[data-desk-explore]').forEach(b => b.addEventListener('click', () => { activeTab = 'network'; loadCase(b.dataset.deskExplore).then(() => $('detail').scrollIntoView({block:'start',behavior:'smooth'})).catch(error); }));
}

async function goStage(tab) {
  if (tab === 'performance') { $('technical-performance').open = true; $('technical-performance').scrollIntoView({block:'start',behavior:'smooth'}); return; }
  if (!selected) {
    const first = Presentation.collection(caseList, demoCollection, experienceMode)[0];
    if (!first) return;
    await loadCase(first.id);
  }
  activeTab = tab;
  await renderDetail();
  $('detail').scrollIntoView({block:'start',behavior:'smooth'});
}

async function loadCase(id) {
  const loaded = await api('/cases/' + encodeURIComponent(id));
  selected = loaded;
  try { selected.demo_enrichment = await api(`/cases/${encodeURIComponent(id)}/demo-enrichment`); }
  catch(e) { selected.demo_enrichment = null; }
  renderQueue();
  await renderDetail();
}

async function renderDetail() {
  const c = selected, o = c.outputs, d = o.detection;
  const ev = o.investigation?.evidence || [];
  const priority = o.triage?.severity || 'pending';
  const head = `<div class="detail-top">
    <div class="case-head">
      <div class="who">
        <span class="eyebrow">Case workspace</span>
        <h2>Transaction ${esc(c.transaction_id)}</h2>
        <div class="case-id">${esc(c.id)} · Revision ${c.revision} · ${esc(c.data_kind)}</div>
        <div class="flags">${badge(priority + ' priority', priority)}${badge(Presentation.statusLabel(c.status), c.status)}${c.demo_enrichment ? badge('DEMO enrichment', 'medium') : ''}</div>
      </div>
      <div class="kpis">
        <div class="kpi"><div class="kpi-label">Model score</div><div class="kpi-value">${score(d?.score)}</div><div class="kpi-note">not a probability</div></div>
        <div class="kpi"><div class="kpi-label">Alert threshold</div><div class="kpi-value">${d?.threshold != null ? d.threshold.toFixed(3) : '—'}</div><div class="kpi-note">case threshold</div></div>
        <div class="kpi"><div class="kpi-label">Connected context</div><div class="kpi-value">${d ? d.subgraph.nodes.length : '—'}</div><div class="kpi-note">transactions</div></div>
        <div class="kpi"><div class="kpi-label">Evidence</div><div class="kpi-value">${ev.length}</div><div class="kpi-note">linked records</div></div>
      </div>
    </div>
    <nav class="steps" role="tablist" aria-label="Investigation sections">
      ${tabs.map((t,i) => `<button class="step ${t.id===activeTab?'active':''}" aria-current="${t.id===activeTab?'step':'false'}" data-step="${t.id}"><span class="step-num">${i+1}</span>${t.label}</button>`).join('')}
    </nav>
  </div>${c.error ? `<div class="warning" style="margin-top:12px">Stage failed: ${esc(c.error.stage)} — ${esc(c.error.message)} <button id="retry" class="quiet">Retry failed stage</button></div>` : ''}<div id="tab-body"></div>`;
  $('detail').innerHTML = head;
  document.querySelectorAll('[data-step]').forEach(b => b.addEventListener('click', () => { activeTab = b.dataset.step; renderDetail().catch(error); }));
  if ($('retry')) $('retry').onclick = async () => { try { await api(`/cases/${c.id}/retry`, {method:'POST'}); await refresh(); } catch(e) { error(e); } };
  const body = $('tab-body');
  if (activeTab === 'overview') { Judge.overview(c, body); }
  else if (activeTab === 'network') { Judge.networkExplanation(c, body); }
  else if (activeTab === 'evidence') { Judge.evidenceReport(c, body); }
  else if (activeTab === 'review') {
    let audit = null;
    try { audit = await api(`/cases/${c.id}/audit`); } catch(e) { error(e); }
    if (selected?.id !== c.id || activeTab !== 'review') return;
    Judge.reviewAudit(c, body, audit);
  }
  Workstation.bindNavigation();
}

function setExperience(mode) {
  experienceMode = mode; document.body.dataset.experience = mode;
  $('judge-mode').setAttribute('aria-pressed', String(mode === 'judge'));
  $('technical-mode').setAttribute('aria-pressed', String(mode === 'technical'));
  $('technical-performance').open = mode === 'technical';
  renderQueue();
  if (selected) renderDetail().catch(error);
}

$('judge-mode').onclick = () => setExperience('judge');
$('technical-mode').onclick = () => setExperience('technical');
$('start-investigation').onclick = async () => { try { activeTab = 'overview'; await loadCase(demoCollection.canonical_case_id); } catch(e) { error(e); } };
$('show-performance').onclick = () => { setExperience('technical'); $('technical-performance').scrollIntoView({block:'start',behavior:'smooth'}); };
$('refresh').onclick = refresh;
$('credentials').onclick = () => { const value = prompt('Enter analyst or reviewer bearer token. It is kept only in this page memory.'); if (value !== null) { token = value; refresh(); } };
$('create').onsubmit = async e => { e.preventDefault(); const b = e.target.querySelector('button'); b.disabled = true; b.textContent = 'Running…'; try { const c = await api('/cases', {method:'POST', body:JSON.stringify({transaction_id:$('transaction').value.trim()})}); selected = c; await refresh(); } catch(err) { error(err); } finally { b.disabled = false; b.textContent = 'Run'; } };
$('system-status').onclick = async () => { try { const [status, model] = await Promise.all([api('/status'), api('/model')]); $('system-details').innerHTML = jsonDetails('Runtime status', status) + jsonDetails('Model and threshold provenance', model); } catch(e) { error(e); } };

['queue-search','queue-status','queue-priority','queue-score','queue-compliance','queue-provider','queue-readiness','queue-date'].forEach(id => $(id).oninput = renderQueue);

document.querySelectorAll('.side-link').forEach(btn => btn.addEventListener('click', () => {
  document.querySelectorAll('.side-link').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const nav = btn.dataset.nav;
  if (nav === 'desk') { document.querySelector('#desk').scrollIntoView({block:'start',behavior:'smooth'}); }
  else if (nav === 'cases') { document.querySelector('.workspace').scrollIntoView({block:'start',behavior:'smooth'}); }
  else if (nav === 'architecture') { const a = document.querySelector('.architecture'); a.open = true; a.scrollIntoView({block:'start',behavior:'smooth'}); }
  else if (nav === 'technical') { setExperience('technical'); $('technical-performance').scrollIntoView({block:'start',behavior:'smooth'}); }
  else if (['overview','network','evidence','review'].includes(nav)) { goStage(nav).catch(error); }
}));

refresh();

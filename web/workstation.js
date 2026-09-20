'use strict';
// Investigator views use only supplied case/API state; no frontend success fixtures.
const Workstation = {
  network(c, body) {
    const d = c.outputs.detection;
    if (!d) { body.textContent = 'Detection unavailable. Inspect the failed stage and audit; prior successful stages remain stored.'; return; }
    const g = d.subgraph, s = g.structure;
    body.innerHTML = `
      <p class="muted">Transaction network — connected payment-flow context. ${esc(g.score_scope || 'Historical snapshot: per-neighbor scores were not retained.')}</p>
      <div class="legend">
        <span><span class="sw target"></span>Target transaction</span>
        <span><span class="sw suspicious"></span>High-score connected</span>
        <span><span class="sw ctx"></span>Other context</span>
        <span style="opacity:.7">· wider arrow = greater explanation weight</span>
      </div>
      <svg class="graph" id="network" viewBox="0 0 700 345" role="img" aria-label="Directed transaction network"></svg>
      <p id="graph-visible" class="graph-note"></p>
      <div id="graph-inspector" class="graph-inspector">Select a transaction or relationship.</div>
      <div class="what-shows"><h4>What this shows</h4><p>ZEN evaluates transaction relationships as part of the graph model's local context. The highlighted relationships contributed more strongly to the local explanation — thicker arrows indicate greater explanation importance. This does not by itself prove illicit activity.</p></div>
      ${Judge.disclosure('Explore the network — filters', `<div class="filter-grid">
        <label>Context depth<select id="graph-depth"><option value="2">Up to 2 incoming hops</option><option value="1">Up to 1 incoming hop</option><option value="0">Target only</option></select></label>
        <label>Nodes<select id="graph-node-mode"><option value="all">All stored nodes</option><option value="risk">Above case threshold</option></select></label>
        <label>Edges<select id="graph-edge-mode"><option value="all">All stored edges</option><option value="top">Top 5 explanation masks</option></select></label>
        <label>Dataset time step<select id="graph-time"><option value="all">All stored time steps</option>${[...new Set(g.nodes.map(n => n.time_step))].sort((a,b) => a-b).map(t => `<option value="${t}">${t}</option>`).join('')}</select></label>
      </div>`, experienceMode === 'technical')}
      ${s ? Judge.disclosure('Network analytics', `<div class="metric-grid">${[['Local density', s.directed_density.toFixed(3)], ['Max fan-in / fan-out', s.max_in_degree + ' / ' + s.max_out_degree], ['Weak components', s.weak_components], ['Above threshold', s.above_threshold_nodes + ' / ' + s.scored_nodes], ['Directed cycle', s.has_directed_cycle ? 'Present' : 'Absent']].map(([k,v]) => `<div class="mini"><span class="stat-label">${k}</span><h3 style="margin:4px 0 0">${v}</h3></div>`).join('')}</div><p class="warning">Local topology and uncalibrated scores are not evidence of a laundering typology. Filters change only this view; the full stored evidence remains intact.</p>`, experienceMode === 'technical') : '<p class="muted">Historical case: structural analysis was not stored. Use a newly generated case for the enhanced view.</p>'}
      ${jsonDetails('Recorded threshold policy', d.threshold_policy || {})}`;
    ['graph-depth','graph-node-mode','graph-edge-mode','graph-time'].forEach(id => { const el = $(id); if (el) el.onchange = () => Workstation.drawNetwork(c); });
    Workstation.drawNetwork(c);
  },
  drawNetwork(c) {
    const g = c.outputs.detection.subgraph, threshold = c.outputs.detection.threshold, metrics = new Map((g.structure?.node_metrics || []).map(n => [n.id, n]));
    const depth = Number($('graph-depth').value), risk = $('graph-node-mode').value === 'risk', time = $('graph-time').value;
    const visible = g.nodes.filter(n => n.target || ((metrics.get(n.id)?.distance_to_target ?? 2) <= depth && (!risk || (n.model_score ?? -1) >= threshold) && (time === 'all' || n.time_step === Number(time))));
    const nodes = [...visible].sort((a,b) => Number(b.target) - Number(a.target) || b.attribution - a.attribution).slice(0,70);
    const groups = new Map(); nodes.forEach(n => { const level = n.target ? 0 : (metrics.get(n.id)?.distance_to_target ?? 2); if (!groups.has(level)) groups.set(level, []); groups.get(level).push(n); });
    const points = new Map(); groups.forEach((list, level) => list.forEach((n, i) => points.set(n.id, {...n, x:600 - level * 235, y:40 + (i + 1) * 260 / (list.length + 1)})));
    const storedEdges = $('graph-edge-mode').value === 'top' ? [...g.edges].sort((a,b) => b.attribution - a.attribution).slice(0,5) : g.edges;
    const edges = storedEdges.filter(e => points.has(e.source) && points.has(e.target)), svg = $('network');
    svg.innerHTML = `<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="12" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#5b8def"/></marker></defs><g id="graph-layer">${edges.map((e,i) => { const a = points.get(e.source), b = points.get(e.target); return `<line data-edge="${i}" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="#41577a" stroke-width="${1 + e.attribution * 4}" marker-end="url(#arrow)"><title>${esc(e.source)} → ${esc(e.target)}; mask ${e.attribution.toFixed(4)}</title></line>`; }).join('')}${[...points.values()].map(n => `<g data-node="${esc(n.id)}" role="button" tabindex="0" aria-label="Inspect transaction ${esc(n.id)}"><circle class="${n.target ? 'target' : n.model_score >= threshold ? 'suspicious' : ''}" cx="${n.x}" cy="${n.y}" r="${n.target ? 13 : 9}"><title>TX ${esc(n.id)}; dataset step ${n.time_step}; model score ${n.model_score?.toFixed(6) ?? 'not stored'}; mask ${n.attribution.toFixed(4)}</title></circle><text x="${n.x - 35}" y="${n.y + 26}">${esc(n.id)}</text></g>`).join('')}</g>`;
    $('graph-visible').textContent = `Showing ${nodes.length}/${g.nodes.length} stored nodes and ${edges.length}/${g.edges.length} stored edges. Target is retained even when filters exclude its time/score. Left-to-right depth is path context, not within-step chronology.`;
    svg.querySelectorAll('[data-node]').forEach(b => { const show = () => Workstation.inspectNode(c, b.dataset.node); b.onclick = show; b.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(); } }; });
    svg.querySelectorAll('[data-edge]').forEach(b => b.onclick = () => { const edge = edges[Number(b.dataset.edge)], evidence = (c.outputs.investigation?.evidence || []).filter(e => e.source_record === edge.source + '->' + edge.target); $('graph-inspector').innerHTML = `<h3>Directed source edge</h3><p>${esc(edge.source)} → ${esc(edge.target)} · explanation weight ${edge.attribution.toFixed(4)}</p>${citations(evidence.map(e => e.id))}`; Workstation.bindNavigation(); });
    let scale = 1, x = 0, y = 0, drag = null; const layer = $('graph-layer'), transform = () => layer.setAttribute('transform', `translate(${x},${y}) scale(${scale})`);
    svg.onwheel = e => { e.preventDefault(); scale = Math.max(.5, Math.min(5, scale * (e.deltaY > 0 ? .9 : 1.1))); transform(); };
    svg.onpointerdown = e => { if (e.target.closest('[data-node],[data-edge]')) return; drag = {x:e.clientX, y:e.clientY}; svg.setPointerCapture(e.pointerId); };
    svg.onpointermove = e => { if (drag) { x += (e.clientX - drag.x) * 700 / svg.clientWidth; y += (e.clientY - drag.y) * 345 / svg.clientHeight; drag = {x:e.clientX, y:e.clientY}; transform(); } };
    svg.onpointerup = () => drag = null;
    if (graphFocus && points.has(graphFocus)) { Workstation.inspectNode(c, graphFocus); graphFocus = null; }
  },
  inspectNode(c, id) {
    const n = c.outputs.detection.subgraph.nodes.find(n => n.id === id), m = c.outputs.detection.subgraph.structure?.node_metrics.find(n => n.id === id);
    const ev = (c.outputs.investigation?.evidence || []).filter(e => e.source_record === id);
    $('graph-inspector').innerHTML = `<h3>Transaction ${esc(id)}</h3><p>Dataset time step ${n.time_step} · model score ${n.model_score?.toFixed(6) ?? 'not stored'} · explanation weight ${n.attribution.toFixed(4)}</p><p>Local in/out degree ${m ? m.in_degree + ' / ' + m.out_degree : 'not stored'}</p>${citations(ev.map(e => e.id))}<button class="quiet" data-source-tx="${esc(id)}">Inspect anonymous source attributes</button><div id="source-attributes"></div>`;
    Workstation.bindNavigation();
  },
  execSummary(c) {
    const d = c.outputs?.detection;
    const score = Number.isFinite(d?.score) ? d.score.toFixed(3) : '—';
    const threshold = Number.isFinite(d?.threshold) ? d.threshold.toFixed(3) : '—';
    return `ZEN's graph model assigned the target transaction a model score of ${score}, above the configured investigation threshold of ${threshold}. The transaction was evaluated together with its connected payment-flow network. The model score is a prioritization signal, not a calibrated probability.`;
  },
  sourceLabel(source) {
    const s = String(source ?? '').trim();
    const looksLikePath = /[A-Za-z]:[\\/]/.test(s) || /(^|[\\/])Users[\\/]/i.test(s) || /OneDrive/i.test(s);
    if (!looksLikePath) return s;
    const tail = (s.split(/[\\/]/).filter(Boolean).pop() || '').toLowerCase();
    if (tail.includes('edgelist')) return 'Elliptic benchmark payment-flow record';
    if (tail.includes('features')) return 'Elliptic benchmark transaction record';
    if (tail.includes('elliptic')) return 'Elliptic benchmark record';
    return 'Elliptic benchmark record';
  },
  shortRef(value, n = 12) {
    const s = String(value ?? '');
    return s.length > n + 4 ? s.slice(0, n) + '…' : s;
  },
  reportBody(c) {
    const o = c.outputs || {}, d = o.detection || {}, inv = o.investigation || {}, ev = inv.evidence || [], n = o.narrative || {}, v = o.compliance || {}, enr = c.demo_enrichment || {};
    const score = Number.isFinite(d.score) ? d.score.toFixed(3) : '—';
    const threshold = Number.isFinite(d.threshold) ? d.threshold.toFixed(3) : '—';
    const target = (d.subgraph?.nodes || []).find(x => x.target) || (d.subgraph?.nodes || []).find(x => x.id === d.seed_transaction);
    const summary = Presentation.reviewSummary(c);
    const info = (k, val) => `<tr><th>${esc(k)}</th><td>${esc(val == null || val === '' ? '—' : String(val))}</td></tr>`;
    const list = claims => `<ul>${claims.map(cl => `<li>${esc(cl.text)}${cl.evidence_ids && cl.evidence_ids.length ? ' ' + cl.evidence_ids.map(id => `[${esc(id)}]`).join(' ') : ''}</li>`).join('')}</ul>`;
    const stamp = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
    const s = n.sections || {};
    const activity = s['Activity and chronology'] || [];
    const missing = (s['Missing information and review'] || []).map(cl => ({ text: Judge.qualify(cl.text, c), evidence_ids: cl.evidence_ids }));
    const otherSections = Object.entries(s).filter(([t]) => !['Activity and chronology', 'Missing information and review'].includes(t));
    const k = enr.kyc || {}, san = enr.sanctions || {};
    const kycLine = [k.customer_id, k.country, k.account_type, k.risk_rating && ('risk ' + k.risk_rating)].filter(Boolean).join(' · ');
    const sanLine = [san.screening_result, san.match_status, san.reference, san.screened_at && ('screened ' + san.screened_at)].filter(Boolean).join(' · ');
    const decided = (c.reviews || []).length ? c.reviews.map(r => `${r.decision} by ${r.actor} on ${r.timestamp} (revision ${r.reviewed_revision})`).join('; ') : 'No human decision recorded';
    return `
      <header class="pr-head"><div class="pr-brand">ZEN ◈ MULTI-AGENT AI SYSTEM FOR AML DETECTION AND REPORTING</div><h1>SAR-style Investigation Report</h1><p class="pr-draft">Draft only · Human review required · Not a filed SAR</p><p class="pr-note">Generated ${esc(stamp)} · Case ${esc(c.id)} · Revision ${esc(String(c.revision))}</p></header>
      <section><h2>Case Information</h2><table class="pr-table">${info('Case ID', c.id)}${info('Transaction ID', c.transaction_id)}${info('Revision', c.revision)}${info('Current status', summary.status)}${info('Model score', score)}${info('Alert threshold', threshold)}${info('Connected context', (d.subgraph?.nodes || []).length + ' transactions')}${info('Evidence records', ev.length)}${info('Dataset time step', target?.time_step)}</table></section>
      <section><h2>Executive Summary</h2><p>${esc(this.execSummary(c))}</p></section>
      <section><h2>Why This Case Needs Review</h2><ul>${Presentation.reasons(c).map(r => `<li>${esc(r)}</li>`).join('')}</ul></section>
      <section><h2>Network / Activity Context</h2><p>${esc(inv.patterns?.interpretation || 'Connected transaction context around the scored transaction.')}</p>${activity.length ? `<h3>Activity and chronology</h3>${list(activity)}` : ''}</section>
      <section><h2>Supporting Evidence</h2><table class="pr-table pr-ev"><tr><th>ID</th><th>Fact</th><th>Source / provenance</th></tr>${ev.map(e => `<tr><td>${esc(e.id)}</td><td>${esc(e.fact)}</td><td>${esc(this.sourceLabel(e.source))}<br>Record: ${esc(e.source_record)}<br>Version: ${esc(this.shortRef(e.version))}</td></tr>`).join('') || '<tr><td colspan="3">No evidence records.</td></tr>'}</table></section>
      ${(kycLine || sanLine) ? `<section><h2>Investigation Enrichment <span class="pr-tag">Demo enrichment — synthetic</span></h2><p class="pr-note">Synthetic demonstration enrichment. Not sourced from the Elliptic benchmark or live customer/sanctions systems, and never a detection-model input.</p><table class="pr-table">${kycLine ? info('Demo KYC (synthetic)', kycLine) : ''}${sanLine ? info('Demo sanctions screening (synthetic)', sanLine) : ''}</table><p class="pr-note">Genuine customer identity and live sanctions coverage are unavailable in the Elliptic benchmark.</p></section>` : ''}
      ${missing.length ? `<section><h2>Missing Information &amp; Limitations</h2>${list(missing)}<p class="pr-note">Benchmark limitation: historical, anonymized Elliptic data — no live data, real calendar dates or interpretable monetary amounts. Human review is required.</p></section>` : ''}
      <section><h2>SAR-style Narrative</h2>${n.synthesis ? `<p>${esc(n.synthesis)}</p>` : ''}${otherSections.map(([t, claims]) => `<h3>${esc(t)}</h3>${list(claims)}`).join('')}<p class="pr-note">Provider: ${esc(Presentation.provider(n))}${n.synthesis_status ? ' · ' + esc(n.synthesis_status) : ''}</p></section>
      <section><h2>Compliance / Validation</h2><p>Status: <strong>${esc(v.status || 'pending')}</strong>${v.readiness?.score != null ? ' · Internal prototype checks ' + esc(String(v.readiness.score)) + '/100' : ''}</p>${(v.issues || []).length ? `<ul>${v.issues.map(i => `<li>${esc(i)}</li>`).join('')}</ul>` : '<p>No blocking validation findings.</p>'}<p class="pr-note">Validation checks the investigation, evidence traceability, report grounding and model provenance. SHAP (where shown) is an independent logistic-baseline cross-check, not the detection model. Passing checks does not certify legal compliance.</p></section>
      <section><h2>Human Review Status</h2><table class="pr-table">${info('Review status', summary.status)}${info('Revision', c.revision)}${info('Decision history', decided)}</table><p class="pr-note">The final decision belongs to a human investigator. Approval does not file a SAR.</p></section>
      <section><h2>Provenance / Audit</h2><table class="pr-table">${info('Data kind', c.data_kind)}${info('Detection model', d.model_id)}${info('Benchmark dataset', 'Elliptic Bitcoin benchmark · ' + this.shortRef(d.dataset_fingerprint))}${info('Narrative provider', Presentation.provider(n))}${info('Case created', c.created_at)}${info('Evidence records', ev.length)}</table><p class="pr-note">Full model, dataset and evidence identifiers are retained in <strong>Technical Provenance &amp; Validation</strong> below.</p></section>
      <section class="pr-tech"><h2>Technical Provenance &amp; Validation</h2><p class="pr-note">Secondary technical appendix — retained for traceability; not required to read the report above.</p><table class="pr-table">${info('Model ID', d.model_id)}${info('Benchmark dataset fingerprint', d.dataset_fingerprint)}${info('Alert threshold policy', d.threshold_policy?.scope || d.threshold_policy?.source)}${info('Threshold value', Number.isFinite(d.threshold) ? d.threshold : '—')}${info('Data kind', c.data_kind)}${info('Narrative provider', Presentation.provider(n) + (n.synthesis_status ? ' · ' + n.synthesis_status : ''))}${info('Generation method', n.generation_metadata?.method)}${info('Narrative model (repository-relative)', n.generation_metadata?.model_path)}${info('Validation status', v.status)}${info('Evidence records', ev.length)}</table><h3>Evidence provenance</h3><table class="pr-table pr-tech-table"><tr><th>ID</th><th>Kind</th><th>Record</th><th>Source</th><th>Version</th></tr>${ev.map(e => `<tr><td>${esc(e.id)}</td><td>${esc(e.kind)}</td><td>${esc(e.source_record)}</td><td>${esc(this.sourceLabel(e.source))}</td><td class="pr-hash">${esc(e.version)}</td></tr>`).join('') || '<tr><td colspan="5">No evidence records.</td></tr>'}</table>${(v.claim_validation || []).length ? `<h3>Claim → evidence → source validation</h3><table class="pr-table pr-tech-table"><tr><th>Section</th><th>Status</th><th>Evidence</th><th>Record</th></tr>${v.claim_validation.flatMap(row => (row.sources || []).length ? row.sources.map(src => `<tr><td>${esc(row.section)}</td><td>${esc(row.status)}</td><td>${esc(src.evidence_id || '')}</td><td>${esc(src.record || '')}</td></tr>`) : [`<tr><td>${esc(row.section)}</td><td>${esc(row.status)}</td><td colspan="2">${esc((row.evidence_ids || []).join(' '))}</td></tr>`]).join('')}</table>` : ''}<p class="pr-note">Fingerprints are cryptographic references to the frozen benchmark and model artifacts. No filesystem locations are recorded in this report.</p></section>
      <footer class="pr-footer">Draft only · Not a filed SAR · Human investigator retains final authority.</footer>`;
  },
  exportReport(c) {
    const root = document.getElementById('print-report');
    if (!root) throw new Error('Print view is unavailable in this browser session.');
    root.innerHTML = this.reportBody(c);
    window.print();
  },
  narrative(c, body) {
    const n = c.outputs.narrative, v = c.outputs.compliance;
    if (!n) { body.textContent = 'Narrative unavailable.'; return; }
    const editable = ['awaiting_review','changes_requested'].includes(c.status), evidence = new Map((c.outputs.investigation?.evidence || []).map(e => [e.id, e]));
    const d = c.outputs.detection;
    const score = Number.isFinite(d?.score) ? d.score.toFixed(3) : '—';
    const threshold = Number.isFinite(d?.threshold) ? d.threshold.toFixed(3) : '—';
    const execSummary = this.execSummary(c);
    const claimHtml = (cl, text) => `<div class="claim ${v?.claim_validation?.some(r => r.text === cl.text && r.status === 'unsupported') ? 'unsupported' : ''}">${v?.claim_validation?.some(r => r.text === cl.text && r.status === 'unsupported') ? '<strong>Unsupported claim — evidence required</strong><br>' : ''}${esc(text === undefined ? cl.text : text)} ${citations(cl.evidence_ids)}</div>`;
    // Distinguish genuine reference data from the synthetic demo layer when demo enrichment is present.
    const qualify = text => Judge.qualify(text, c);
    const humanTitles = ['Activity and chronology', 'Missing information and review'];
    const humanSections = Object.entries(n.sections).filter(([t]) => humanTitles.includes(t));
    const techSections = Object.entries(n.sections).filter(([t]) => !humanTitles.includes(t));
    const citedIds = [...new Set(Object.values(n.sections).flat().flatMap(cl => cl.evidence_ids || []))];
    const evList = c.outputs.investigation?.evidence || [];
    const topCited = citedIds.map(id => evidence.get(id)).filter(Boolean).slice(0, 3);
    const topEvidence = topCited.length ? topCited : evList.slice(0, 3);
    const summary = Presentation.reviewSummary(c);
    const enrichSection = Judge.enrichment(c);
    const targetNode = (d?.subgraph?.nodes || []).find(x => x.target) || (d?.subgraph?.nodes || []).find(x => x.id === d?.seed_transaction);
    const snapshot = `<section class="tx-snapshot"><h2>Transaction snapshot</h2><p class="muted">Investigation context: the target transaction is reviewed together with its connected payment-flow context — the transaction network supplies the relationships considered during investigation.</p><div class="snapshot-grid"><div><span>Transaction ID</span><strong>${esc(c.transaction_id)}</strong></div><div><span>Model score</span><strong>${score}</strong></div><div><span>Alert threshold</span><strong>${threshold}</strong></div><div><span>Connected transactions</span><strong>${d?.subgraph?.nodes?.length ?? 0}</strong></div><div><span>Evidence records</span><strong>${evList.length}</strong></div><div><span>Dataset time step</span><strong>${targetNode?.time_step ?? '—'}</strong></div></div></section>`;
    body.innerHTML = `<div class="report">
      <div class="report-head">
        <div class="report-status">${badge('DRAFT · NOT FILED', 'review_ready')} ${badge('HUMAN REVIEW REQUIRED', 'pending')}</div>
        <h1>ZEN Investigation Report</h1>
        <p class="muted">SAR-style draft · Transaction ${esc(c.transaction_id)} · ${esc(Presentation.provider(n))}</p>
      </div>
      <section><h2>Executive summary</h2><p>${esc(execSummary)}</p></section>
      <section><h2>Why this case was flagged</h2><p>The transaction was evaluated together with its connected payment-flow network.</p></section>
      ${enrichSection}
      ${humanSections.map(([title, claims]) => `<section><h2>${esc(title)}</h2>${claims.map(cl => claimHtml(cl, qualify(cl.text))).join('')}</section>`).join('')}
      ${snapshot}
      <section><h2>What supports this case</h2><p class="muted">The draft is grounded in ${citedIds.length} cited evidence record${citedIds.length === 1 ? '' : 's'} (${evList.length} linked in this case). The most relevant are shown below.</p><div class="evidence-rows">${topEvidence.map(e => `<div class="evidence-row"><span class="ev-id">${esc(e.id)}</span><div><p>${esc(qualify(e.fact))}</p><button class="quiet" data-evidence="${esc(e.id)}">Inspect evidence</button></div></div>`).join('') || '<p class="muted">No evidence records.</p>'}</div><button class="quiet" data-evidence-all>View all ${evList.length} evidence records →</button>${(v?.issues || []).map(i => `<p class="warning">${esc(i)}</p>`).join('')}</section>
      <section class="review-section"><h2>${esc(summary.title)}</h2><p>ZEN has prepared the case and SAR-style narrative. The final decision belongs to the human investigator.</p><p class="review-status-line">Current status: ${badge(summary.status, c.status)}</p><button class="primary" data-jump="review">Review &amp; Audit →</button></section>
      ${Judge.disclosure('Technical report details', `${techSections.map(([title, claims]) => `<h3>${esc(title)}</h3>${claims.map(claimHtml).join('')}`).join('')}${jsonDetails('Generated interpretation', {synthesis: n.synthesis, synthesis_status: n.synthesis_status, synthesis_evidence_ids: v?.synthesis_evidence_ids || []})}${jsonDetails('Detection provenance', {model_id: d?.model_id, dataset_fingerprint: d?.dataset_fingerprint, threshold_policy: d?.threshold_policy})}${jsonDetails('Generation provenance', n.generation_metadata || {})}${jsonDetails('Revision provenance', n.revision_metadata || {})}${jsonDetails('Claim → evidence → source validation', v?.claim_validation || [])}<p><button id="load-history" class="quiet">Compare saved narrative revisions</button></p><div id="narrative-history"></div>`, experienceMode === 'technical')}
      ${Judge.disclosure('Edit claims with supporting evidence', `<p class="muted">Save creates a new revision and reruns backend validation. Exact cited facts remain required. Original generation provenance is server-owned.</p><div id="claim-editor">${Object.entries(n.sections).map(([title, claims], si) => `<h3>${esc(title)}</h3>${claims.map((cl, ci) => `<div class="claim-edit"><label>Claim ${si+1}.${ci+1}<textarea data-section-index="${si}" data-claim-index="${ci}" ${!editable ? 'disabled' : ''}>${esc(cl.text)}</textarea></label><label>Evidence IDs (comma separated)<input data-cite-section="${si}" data-cite-claim="${ci}" value="${esc(cl.evidence_ids.join(', '))}" ${!editable ? 'disabled' : ''}></label><p class="source">Supporting facts: ${cl.evidence_ids.map(id => esc(id + ': ' + (evidence.get(id)?.fact || 'MISSING EVIDENCE'))).join('<br>')}</p><p class="${v?.claim_validation?.some(row => row.section === title && row.text === cl.text && row.status === 'unsupported') ? 'warning' : 'muted'}">${v?.claim_validation?.find(row => row.section === title && row.text === cl.text)?.status || 'not validated'}</p></div>`).join('')}`).join('')}</div><label>Summary text (optional, exact cited one/two-fact text only)<textarea id="summary-edit" ${!editable ? 'disabled' : ''}>${esc(n.synthesis || '')}</textarea></label><p id="edit-state" class="muted">Saved revision ${c.revision}</p><button id="save-claims" ${!editable ? 'disabled' : ''}>Save claims &amp; revalidate</button>`, false)}
      ${Judge.disclosure('Advanced structured draft editor', `<textarea id="draft-edit" style="min-height:200px" aria-label="Structured draft JSON" ${!editable ? 'disabled' : ''}>${esc(JSON.stringify(n, null, 2))}</textarea><button id="save-draft" ${!editable ? 'disabled' : ''}>Save JSON revision &amp; validate</button>`, false)}
    </div>`;
    const save = async revised => { const buttons = [$('save-claims'), $('save-draft')]; buttons.forEach(b => { if (b) b.disabled = true; }); $('edit-state').textContent = 'Saving revision and validating…'; try { await api(`/cases/${c.id}/narrative`, {method:'PUT', body:JSON.stringify({expected_revision:c.revision, narrative:revised})}); await refresh(); } catch(e) { error(e); if ($('edit-state')) $('edit-state').textContent = 'Save failed — edits remain unsaved'; } finally { buttons.forEach(b => { if (b) b.disabled = !editable; }); } };
    body.querySelectorAll('#claim-editor textarea,#claim-editor input,#summary-edit').forEach(input => input.oninput = () => { $('edit-state').textContent = 'Unsaved edits — not yet validated'; });
    if ($('save-claims')) $('save-claims').onclick = () => { const revised = JSON.parse(JSON.stringify(n)), titles = Object.keys(n.sections); body.querySelectorAll('[data-section-index]').forEach(el => { revised.sections[titles[Number(el.dataset.sectionIndex)]][Number(el.dataset.claimIndex)].text = el.value; }); body.querySelectorAll('[data-cite-section]').forEach(el => { revised.sections[titles[Number(el.dataset.citeSection)]][Number(el.dataset.citeClaim)].evidence_ids = el.value.split(',').map(s => s.trim()).filter(Boolean); }); revised.synthesis = $('summary-edit').value.trim() || null; save(revised); };
    if ($('save-draft')) $('save-draft').onclick = () => { try { save(JSON.parse($('draft-edit').value)); } catch(e) { error(e); } };
    if ($('load-history')) $('load-history').onclick = async () => { try { const history = await api(`/cases/${c.id}/narrative-history`); if (selected?.id !== c.id || activeTab !== 'evidence') return; const last = history.slice(-2); $('narrative-history').innerHTML = `<p class="muted">${history.length} distinct saved narrative revision(s).</p><div class="two-col">${last.map(r => `<div class="mini"><h3>Revision ${r.revision}</h3><p class="source">${esc(r.actor)} · ${esc(r.timestamp)}<br>${esc(r.narrative_hash)}</p>${Object.entries(r.narrative.sections).map(([title, claims]) => `<h3>${esc(title)}</h3>${claims.map(cl => `<p>${esc(cl.text)} [${cl.evidence_ids.map(esc).join(', ')}]</p>`).join('')}`).join('')}</div>`).join('')}</div>`; } catch(e) { error(e); } };
  },
  bindNavigation() {
    document.querySelectorAll('[data-jump]').forEach(b => b.onclick = () => { activeTab = b.dataset.jump; renderDetail().catch(error); });
    document.querySelectorAll('[data-evidence]').forEach(b => b.onclick = async () => { try { const id = b.dataset.evidence; activeTab = 'evidence'; await renderDetail(); $('evidence-filter').value = id; $('evidence-filter').dispatchEvent(new Event('input')); document.getElementById('evidence-' + id)?.scrollIntoView({block:'center'}); } catch(e) { error(e); } });
    document.querySelectorAll('[data-show-node]').forEach(b => b.onclick = () => { graphFocus = b.dataset.showNode; activeTab = 'network'; renderDetail().catch(error); });
    document.querySelectorAll('[data-source-tx]').forEach(b => b.onclick = async () => { try { const id = b.dataset.sourceTx, caseId = selected.id, result = await api(`/cases/${caseId}/transactions/${encodeURIComponent(id)}`); if (selected?.id !== caseId || activeTab !== 'network') return; const target = $('source-attributes'); if (target) target.innerHTML = `<h3>Source transaction ${esc(id)} · dataset step ${result.time_step}</h3><p class="muted">${esc(result.limitation)}</p>${jsonDetails('165 source attributes; first 93 are model inputs', result)}`; } catch(e) { error(e); } });
    document.querySelectorAll('[data-open-disclosure]').forEach(b => b.onclick = () => { const label = b.dataset.openDisclosure; const summary = [...document.querySelectorAll('.disclosure > summary')].find(s => (s.textContent || '').trim() === label); if (summary) { const d = summary.closest('details'); d.open = true; d.scrollIntoView({block:'center', behavior:'smooth'}); } });
    document.querySelectorAll('[data-evidence-all]').forEach(b => b.onclick = () => { const f = $('evidence-filter'); if (f) { f.value = ''; f.dispatchEvent(new Event('input')); } const t = $('evidence-mount'); if (t && typeof t.scrollIntoView === 'function') t.scrollIntoView({block:'start', behavior:'smooth'}); });
  },
  operatingExplorer(report) {
    if (!report) return;
    $('evaluation').insertAdjacentHTML('beforeend', `<h3>Validation operating-point explorer</h3><p class="muted">Exploration only; changing this control does not change stored cases or deploy a threshold. Actual new-case overrides use AML_DETECTION_THRESHOLD and retain policy provenance. Triage priority has separate cutoffs.</p><div class="filter-grid"><label>Model<select id="op-model"><option value="gat">GAT</option><option value="baseline">Logistic baseline</option></select></label><label>Validation objective<select id="op-objective"><option value="recall_emphasis">Recall emphasis / F2</option><option value="balanced">Balanced / F1</option><option value="precision_emphasis">Precision emphasis / F0.5</option></select></label><label>Explore threshold<input type="range" id="op-threshold" min="0.05" max="0.95" step="0.01" value="${report.default_threshold}"></label></div><div id="op-results"></div><div id="calibration-results"></div>`);
    const update = () => { const model = $('op-model').value, data = report.models[model], threshold = Number($('op-threshold').value), r = data.thresholds.reduce((a,b) => Math.abs(a.threshold - threshold) < Math.abs(b.threshold - threshold) ? a : b); $('op-results').innerHTML = `<p>Validation threshold <strong>${r.threshold.toFixed(2)}</strong> · ${r.alerts} model alerts</p><table><tr><th>Precision</th><th>Recall</th><th>F0.5</th><th>F1</th><th>F2</th><th>FP</th><th>FN</th></tr><tr>${['precision','recall','f0_5','f1','f2','fp','fn'].map(k => `<td>${k === 'fp' || k === 'fn' ? r[k] : r[k].toFixed(4)}</td>`).join('')}</tr></table><svg class="threshold-chart" viewBox="0 0 600 200" role="img" aria-label="Validation precision recall and F2 versus threshold"><path d="M35 10 V170 H580" fill="none" stroke="#41577a"/>${[['precision','#e2a24f'],['recall','#43c9a4'],['f2','#5b8def']].map(([k,color]) => `<polyline fill="none" stroke="${color}" stroke-width="2" points="${data.thresholds.map(row => `${35 + row.threshold * 540},${170 - row[k] * 150}`).join(' ')}"/>`).join('')}<line x1="${35 + r.threshold * 540}" x2="${35 + r.threshold * 540}" y1="10" y2="170" stroke="#ffffff" stroke-dasharray="4"/><text x="40" y="192" fill="#8ea2ba">Threshold 0.05 → 0.95 · amber precision · green recall · blue F2</text></svg>${jsonDetails('All validation thresholds / FP and FN trade-offs', data.thresholds)}`;
      const cal = data.calibration; $('calibration-results').innerHTML = cal.status === 'diagnostic_only' ? `<h3>Calibration · NOT DEPLOYED · REUSED VALIDATION DIAGNOSTIC</h3><p class="muted">${esc(cal.limitation)}</p><table><tr><th>Method</th><th>Brier ↓</th><th>Log loss ↓</th><th>10-bin ECE ↓</th></tr>${['raw','sigmoid','isotonic'].map(k => `<tr><td>${k}</td><td>${cal[k].brier.toFixed(4)}</td><td>${cal[k].log_loss.toFixed(4)}</td><td>${cal[k].ece_10_equal_width.toFixed(4)}</td></tr>`).join('')}</table><p class="muted">Fit steps 30–32; assessment 33–34. Brier reflects calibration and discrimination. No probability-of-laundering claim.</p>${jsonDetails('Reliability bins and fitted parameters', cal)}${'<p class="muted">Fixed-weight graph intervention: sensitivity to explicit edges; not a retrained no-graph baseline or causal proof.</p>' + jsonDetails('Fixed-weight graph intervention', report.topology_intervention)}` : 'Calibration diagnostic unavailable: insufficient classes.'; };
    const objective = () => { $('op-threshold').value = report.models[$('op-model').value].operating_points[$('op-objective').value].threshold; update(); };
    $('op-model').onchange = objective; $('op-objective').onchange = objective; $('op-threshold').oninput = update; objective();
  }
};

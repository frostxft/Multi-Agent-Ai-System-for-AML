'use strict';
const Judge = {
  disclosure(title, html, open = false) {
    return `<details class="disclosure" ${open ? 'open' : ''}><summary>${esc(title)}</summary><div class="inner">${html}</div></details>`;
  },
  facts(c) { return (c.outputs.investigation?.evidence || []).filter(e => ['benchmark','synthetic_test','unverified_input'].includes(e.kind)); },
  qualify(text, c) {
    if (!c?.demo_enrichment) return text;
    if (/KYC are unavailable/i.test(text)) return `${text} (Genuine reference data only — the synthetic demo KYC shown for this case is illustrative.)`;
    if (/sanctions reference or screening result is available/i.test(text)) return `${text} (Live coverage only — the synthetic demo screening shown for this case is illustrative.)`;
    return text;
  },
  enrichment(c) {
    const enr = c.demo_enrichment;
    if (!enr) return '';
    const k = enr.kyc || {}, s = enr.sanctions || {};
    return `<div class="section-title"><h2>Investigation enrichment</h2><span class="sub">DEMO / SYNTHETIC · not a detection-model input</span></div>
      <div class="enrich-grid">
        <div class="enrich-card"><span class="enrich-tag">DEMO KYC</span><h4>${esc(k.customer_id || '—')}</h4>
          <div class="metric-row"><span>Country</span><strong>${esc(k.country || '—')}</strong></div>
          <div class="metric-row"><span>Account type</span><strong>${esc(k.account_type || '—')}</strong></div>
          <div class="metric-row"><span>Risk attribute</span><strong>${esc(k.risk_rating || '—')}</strong></div>
        </div>
        <div class="enrich-card"><span class="enrich-tag">DEMO SANCTIONS SCREENING</span><h4>${esc(s.match_status || '—')}</h4>
          <div class="metric-row"><span>Screening result</span><strong>${esc(s.screening_result || '—')}</strong></div>
          <div class="metric-row"><span>Reference</span><strong>${esc(s.reference || '—')}</strong></div>
          <div class="metric-row"><span>Screened at</span><strong>${esc(s.screened_at || '—')}</strong></div>
        </div>
      </div>
      <p class="muted"><strong>Demo enrichment — available (synthetic).</strong> Genuine customer KYC and live sanctions coverage — unavailable and not represented here. This enrichment is not a detection-model input and not part of benchmark evidence.</p>`;
  },
  timeline(c) {
    const o = c.outputs, ev = o.investigation?.evidence || [];
    const failedStage = c.error?.stage;
    const stages = [
      {key:'detection', label:'Detection', note:'Transaction scored and explained', done: !!o.detection},
      {key:'explanation', label:'Explanation', note:'Graph explanation generated', done: !!(o.detection?.explanation && o.detection.explanation.status === 'available')},
      {key:'investigation', label:'Evidence', note:'Source records collected', done: ev.length > 0},
      {key:'investigation', label:'Investigation', note:'Dossier assembled', done: !!o.investigation},
      {key:'narrative', label:'Draft report', note:'Report prepared', done: !!o.narrative},
      {key:'compliance', label:'Validation', note:'Consistency checked', done: !!o.compliance}
    ];
    const decision = ['approved','rejected'].includes(c.status);
    return `<div class="timeline">
      ${stages.map(s => { const state = s.done ? 'done' : (failedStage === s.key ? 'failed' : 'pending'); return `<div class="tl-item ${state}"><div class="tl-dot">${s.done ? '✓' : (failedStage === s.key ? '!' : '·')}</div><div class="tl-body"><div class="tl-title">${s.label}</div><div class="tl-note">${s.done ? s.note : (failedStage === s.key ? 'Stage failed' : 'Not completed')}</div></div></div>`; }).join('')}
      <div class="tl-item current"><div class="tl-dot">${decision ? '✓' : '→'}</div><div class="tl-body"><div class="tl-title">Human decision</div><div class="tl-note">${decision ? 'Decision recorded' : 'Required — an investigator makes the final decision'}</div></div></div>
    </div>`;
  },
  overview(c, body) {
    const o = c.outputs, d = o.detection, ev = o.investigation?.evidence || [];
    const n = o.narrative;
    const score = Number.isFinite(d?.score) ? d.score.toFixed(3) : '—';
    const threshold = Number.isFinite(d?.threshold) ? d.threshold.toFixed(3) : '—';
    const above = (d?.subgraph?.nodes || []).filter(x => !x.target && Number.isFinite(x.model_score) && x.model_score >= d.threshold).length;
    body.innerHTML = `
      <div class="finding-grid">
        <section class="finding-card"><span class="eyebrow">What ZEN found</span><h3>High model score</h3><p>The target transaction received a model score of <strong>${score}</strong>, above the investigation threshold of ${threshold}.</p></section>
        <section class="finding-card"><span class="eyebrow">Why it was flagged</span><h3>Network-level evaluation</h3><p>The model evaluated the transaction together with its connected payment-flow network${above ? ` — <strong>${above} additional connected transaction${above === 1 ? '' : 's'}</strong> also exceed the threshold` : ''}.</p></section>
        <section class="finding-card"><span class="eyebrow">What supports the case</span><h3>${ev.length} evidence records</h3><p>Source-linked records are available for investigation.</p></section>
      </div>
      <div class="action-row">
        <button class="primary" data-jump="review">Review investigation</button>
        <button class="quiet" data-jump="network">Explore the network</button>
      </div>
      ${Judge.enrichment(c)}
      <div class="section-title"><h2>Investigation progress</h2><span class="sub">Automated stages · human decision last</span></div>
      ${Judge.timeline(c)}
      <div class="section-title"><h2>SAR narrative</h2><span class="sub">Draft · human review required · not a filed SAR</span></div>
      <div class="report-preview">
        <div class="rp-head">
          <div class="rp-status">${badge('DRAFT · HUMAN REVIEW REQUIRED', 'medium')}</div>
          <h3>ZEN Investigation Report</h3>
          <p class="muted">Transaction ${esc(c.transaction_id)}</p>
        </div>
        <div class="rp-kpis">
          <div class="kpi"><div class="kpi-label">Model score</div><div class="kpi-value">${score}</div></div>
          <div class="kpi"><div class="kpi-label">Alert threshold</div><div class="kpi-value">${threshold}</div></div>
          <div class="kpi"><div class="kpi-label">Evidence</div><div class="kpi-value">${ev.length} records</div></div>
        </div>
        <h4>Executive summary</h4>
        <p>ZEN identified this transaction as an investigation candidate based on its graph-model score and surrounding payment-flow context.</p>
        <p>The target transaction received a model score of <strong>${score}</strong>, above the configured investigation threshold of ${threshold}.</p>
        <p class="rp-note">Model score is a prioritization signal, not a calibrated probability.</p>
        <h4>What ZEN prepared</h4>
        <p>An evidence-grounded investigation draft is ready for human review.</p>
        <button class="primary" data-jump="evidence">Review draft →</button>
        ${Judge.disclosure('Technical details', `${jsonDetails('Case context', {case_id: c.id, transaction_id: c.transaction_id})}${n ? jsonDetails('Generated summary (provider: ' + Presentation.provider(n) + ')', {provider: n.provider, synthesis: n.synthesis, synthesis_status: n.synthesis_status, synthesis_evidence_ids: o.compliance?.synthesis_evidence_ids || []}) : ''}${jsonDetails('Detection provenance', {model_id: d?.model_id, dataset_fingerprint: d?.dataset_fingerprint, threshold_policy: d?.threshold_policy})}${jsonDetails('Measured stage times (seconds)', c.timings)}`, experienceMode === 'technical')}
      </div>`;
  },
  networkExplanation(c, body) {
    const d = c.outputs.detection, e = d?.explanation;
    body.innerHTML = `
      <div class="section-title"><h2>Why did ZEN focus here?</h2></div>
      <div class="concept"><p>ZEN highlights the selected transaction and the connected activity that contributed to its investigation priority. Highlighted relationships show where the detection placed more importance — it does not prove wrongdoing.</p></div>
      <div class="section-title"><h2>Transaction network</h2><span class="sub">Target · connected high-score · other context</span></div>
      <div id="network-mount"></div>
      ${e ? `
      <div class="section-title"><h2>What influenced this case</h2><span class="sub">Where the detection focused</span></div>
      <div class="focus-grid">
        <div class="focus-card"><h3>✓ Local transaction network</h3><p>The target transaction evaluated together with its surrounding payment-flow network.</p></div>
        <div class="focus-card"><h3>✓ Important transaction relationships</h3><p>The relationships that mattered most to the local explanation.</p></div>
        <div class="focus-card"><h3>✓ Anonymized model input signals</h3><p>Anonymized benchmark features also influence the model.</p></div>
      </div>
      <p class="muted">Because the Elliptic benchmark uses anonymized features, individual feature IDs do not have human-readable financial meanings.</p>
      <div class="section-title"><h2>Network relationships</h2><span class="sub">Explanation weight, not confidence or proof</span></div>
      <div id="edges-mount"></div>
      <button class="quiet" data-open-disclosure="Technical GNNExplainer details">View technical explanation</button>
      ${Judge.disclosure('Technical GNNExplainer details', `<div id="gnn-mount"></div>`, experienceMode === 'technical')}
      <div class="section-title"><h2>Independent model cross-check</h2></div>
      <div id="shap-mount"></div>`
      : '<p class="muted">No model explanation is available for this case.</p>'}
      ${Judge.enrichment(c)}
      <p class="muted" style="margin-top:12px">Model scores are not calibrated probabilities. Model attribution is not causal or legal evidence.</p>`;
    Workstation.network(c, $('network-mount'));
    if (e) {
      $('edges-mount').innerHTML = `<div class="edge-list">${[...e.edges].sort((a,b) => b.attribution - a.attribution).slice(0,5).map((edge,i) => `<div class="edge-card"><span class="rank">${i+1}</span><div><strong>Transaction ${esc(edge.source)} → ${esc(edge.target)}</strong><p>Explanation weight ${edge.attribution.toFixed(4)}${edge.attribution === 0 ? ' · no positive weight' : ''}</p>${citations((c.outputs.investigation?.evidence || []).filter(v => v.source_record === edge.source + '->' + edge.target).map(v => v.id))}<button class="quiet" data-show-node="${esc(edge.target)}">View in network</button></div></div>`).join('')}</div>`;
      const sigTop = [...e.features].sort((a,b) => b.attribution - a.attribution).slice(0,10);
      const sigMax = Math.max(...sigTop.map(f => f.attribution), 1e-9);
      $('gnn-mount').innerHTML = `<p class="muted"><strong>${esc(e.method)}</strong> · ${e.epochs} optimization steps</p>
        <h4>Anonymized input signals (raw feature weights)</h4>
        <div class="shap-bars">${sigTop.map(f => `<div class="shap-row"><span class="shap-name">${esc(f.name.replace('local_feature_','Feature '))}</span><div class="shap-track"><div class="shap-bar pos" style="width:${(f.attribution / sigMax * 100).toFixed(1)}%"></div></div><span class="shap-val">${f.attribution.toFixed(4)}</span></div>`).join('')}</div>
        <p class="muted">These feature identifiers come from the anonymized Elliptic benchmark and do not have human-readable financial meanings.</p>
        <h4>Fixed-weight explanation intervention</h4>
        <p class="muted">Original score ${d.score.toFixed(6)}; after removing top five edges ${e.fidelity.top5_edges_removed_score.toFixed(6)}; score drop ${e.fidelity.score_drop.toFixed(6)}. Not a causal or retrained-baseline test.</p>
        ${jsonDetails('Full masks, configuration and limitations', e)}`;
      const shap = e.baseline_shap || {features: [], explains: ''};
      const shapTop = [...(shap.features || [])].sort((a,b) => Math.abs(b.value) - Math.abs(a.value)).slice(0,8);
      const maxAbs = Math.max(...shapTop.map(f => Math.abs(f.value)), 1e-9);
      $('shap-mount').innerHTML = `<div class="crosscheck"><div class="cc-top"><span class="cc-check">✓</span><div><h3>Cross-check available</h3><p>An independent, simpler logistic baseline is cross-checked; its anonymized input signals are listed under the technical details.</p></div></div><div class="cc-labels"><div class="cc-label pos"><span>Explains</span><strong>Logistic baseline</strong></div><div class="cc-label neg"><span>Does not explain</span><strong>Detection model</strong></div></div>${Judge.disclosure('View SHAP details', `<p class="muted">${esc(shap.explains)}</p>${shapTop.length ? `<div class="shap-bars">${shapTop.map(f => { const w = (Math.abs(f.value) / maxAbs) * 100; const pos = f.value >= 0; return `<div class="shap-row"><span class="shap-name">${esc(f.name.replace('local_feature_','Feature '))}</span><div class="shap-track"><div class="shap-bar ${pos ? 'pos' : 'neg'}" style="width:${w}%"></div></div><span class="shap-val">${pos ? '+' + f.value.toFixed(3) : f.value.toFixed(3)}</span></div>`; }).join('')}</div>` : '<p class="muted">No baseline feature values recorded.</p>'}<p class="muted">Positive values push the baseline score upward; negative push it downward. Anonymous features; no inferred amount, identity or transaction behavior.</p>`)}</div>`;
    }
  },
  evidenceReport(c, body) {
    const ev = c.outputs.investigation?.evidence || [];
    body.innerHTML = `
      <div class="section-title"><h2>Evidence</h2><span class="sub">Why should I believe this case?</span></div>
      <label for="evidence-filter">Search evidence</label><input id="evidence-filter" placeholder="Evidence ID, transaction or fact">
      <div id="evidence-mount"></div>
      <div class="section-title" style="margin-top:26px"><h2>SAR narrative</h2><span class="sub">Draft · human review required · not a filed SAR</span><button class="quiet" id="export-sar" type="button">Export SAR-style Report</button></div>
      <div id="report-mount"></div>`;
    const render = (q = '') => { $('evidence-mount').innerHTML = ev.filter(e => (e.id + ' ' + e.fact + ' ' + e.source_record).toLowerCase().includes(q.toLowerCase())).map(e => `<article class="evidence" id="evidence-${esc(e.id)}">
        <div class="ev-head"><h3>${esc(e.id)}</h3>${badge(Presentation.kind(e.kind), e.kind === 'benchmark' ? 'review_ready' : '')}</div>
        <p class="evidence-fact">${esc(Judge.qualify(e.fact, c))}</p>
        <p class="ev-meta">Source: ${esc(e.kind === 'benchmark' ? (e.source_record.includes('->') ? 'payment-flow record' : 'transaction record') : e.source)} · Record ${esc(e.source_record)}</p>
        <div class="ev-actions">${Judge.disclosure('View source &amp; provenance', `<p class="source">Source: ${esc(e.source)}<br>Record: ${esc(e.source_record)}<br>Version: ${esc(e.version)}</p>`)}${(c.outputs.detection?.subgraph.nodes || []).filter(n => e.source_record === n.id || e.source_record.split('->').includes(n.id)).map(n => `<button class="quiet" data-show-node="${esc(n.id)}">View transaction ${esc(n.id)} in network</button>`).join('')}</div>
      </article>`).join('') || '<p class="muted">No matching evidence.</p>'; Workstation.bindNavigation(); };
    render();
    $('evidence-filter').oninput = e => render(e.target.value);
    Workstation.narrative(c, $('report-mount'));
    const exportBtn = $('export-sar');
    if (exportBtn) {
      const restore = () => { const b = $('export-sar'); if (b) { b.disabled = false; b.textContent = 'Export SAR-style Report'; } };
      exportBtn.onclick = () => { exportBtn.disabled = true; exportBtn.textContent = 'Preparing report…'; try { Workstation.exportReport(c); } catch(e) { error(e); restore(); return; } setTimeout(restore, 1500); };
    }
  },
  reviewAudit(c, body, audit) {
    const v = c.outputs.compliance;
    const decided = ['approved','rejected'].includes(c.status);
    const canReview = ['awaiting_review','changes_requested'].includes(c.status) && health?.role === 'reviewer';
    const lastReview = c.reviews.length ? c.reviews[c.reviews.length - 1] : null;
    const vsRow = (label, ok, note) => `<div class="vs-item"><div class="vs-head"><span>${label}</span><span class="${ok ? 'ok' : 'bad'}">${ok ? '✓' : 'Needs attention'}</span></div><p>${note}</p></div>`;
    const identityNote = c.demo_enrichment
      ? 'Genuine customer identity and live sanctions data are unavailable in the Elliptic benchmark; synthetic demo enrichment is available separately for this prototype.'
      : 'Genuine customer identity, KYC and live sanctions data are unavailable in the Elliptic benchmark.';
    const factorList = (v?.readiness?.factors || []).length
      ? v.readiness.factors.map(f => `<p><strong>${esc(f.name.replaceAll('_',' '))}: ${f.satisfied ? 'Yes' : 'No'}</strong> · Weight ${f.weight}<br>${esc(f.reason)}</p>`).join('')
      : Object.entries(v?.readiness?.checks || {}).map(([k, val]) => `<p><strong>${esc(k.replaceAll('_',' '))}: ${val ? 'Yes' : 'No'}</strong></p>`).join('');
    body.innerHTML = `
      ${Judge.enrichment(c)}
      <div class="section-title"><h2>Compliance</h2><span class="sub">ZEN validates the investigation, evidence traceability, report grounding and model provenance before human review.</span></div>
      ${v ? `<div class="validation-status">
        ${vsRow('Explanation available', v.readiness.checks.explanation_available, 'A local graph explanation exists for this case.')}
        ${vsRow('Evidence traceable', v.readiness.checks.evidence_traceable, 'Evidence records carry source references and versions.')}
        ${vsRow('Report validated', v.readiness.checks.narrative_consistent, 'Draft claims are checked against the cited evidence.')}
        ${vsRow('Model provenance recorded', v.readiness.checks.model_versioned, 'The model checkpoint identity accompanies the score.')}
        <div class="vs-item"><div class="vs-head"><span>Benchmark limitations</span><span class="lim">Noted</span></div><p>Historical, anonymized Elliptic benchmark — no live data, real calendar dates or interpretable monetary amounts.</p></div>
        ${vsRow('Human review required', v.readiness.checks.human_review_required, 'A human investigator makes the final decision; approval does not file a SAR.')}
        <div class="vs-item"><div class="vs-head"><span>Genuine customer identity &amp; live sanctions data</span><span class="lim">Unavailable in benchmark</span></div><p>${esc(identityNote)}</p></div>
      </div>
        ${v.issues.map(i => `<p class="warning">${esc(i)}</p>`).join('')}
        <p class="muted">Passing these checks does not certify legal or regulatory compliance.</p>
        ${Judge.disclosure('Technical validation details', `<h4>Internal prototype checks: ${v.readiness.score}/100</h4><p class="muted">Engineering readiness indicators only — not a regulatory standard.</p><p class="muted">${esc(v.readiness.basis)}</p>${factorList}${jsonDetails('Raw validation checklist, source checks and claim validation', v)}`, experienceMode === 'technical')}`
        : '<p class="muted">Readiness has not been established.</p>'}
      <div class="section-title"><h2>Human review</h2></div>
      <div class="review-cta">
        <div class="big">AI prepares the case. A human investigator makes the final decision.</div>
        ${decided
          ? `<div class="decision-recorded"><div class="dr-head"><span class="ok">✓</span> Decision recorded — ${c.status === 'approved' ? 'Approved' : 'Rejected'}</div>${lastReview ? `<p>${esc(lastReview.actor)} · ${esc(lastReview.timestamp)} · reviewed revision ${esc(String(lastReview.reviewed_revision))}</p>` : ''}<p class="muted">This decision is preserved in the audit trail. Review actions are locked for the decided revision; a reviewer can reopen the case to return it to review without altering the recorded decision. Approval records an internal prototype disposition; it does not file a SAR.</p>${health?.role === 'reviewer' ? `<div class="reopen-box"><label for="reopen-reason">Reason for reopening (required, at least 3 characters)</label><textarea id="reopen-reason" rows="2" placeholder="Explain why this decided case is being returned to review."></textarea><button class="secondary" id="reopen-btn">Reopen for review</button></div>` : ''}</div>`
          : canReview
            ? `<p>Reviewing revision ${c.revision} · ${esc(Presentation.review(c))}</p><p class="muted">Decisions are persisted against this case revision. Approval records an internal prototype disposition; it does not file a SAR.</p><label for="review-notes" style="display:block;margin-top:10px">Investigator notes (required, at least 3 characters)</label><textarea id="review-notes" rows="4" placeholder="Record your reasoning, limitations considered and requested action."></textarea><div class="review-actions"><button class="approve" data-decision="approve" ${v?.issues.length ? 'disabled' : ''}>Approve</button><button class="secondary" data-decision="request_changes">Request changes</button><button class="danger" data-decision="reject">Reject</button></div>${v?.issues.length ? '<p class="warning">Open compliance findings block approval; request changes or reject remain available.</p>' : ''}`
            : `<p>Reviewing revision ${c.revision} · ${esc(Presentation.review(c))}</p><p class="warning">${health?.role === 'reviewer' ? 'This case is not currently open for review.' : 'A reviewer role is required to record a decision.'}</p>`}
        <h3>Decision history</h3>
        ${c.reviews.length ? c.reviews.map(r => `<div class="mini">${badge(r.decision)}<p>${esc(r.notes)}</p><small>${esc(r.actor)} · ${esc(r.timestamp)} · revision ${r.reviewed_revision}</small></div>`).join('') : '<p class="muted">No human decision has been recorded.</p>'}
      </div>
      <div class="section-title"><h2>Audit trail</h2></div>
      ${audit ? `<p class="muted">${badge(audit.valid ? 'integrity verified' : 'integrity failure', audit.valid ? 'review_ready' : 'failed')} ${esc(audit.limitation)}</p>
        ${audit.events.map(e => `<div class="audit"><strong>${esc(Presentation.event(e))}</strong><p>${esc(e.actor)} · Revision ${e.revision}</p><small>${esc(e.timestamp)}</small>${jsonDetails('Event details and hashes', e)}</div>`).join('')}`
        : '<p class="muted">Audit unavailable.</p>'}`;
    document.querySelectorAll('[data-decision]').forEach(b => b.onclick = async () => {
      const notes = $('review-notes') ? $('review-notes').value : '';
      if (notes.trim().length < 3) { error(new Error('Investigator notes (at least 3 non-whitespace characters) are required before recording a decision.')); return; }
      try { await api(`/cases/${c.id}/review`, {method:'POST', body:JSON.stringify({decision:b.dataset.decision, notes, expected_revision:c.revision})}); await refresh(); } catch(e) { error(e); }
    });
    if ($('reopen-btn')) $('reopen-btn').onclick = async () => {
      const reason = $('reopen-reason') ? $('reopen-reason').value : '';
      if (reason.trim().length < 3) { error(new Error('A reopen reason (at least 3 non-whitespace characters) is required.')); return; }
      try { await api(`/cases/${c.id}/reopen`, {method:'POST', body:JSON.stringify({reason, expected_revision:c.revision})}); await refresh(); } catch(e) { error(e); }
    };
  }
};

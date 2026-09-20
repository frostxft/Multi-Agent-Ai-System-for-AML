'use strict';
// Pure presentation decisions, tested without a browser. Never changes case facts.
const Presentation = {
  review(c) {
    if (c.status === 'approved') return 'Approved by reviewer';
    if (c.status === 'rejected') return 'Rejected by reviewer';
    if (c.error || c.status === 'failed') return 'Stage needs attention';
    const state=c.outputs?.compliance?.status ?? c.compliance_status;
    const issues=c.outputs?.compliance?.issues?.length ?? c.blocking_findings ?? 0;
    if (issues || state==='issues_found') return 'Blocked — findings to resolve';
    if (c.status==='changes_requested') return 'Changes requested';
    return state==='review_ready' && c.status==='awaiting_review' ? 'Ready for human review' : 'Awaiting validation';
  },
  provider(n) {
    return ({local:'Local model · constrained summary',extractive:'Deterministic extractive mode',ollama:'Ollama · configured provider'})[n?.provider] || 'Generation pending';
  },
  kind(kind) {
    return ({benchmark:'FACT',synthetic_test:'SYNTHETIC DEMO DATA',model_output:'MODEL OUTPUT',derived_value:'DERIVED ANALYSIS',missing_information:'MISSING CONTEXT',unverified_input:'UNVERIFIED INPUT'})[kind] || kind;
  },
  statusLabel(status) {
    return ({awaiting_review:'Awaiting human review',changes_requested:'Changes requested',approved:'Approved',rejected:'Rejected',failed:'Stage failed',processing:'Processing'})[status] || String(status ?? '').replaceAll('_',' ');
  },
  reviewSummary(c) {
    const issues = c.outputs?.compliance?.issues?.length ?? c.blocking_findings ?? 0;
    const state = c.outputs?.compliance?.status ?? c.compliance_status;
    if (c.status === 'approved') return { title: 'Human review completed', status: 'Approved' };
    if (c.status === 'rejected') return { title: 'Human review completed', status: 'Rejected' };
    if (c.error || c.status === 'failed') return { title: 'Stage needs attention', status: 'Stage failed' };
    if (c.status === 'changes_requested') return { title: 'Changes requested', status: 'Returned for investigator updates' };
    if (issues || state === 'issues_found') return { title: 'Human review required', status: 'Blocked — findings to resolve' };
    return { title: 'Human review required', status: 'Awaiting human review' };
  },
  reasons(c) {
    const d=c.outputs?.detection, e=d?.explanation, g=d?.subgraph;
    if(!d)return ['Detection has not completed. No model finding is available.'];
    const score=Number.isFinite(d.score)?d.score.toFixed(3):'—';
    const threshold=Number.isFinite(d.threshold)?d.threshold.toFixed(3):'—';
    const reasons=[`The primary transaction received a model score of ${score}, ${d.score>=d.threshold?'above':'below'} this case’s alert threshold of ${threshold}.`];
    if(g?.nodes?.length)reasons.push(`The investigation includes ${g.nodes.length} connected transaction${g.nodes.length===1?'':'s'} and ${g.edges.length} payment-flow relationship${g.edges.length===1?'':'s'}.`);
    const scored=(g?.nodes||[]).filter(n=>!n.target&&Number.isFinite(n.model_score));
    if(scored.length){const above=scored.filter(n=>n.model_score>=d.threshold).length;if(above)reasons.push(`${above} additional connected transaction${above===1?'':'s'} ${above===1?'exceeds':'exceed'} the alert threshold.`);}
    if(e?.status==='available'&&e.edges?.some(edge=>edge.attribution>0))reasons.push('The graph explanation identifies important transaction relationships.');
    return reasons;
  },
  flagReasons(c) {
    const d=c.outputs?.detection, e=d?.explanation, g=d?.subgraph;
    if(!d)return [];
    const out=[];
    if(Number.isFinite(d.score)&&Number.isFinite(d.threshold)&&d.score>=d.threshold)out.push({title:'High model score',text:`The primary transaction received a model score of ${d.score.toFixed(3)}, above the investigation threshold of ${d.threshold.toFixed(3)}.`});
    const scored=(g?.nodes||[]).filter(n=>!n.target&&Number.isFinite(n.model_score));
    const above=scored.filter(n=>n.model_score>=d.threshold).length;
    if(above)out.push({title:'Connected high-score transactions',text:`${above} additional connected transaction${above===1?'':'s'} also exceed the investigation threshold.`});
    if(e?.status==='available'&&e.edges?.some(edge=>edge.attribution>0))out.push({title:'Important transaction relationships',text:'The graph explanation identifies specific transaction relationships as more important to this local prediction.'});
    return out;
  },
  collection(cases,collection,mode) {
    if(mode==='technical')return cases;
    if(collection?.status!=='available')return [];
    const byId=new Map(cases.map(c=>[c.id,c]));
    return collection.case_ids.map(id=>byId.get(id)).filter(Boolean);
  },
  counts(cases) {
    const pending=cases.filter(c=>['awaiting_review','changes_requested'].includes(c.status));
    return {review:pending.length,high:pending.filter(c=>c.severity==='high').length,
      evidence:cases.filter(c=>c.evidence_traceable===true&&c.evidence_count>0).length,
      ready:pending.filter(c=>Presentation.review(c)==='Ready for human review').length,
      blocked:cases.filter(c=>c.error||c.status==='failed'||(pending.includes(c)&&c.blocking_findings>0)).length};
  },
  event(e) {
    if(e.action==='completed')return ({detection:'Transaction scored and explained',triage:'Investigation priority assigned',investigation:'Evidence collected and dossier prepared',narrative:'SAR narrative prepared',compliance:'Compliance validation completed'})[e.stage]||'Stage completed';
    return ({case_created:'Case opened',started:'Stage started',review_requested:'Human review requested',draft_revised_and_revalidated:'Draft edited and checked again',request_changes:'Reviewer requested changes',approve:'Reviewer approved',reject:'Reviewer rejected',reopened_for_review:'Case reopened for review',failed:'Stage failed'})[e.action] || e.action.replaceAll('_',' ');
  }
};
if(typeof module!=='undefined')module.exports=Presentation;

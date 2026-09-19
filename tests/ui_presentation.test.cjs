const test = require('node:test');
const assert = require('node:assert/strict');
const P = require('../web/presentation.js');
const fixture = () => ({status:'awaiting_review',outputs:{detection:{score:.4,threshold:.7,subgraph:{nodes:[{id:'T',target:true,model_score:.4},{id:'N',model_score:.9}],edges:[{source:'N',target:'T'}]},explanation:{status:'available',edges:[{attribution:.5}]}},compliance:{status:'review_ready',issues:[]}}});

test('plain reasons follow score, cutoff and scored context; do not invent feature semantics',()=>{
  const c=fixture(),before=JSON.stringify(c),text=P.reasons(c).join(' ');
  assert.match(text,/0\.400.*below.*0\.700/);assert.match(text,/1 additional connected transaction/);
  assert.doesNotMatch(text,/high model score|account|amount|velocity|smurfing|layering|certainty|probability/);
  assert.equal(JSON.stringify(c),before);
  c.outputs.detection.subgraph.nodes[1].model_score=null;
  assert.doesNotMatch(P.reasons(c).join(' '),/additional connected transaction/);
  assert.deepEqual(P.reasons({outputs:{}}),['Detection has not completed. No model finding is available.']);
});
test('flag reasons are concise, numbered categories derived from actual data',()=>{
  const c=fixture();
  const titles=P.flagReasons(c).map(r=>r.title);
  assert.deepEqual(titles,['Connected high-score transactions','Important transaction relationships']);
  assert.doesNotMatch(P.flagReasons(c).map(r=>r.text).join(' '),/account|amount|velocity|smurfing|layering/);
  c.outputs.detection.score=.9;
  const all=P.flagReasons(c);
  assert.equal(all[0].title,'High model score');
  assert.match(all[0].text,/0\.900.*0\.700/);
  assert.deepEqual(P.flagReasons({outputs:{}}),[]);
});

test('readiness never turns missing validation, failures or unsupported text into ready',()=>{
 const c=fixture();assert.equal(P.review(c),'Ready for human review');
 c.outputs.compliance.issues=['Unsupported claim'];assert.match(P.review(c),/Blocked/);
 c.outputs.compliance=undefined;assert.equal(P.review(c),'Awaiting validation');
 c.status='approved';assert.equal(P.review(c),'Approved by reviewer');
 c.status='failed';assert.equal(P.review(c),'Stage needs attention');
});
test('judge collection keeps manifest order and preserves repeated historical cases',()=>{
 const cases=[{id:'history',transaction_id:'T'},{id:'second'},{id:'canonical',transaction_id:'T'}];
 const collection={status:'available',case_ids:['canonical','second']};
 assert.deepEqual(P.collection(cases,collection,'judge').map(c=>c.id),['canonical','second']);
 assert.equal(P.collection(cases,collection,'technical'),cases);
 assert.deepEqual(P.collection(cases,{status:'unavailable'},'judge'),[]);assert.equal(cases.length,3);
});
test('operational cards count only supplied cases and require explicit evidence checks',()=>{
 const cases=[{status:'awaiting_review',severity:'high',evidence_traceable:true,evidence_count:3,compliance_status:'review_ready',blocking_findings:0},{status:'awaiting_review',severity:'low',evidence_count:4,compliance_status:'issues_found',blocking_findings:1},{status:'approved',severity:'high',evidence_traceable:true,evidence_count:2}];
 assert.deepEqual(P.counts(cases),{review:2,high:1,evidence:2,ready:1,blocked:1});
 assert.equal(P.counts([{status:'failed',error:{stage:'narrative'}}]).blocked,1);
});
test('provider and timeline labels distinguish extraction, generation and actual events',()=>{
 assert.equal(P.provider({provider:'extractive'}),'Deterministic extractive mode');
 assert.match(P.provider({provider:'local'}),/Local model/);
  assert.equal(P.event({stage:'narrative',action:'started'}),'Stage started');
  assert.equal(P.event({stage:'narrative',action:'completed'}),'SAR narrative prepared');
  assert.equal(P.event({stage:'human_review',action:'approve'}),'Reviewer approved');
  assert.equal(P.event({stage:'human_review',action:'reopened_for_review'}),'Case reopened for review');
  assert.equal(P.kind('synthetic_test'),'SYNTHETIC DEMO DATA');
});
test('status labels convert internal states to human wording',()=>{
  assert.equal(P.statusLabel('awaiting_review'),'Awaiting human review');
  assert.equal(P.statusLabel('changes_requested'),'Changes requested');
  assert.equal(P.statusLabel('approved'),'Approved');
  assert.equal(P.statusLabel('rejected'),'Rejected');
  assert.equal(P.statusLabel('failed'),'Stage failed');
});
test('review summary is dynamic across review states',()=>{
  const c=(status,extra={})=>({status,outputs:{compliance:{status:'review_ready',issues:[],...extra}}});
  assert.deepEqual(P.reviewSummary(c('awaiting_review')),{title:'Human review required',status:'Awaiting human review'});
  assert.deepEqual(P.reviewSummary(c('approved')),{title:'Human review completed',status:'Approved'});
  assert.deepEqual(P.reviewSummary(c('rejected')),{title:'Human review completed',status:'Rejected'});
  assert.deepEqual(P.reviewSummary(c('changes_requested')),{title:'Changes requested',status:'Returned for investigator updates'});
});

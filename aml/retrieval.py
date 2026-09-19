from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def retrieve(evidence, query, k=12, *, case_id=None, kinds=None, source_records=None):
    if not evidence:
        raise ValueError('No evidence available for retrieval')
    if k < 1:
        raise ValueError('Retrieval count must be positive')
    cases = {e['case_id'] for e in evidence}
    if len(cases) != 1 or (case_id is not None and cases != {case_id}):
        raise ValueError('Retrieval must remain within one requested case')
    if len({e['id'] for e in evidence}) != len(evidence):
        raise ValueError('Duplicate evidence IDs')
    candidates, seen = [], set()
    for e in evidence:
        if kinds is not None and e['kind'] not in kinds: continue
        if source_records is not None and e['source_record'] not in source_records: continue
        identity = (e['source'], e['source_record'], e['version'], e['fact'])
        if identity in seen: continue
        seen.add(identity); candidates.append(e)
    if not candidates: return []
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([e['fact'] for e in candidates])
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    order = np.argsort(-scores, kind='stable')[:k]
    return [{'evidence_id': candidates[int(i)]['id'], 'score': float(scores[int(i)]), 'method': 'TF-IDF cosine',
             'kind': candidates[int(i)]['kind'], 'source_record': candidates[int(i)]['source_record'],
             'selection_reason': 'Case-scoped lexical match after exact metadata filters and source-fact deduplication',
             'score_meaning': 'Text similarity, not truth/model confidence'} for i in order if scores[int(i)] > 0]

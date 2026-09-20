"""Validation-only operating-point and reliability diagnostics, never deployment policy."""
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression


def checked(y, scores):
    y, scores = np.asarray(y), np.asarray(scores, dtype=float)
    if y.shape != scores.shape or y.ndim != 1 or not len(y):
        raise ValueError('Aligned nonempty labels/scores required')
    if not set(y).issubset({0, 1}) or not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError('Binary labels and finite scores in [0,1] required')
    return y, scores


def threshold_table(y, scores):
    y, scores = checked(y, scores)
    rows = []
    for threshold in np.linspace(.05, .95, 91):
        pred = scores >= threshold
        tp, fp = int(((y == 1) & pred).sum()), int(((y == 0) & pred).sum())
        fn, tn = int(((y == 1) & ~pred).sum()), int(((y == 0) & ~pred).sum())
        row = {'threshold': float(threshold), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
               'precision': tp / (tp + fp) if tp + fp else 0.,
               'recall': tp / (tp + fn) if tp + fn else 0., 'alerts': tp + fp}
        for beta, name in [(.5, 'f0_5'), (1, 'f1'), (2, 'f2')]:
            denom = (1 + beta**2) * tp + beta**2 * fn + fp
            row[name] = (1 + beta**2) * tp / denom if denom else 0.
        rows.append(row)
    return rows


def operating_points(rows):
    return {name: {'objective': description, **max(rows, key=lambda r: r[metric])}
            for name, metric, description in [
                ('recall_emphasis', 'f2', 'Maximum validation F2; misses weighted more heavily'),
                ('balanced', 'f1', 'Maximum validation F1'),
                ('precision_emphasis', 'f0_5', 'Maximum validation F0.5; precision weighted more heavily')]}


def reliability(y, scores, bins=10):
    y, scores = checked(y, scores)
    assigned = np.minimum((scores * bins).astype(int), bins - 1)
    rows = []
    for i in range(bins):
        mask = assigned == i
        if mask.any():
            rows.append({'lower': i / bins, 'upper': (i + 1) / bins, 'count': int(mask.sum()),
                         'mean_score': float(scores[mask].mean()), 'observed_illicit_fraction': float(y[mask].mean())})
    return {'n': len(y), 'positives': int(y.sum()), 'brier': float(brier_score_loss(y, scores)),
            'log_loss': float(log_loss(y, np.clip(scores, 1e-7, 1-1e-7), labels=[0, 1])),
            'average_precision': float(average_precision_score(y, scores)),
            'ece_10_equal_width': sum(r['count'] * abs(r['mean_score'] - r['observed_illicit_fraction']) for r in rows) / len(y),
            'bins': rows}


def calibration_experiment(y, scores, times):
    y, scores = checked(y, scores)
    times = np.asarray(times)
    if times.shape != y.shape or not np.all((times >= 30) & (times <= 34)):
        raise ValueError('Calibration diagnostics accept validation time steps 30..34 only')
    fit, assessment = times <= 32, times >= 33
    if any(set(y[m]) != {0, 1} for m in [fit, assessment]):
        return {'status': 'insufficient_classes', 'deployed': False}
    logits = np.log(np.clip(scores, 1e-7, 1-1e-7) / (1-np.clip(scores, 1e-7, 1-1e-7)))[:, None]
    sigmoid = LogisticRegression(C=1., max_iter=1000).fit(logits[fit], y[fit])
    isotonic = IsotonicRegression(out_of_bounds='clip').fit(scores[fit], y[fit])
    return {'status': 'diagnostic_only', 'deployed': False, 'fit_steps': [30, 32], 'assessment_steps': [33, 34],
            'fit_count': int(fit.sum()), 'assessment_count': int(assessment.sum()),
            'limitation': 'Checkpoint was already selected using steps 30..34; this is a reused-validation temporal diagnostic, not independent calibration validation.',
            'raw': reliability(y[assessment], scores[assessment]),
            'sigmoid': reliability(y[assessment], sigmoid.predict_proba(logits[assessment])[:, 1]),
            'isotonic': reliability(y[assessment], isotonic.predict(scores[assessment])),
            'sigmoid_parameters': {'coefficient': float(sigmoid.coef_[0, 0]), 'intercept': float(sigmoid.intercept_[0])},
            'isotonic_parameters': {'x': isotonic.X_thresholds_.tolist(), 'y': isotonic.y_thresholds_.tolist()}}

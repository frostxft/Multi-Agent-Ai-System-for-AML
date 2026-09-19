"""Deterministic, clearly-labelled demo KYC / sanctions enrichment for the capstone.

This module is deliberately isolated and explicit:

* It returns SYNTHETIC, clearly-labelled demo enrichment only.
* It is NEVER an input to the GAT model and never changes any model score.
* It is NEVER written into benchmark evidence records or their provenance.
* It is a static prototype reference, not live KYC or live sanctions screening.
* It does not create real customers or real sanctions matches.

The values are deterministic functions of the transaction ID so a given demo case
always renders the same enrichment.
"""
from __future__ import annotations

import hashlib

VERSION = 'demo-enrichment-v1'
LABEL = 'DEMO / SYNTHETIC PROTOTYPE ENRICHMENT'
SOURCE = 'Team Zen static demo reference (synthetic; not a real provider)'
SCREENED_AT = '2026-07-05T00:00:00Z'
NOTE = ('Synthetic demonstration enrichment. Not a real customer or sanctions hit; '
        'never used as a GAT model input and not part of benchmark evidence.')

# Fictional demo profile shapes; no real customer data is represented.
_DEMO_PROFILES = (
    {'country': 'India', 'account_type': 'Retail savings', 'risk_rating': 'Low'},
    {'country': 'India', 'account_type': 'Business current', 'risk_rating': 'Medium'},
    {'country': 'United Arab Emirates', 'account_type': 'Corporate', 'risk_rating': 'Medium'},
    {'country': 'Singapore', 'account_type': 'Corporate', 'risk_rating': 'Elevated'},
)

# Static synthetic screening list. It contains only fictional identifiers that are
# never generated below, so the demo reports "no match" rather than inventing a hit.
_DEMO_SANCTIONS_LIST = {'DEMO-ENTITY-LISTED-0000'}


def _digest(transaction_id: str) -> str:
    return hashlib.sha256(str(transaction_id).encode()).hexdigest()


def demo_enrichment(transaction_id: str) -> dict:
    """Return deterministic synthetic KYC + sanctions enrichment for a transaction."""
    digest = _digest(transaction_id)
    profile = _DEMO_PROFILES[int(digest[:8], 16) % len(_DEMO_PROFILES)]
    customer_id = 'DEMO-CUST-' + digest[:8].upper()
    entity_id = 'DEMO-ENTITY-' + digest[8:16].upper()
    matched = entity_id in _DEMO_SANCTIONS_LIST
    kyc = {
        'label': 'DEMO / SYNTHETIC KYC',
        'status': 'synthetic_profile',
        'customer_id': customer_id,
        'country': profile['country'],
        'account_type': profile['account_type'],
        'risk_rating': profile['risk_rating'],
        'source': SOURCE,
        'version': VERSION,
        'note': NOTE,
    }
    sanctions = {
        'label': 'DEMO / SYNTHETIC SANCTIONS SCREENING',
        'status': 'synthetic_match' if matched else 'synthetic_no_match',
        'screening_result': 'Potential match on static demo list' if matched else 'No match on static demo list',
        'match_status': 'Potential match' if matched else 'No match',
        'reference': 'DEMO-SANCTIONS-LIST-v1 (synthetic)',
        'source': SOURCE,
        'screened_at': SCREENED_AT,
        'entity_id': entity_id,
        'note': NOTE,
    }
    return {
        'label': LABEL,
        'version': VERSION,
        'transaction_id': str(transaction_id),
        'entity_link': 'Deterministic synthetic demo mapping; not inferred from benchmark data',
        'kyc': kyc,
        'sanctions': sanctions,
        'not_model_input': True,
        'note': NOTE,
    }

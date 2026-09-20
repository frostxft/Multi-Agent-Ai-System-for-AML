"""Reference-provider contracts and isolated synthetic snapshots, never entity inference."""
from typing import Protocol, Literal
from pathlib import Path
import hashlib
import json
from pydantic import Field
from .schemas import Contract


class ReferenceResult(Contract):
    status: Literal['unavailable', 'synthetic_profile', 'synthetic_match', 'synthetic_no_match']
    label: str
    source: str
    version: str
    entity_id: str | None = None
    fields: dict = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)


class KYCProvider(Protocol):
    def profile(self, entity_id: str) -> ReferenceResult: ...


class SanctionsProvider(Protocol):
    def screen(self, entity_id: str, attributes: dict) -> ReferenceResult: ...


class UnavailableReferenceProvider:
    def profile(self, entity_id):
        return ReferenceResult(status='unavailable', label='KYC UNAVAILABLE', source='Dataset scope', version='no-reference-v1',
                               limitations=['No verified transaction-to-entity link or genuine KYC provider.'])

    def screen(self, entity_id, attributes):
        return ReferenceResult(status='unavailable', label='SANCTIONS UNAVAILABLE', source='Dataset scope', version='no-reference-v1',
                               limitations=['No genuine sanctions snapshot or screening coverage.'])


class SyntheticSnapshotProvider:
    """Explicit entity-ID matching only; no fuzzy name matching or real sanctions assertion."""
    def __init__(self, path: Path):
        raw = path.read_bytes(); data = json.loads(raw)
        if data.get('kind') != 'synthetic_demo' or not data.get('source') or not data.get('version'):
            raise ValueError('Reference snapshot must declare synthetic_demo, source and version')
        self.data = data
        self.version = data['version'] + ':sha256:' + hashlib.sha256(raw).hexdigest()

    def profile(self, entity_id):
        fields = self.data.get('profiles', {}).get(entity_id)
        return ReferenceResult(status='synthetic_profile' if fields is not None else 'unavailable',
                               label='SYNTHETIC DEMO KYC', entity_id=entity_id, source=self.data['source'], version=self.version,
                               fields=fields or {}, limitations=['Artificial fixture profile, not a real customer or verified identity.'])

    def screen(self, entity_id, attributes):
        match = next((r for r in self.data.get('sanctions', []) if r['entity_id'] == entity_id), None)
        return ReferenceResult(status='synthetic_match' if match else 'synthetic_no_match', label='SYNTHETIC DEMO SANCTIONS',
                               entity_id=entity_id, source=self.data['source'], version=self.version, fields=match or {},
                               limitations=['Exact synthetic entity-ID lookup only; no real sanctions coverage or identity resolution.'])


def reference_context(data_kind, transaction_id, provider=None):
    if data_kind != 'synthetic_test' or provider is None:
        unavailable = UnavailableReferenceProvider()
        return {'kyc': unavailable.profile(None).model_dump(), 'sanctions': unavailable.screen(None, {}).model_dump(),
                'entity_link': 'unavailable; Bitcoin transaction IDs are not customer identities'}
    entity = provider.data.get('transaction_entity_links', {}).get(transaction_id)
    if entity is None:
        return reference_context('unverified_input', transaction_id)
    profile = provider.profile(entity)
    return {'kyc': profile.model_dump(), 'sanctions': provider.screen(entity, profile.fields).model_dump(),
            'entity_link': 'SYNTHETIC DEMO mapping supplied explicitly by fixture; not inferred'}

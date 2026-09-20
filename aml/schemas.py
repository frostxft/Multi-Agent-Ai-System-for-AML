from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)

class Detection(Contract):
    case_id: str
    model_id: str
    dataset_fingerprint: str
    data_kind: str
    seed_transaction: str
    score: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    flagged: bool
    inference_at: str
    subgraph: dict
    explanation: dict
    threshold_policy: dict = Field(default_factory=dict)

class Evidence(Contract):
    id: str
    case_id: str
    kind: Literal['benchmark', 'synthetic_test', 'unverified_input', 'model_output', 'derived_value', 'missing_information']
    source: str
    source_record: str
    version: str
    fact: str

class Claim(Contract):
    text: str
    evidence_ids: list[str] = Field(min_length=1)

class Narrative(Contract):
    status: Literal['DRAFT'] = 'DRAFT'
    provider: str
    sections: dict[str, list[Claim]]
    synthesis: str | None = None
    synthesis_status: str
    retrieved_evidence_ids: list[str]
    generation_metadata: dict = Field(default_factory=dict)
    revision_metadata: dict = Field(default_factory=dict)

class Review(Contract):
    decision: Literal['approve', 'reject', 'request_changes']
    notes: str = Field(min_length=3, max_length=5000)
    expected_revision: int = Field(ge=1)

    @field_validator('notes')
    @classmethod
    def meaningful_notes(cls, value):
        if len(value.strip()) < 3:
            raise ValueError('Review notes must contain at least three non-whitespace characters')
        return value.strip()

class CreateCase(Contract):
    transaction_id: str = Field(min_length=1, max_length=80)

class Reopen(Contract):
    expected_revision: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=2000)

    @field_validator('reason')
    @classmethod
    def meaningful_reason(cls, value):
        if len(value.strip()) < 3:
            raise ValueError('Reopen reason must contain at least three non-whitespace characters')
        return value.strip()

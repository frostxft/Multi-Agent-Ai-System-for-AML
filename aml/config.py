from dataclasses import dataclass
from pathlib import Path
import os
from urllib.parse import urlsplit

@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv('AML_DATA_DIR', 'data/elliptic/raw'))
    artifact_dir: Path = Path(os.getenv('AML_ARTIFACT_DIR', 'artifacts/benchmark'))
    db_path: Path = Path(os.getenv('AML_DB_PATH', 'artifacts/cases.db'))
    medium_threshold: float = float(os.getenv('AML_MEDIUM_THRESHOLD', '.5'))
    high_threshold: float = float(os.getenv('AML_HIGH_THRESHOLD', '.8'))
    llm_provider: str = os.getenv('AML_LLM_PROVIDER', 'extractive')
    llm_model: str = os.getenv('AML_LLM_MODEL', 'artifacts/flan-t5-small')
    ollama_url: str = os.getenv('AML_OLLAMA_URL', 'http://127.0.0.1:11434')
    encryption_key: str = os.getenv('AML_ENCRYPTION_KEY', '')
    reviewer_token: str = os.getenv('AML_REVIEWER_TOKEN', '')
    analyst_token: str = os.getenv('AML_ANALYST_TOKEN', '')
    detection_threshold: float | None = float(os.environ['AML_DETECTION_THRESHOLD']) if os.getenv('AML_DETECTION_THRESHOLD') else None
    reference_fixture: str = os.getenv('AML_REFERENCE_FIXTURE', '')

    def __post_init__(self):
        endpoint = urlsplit(self.ollama_url)
        if endpoint.scheme not in {'http', 'https'} or not endpoint.hostname or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
            raise ValueError('Narrative endpoint must be HTTP(S) without embedded credentials, query or fragment')
        if self.detection_threshold is not None and not 0 <= self.detection_threshold <= 1:
            raise ValueError('Detection threshold must be finite and in [0,1]')
        if not 0 <= self.medium_threshold < self.high_threshold <= 1:
            raise ValueError('Require 0 <= medium < high <= 1')
        if self.llm_provider not in {'extractive', 'local', 'ollama'}:
            raise ValueError('Unknown narrative provider')
        if self.reviewer_token and self.reviewer_token == self.analyst_token:
            raise ValueError('Reviewer and analyst tokens must be distinct')

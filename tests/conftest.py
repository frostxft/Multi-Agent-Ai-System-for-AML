from dataclasses import replace
import pytest
from aml.config import Settings
from aml.data import synthetic_fixture, load_graph
from aml.model import train
from aml.pipeline import Pipeline

@pytest.fixture(scope='session')
def trained(tmp_path_factory):
    root = tmp_path_factory.mktemp('synthetic')
    synthetic_fixture(root / 'raw')
    graph = load_graph(root / 'raw')
    train(graph, root / 'model', epochs=5)
    return graph, Settings(data_dir=root / 'raw', artifact_dir=root / 'model', llm_provider='extractive')

@pytest.fixture
def pipeline(trained, tmp_path):
    graph, settings = trained
    return Pipeline(graph, replace(settings, db_path=tmp_path / 'cases.db'))

@pytest.fixture
def case(pipeline):
    result = pipeline.create('3500', 'synthetic-test-actor')
    assert result['status'] == 'awaiting_review', result.get('error')
    return result

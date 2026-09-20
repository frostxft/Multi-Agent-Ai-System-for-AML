import copy
import torch
import numpy as np
from aml.model import train

def test_heldout_features_and_labels_do_not_change_training(trained,tmp_path):
    graph,_=trained
    changed=copy.deepcopy(graph)
    # Alter every test-period feature/label while retaining the same graph shape.
    changed.features[changed.times>=35] *= -13
    changed.labels[changed.times>=35] = 1 - changed.labels[changed.times>=35]
    # Preserve unknown semantics; labels stay binary/unknown.
    changed.labels[changed.labels==2] = -1
    train(graph,tmp_path/'a',epochs=2)
    train(changed,tmp_path/'b',epochs=2)
    a=torch.load(tmp_path/'a/gat.pt',weights_only=True)
    b=torch.load(tmp_path/'b/gat.pt',weights_only=True)
    assert a['threshold']==b['threshold']
    assert all(torch.equal(a['state_dict'][k],b['state_dict'][k]) for k in a['state_dict'])
    baseline_a = np.load(tmp_path/'a/baseline.npz')
    baseline_b = np.load(tmp_path/'b/baseline.npz')
    assert all(np.array_equal(baseline_a[key], baseline_b[key]) for key in baseline_a.files)

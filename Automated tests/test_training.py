"""Reproducibility tests for model-training datasets.

Author: Leslie Raya
"""

from ml.train_model import generate_attack_scenarios, generate_normal_activity


def test_normal_generation_is_reproducible() -> None:
    first = generate_normal_activity(25, seed=7)
    second = generate_normal_activity(25, seed=7)
    assert first.equals(second)


def test_attack_scenarios_have_higher_throughput() -> None:
    normal = generate_normal_activity(100, seed=8)
    attacks = generate_attack_scenarios(100, seed=9)
    assert attacks["events_per_second"].median() > normal["events_per_second"].median()

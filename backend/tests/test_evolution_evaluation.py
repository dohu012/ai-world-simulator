from app.application.evolution_evaluation import run_evolution_evaluation


def test_fixed_evolution_corpus_passes_hard_gates_and_is_repeatable() -> None:
    first = run_evolution_evaluation()
    second = run_evolution_evaluation()
    assert first == second
    assert first.hard_gates_passed
    assert first.decisions_per_l3_agent == 30
    assert first.unsupported_commits == 0
    assert first.forbidden_exposure == 0
    assert first.oracle_follow_count > 0
    assert first.oracle_reject_count > 0
    assert first.oracle_partial_count > 0
    assert first.maximum_dependence <= 0.45
    assert first.evolved_consistency >= first.static_consistency

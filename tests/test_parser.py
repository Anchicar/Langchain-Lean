from langchain_lean.core.parser import parse_lean_output


def test_parse_success_complete():
    parsed = parse_lean_output(raw_output="", exit_code=0)
    assert parsed.success is True
    assert parsed.proof_complete is True
    assert parsed.errors == []
    assert parsed.goals == []


def test_parse_incomplete_with_goal():
    raw = (
        "check.lean:4:16: error: unexpected end of input; expected '?', '_' or '{'\n"
        "check.lean:4:14: error: unsolved goals\n"
        "case succ\n"
        "n : Nat\n"
        "ih : n + 0 = n\n"
        "⊢ n + 1 + 0 = n + 1\n"
    )
    parsed = parse_lean_output(raw_output=raw, exit_code=1)

    assert parsed.success is False
    assert parsed.proof_complete is False
    assert len(parsed.errors) >= 2
    assert len(parsed.goals) == 1
    assert parsed.goals[0].goal == "n + 1 + 0 = n + 1"


def test_parse_syntax_error():
    raw = "check.lean:1:10: error: expected token\n"
    parsed = parse_lean_output(raw_output=raw, exit_code=1)

    assert parsed.success is False
    assert parsed.proof_complete is False
    assert parsed.errors == ["expected token"]

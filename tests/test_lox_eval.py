import pytest

import pylox.lox_eval as le
import pylox.lox_types as lt
import pylox.token_types as tt


@pytest.mark.parametrize(
    "lox_type, left, right, result",
    (
        (tt.MINUS, 2.0, 1.0, 1),
        (tt.PLUS, "foo", "bar", "foobar"),
        (tt.STAR, "foo", 10, "foo" * 10),
    ),
)
def test_evaluate_lox_binary(lox_type, left, right, result):
    assert le.evaluate_lox_binary(lox_type, left, right) == result


@pytest.mark.parametrize(
    "lox_type, left, result", ((tt.BANG, lt.nil, True), (tt.MINUS, 2, -2))
)
def test_evaluate_lox_unary(lox_type, left, result):
    assert le.evaluate_lox_unary(lox_type, left) == result

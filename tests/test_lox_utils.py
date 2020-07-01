import pytest

import pylox.lox_utils as lu


@pytest.mark.parametrize(
    "num, expected", (("20", True), ("2.2", True), ("e+20", True), ("nope", False))
)
def test_is_lox_number(num, expected):
    assert lu.is_lox_number(num) is expected


@pytest.mark.parametrize("string, expected", (('"good"', True), ("bad", False)))
def test_is_lox_string(string, expected):
    assert lu.is_lox_string(string) is expected

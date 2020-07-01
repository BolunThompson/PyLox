import pylox.lox_types as lc


def test_singleton():
    assert lc.nil is lc.NilType()

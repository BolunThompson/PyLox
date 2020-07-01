import pylox.scanner as s
from tests import data


# Parameterize later?
def test_scanner():
    assert tuple(s.scan(data.SOURCE[0])) == tuple(data.SOURCE[1])

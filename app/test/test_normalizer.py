import pytest
from ..normalizer import normalize_hpc


def test_normalize():
    # Using RHESSI Flare 12070596 as the test subject
    # hpc_x = 515
    # hpc_y = -342
    coord = normalize_hpc(515, -342, "2012-07-05 13:01:46")
    assert pytest.approx(coord.Tx.value) == 523.6178
    assert pytest.approx(coord.Ty.value) == -347.7228

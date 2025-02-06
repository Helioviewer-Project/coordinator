from astropy.time import Time, TimeDelta
import astropy.units as u
from ephemeris import get_position


def test_ephemeris():
    # Get sdo position
    start = Time("2025-01-01 00:00:00")
    positions = get_position("sdo", start, Time("2025-01-01 12:00:00"))
    # Verify that there's a coordinate for every hour between start and end, inclusive.
    assert len(positions) == 13
    for i, pos in enumerate(positions):
        assert pos.obstime == start + TimeDelta(i * u.hour)

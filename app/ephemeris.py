import astropy.units as u
from astropy.time import Time
from sunpy.coordinates import get_horizons_coord

# JPL Horizons treats a bare major-body name as a wildcard, so "earth" becomes
# "EARTH*" and matches both the planet's body center and its planet-moon
# barycenter (e.g. "Earth" (399) and "Earth-Moon Barycenter" (3)). That
# ambiguity makes Horizons raise "Multiple major-bodies match string" instead
# of returning a position. Map the ambiguous names to their unambiguous
# Horizons body-center IDs so a request like /position/earth resolves to the
# geocenter (399). Spacecraft names (e.g. "SDO") are already unambiguous and
# pass through untouched.
_HORIZONS_BODY_IDS = {
    "sun": 10,  # Sun (no barycenter ambiguity)
    "mercury": 199,  # Mercury body center, not Mercury Barycenter (1)
    "venus": 299,  # Venus body center, not Venus Barycenter (2)
    "earth": 399,  # Earth geocenter, not Earth-Moon Barycenter (3)
    "moon": 301,  # Moon (Earth's moon) body center
    "mars": 499,  # Mars body center, not Mars Barycenter (4)
    "jupiter": 599,  # Jupiter body center, not Jupiter Barycenter (5)
    "saturn": 699,  # Saturn body center, not Saturn Barycenter (6)
    "uranus": 799,  # Uranus body center, not Uranus Barycenter (7)
    "neptune": 899,  # Neptune body center, not Neptune Barycenter (8)
    "pluto": 999,  # Pluto body center, not Pluto Barycenter (9)
}


def _resolve_observatory(observatory_name: str):
    """
    Translate an ambiguous major-body name (case-insensitive) into its JPL
    Horizons body-center ID, leaving spacecraft and other names untouched.
    """
    return _HORIZONS_BODY_IDS.get(observatory_name.strip().lower(), observatory_name)


def get_position(observatory_name: str, start_time: Time, end_time: Time):
    time_range = end_time - start_time
    hours = int(time_range.to("hour").value)
    times = Time([start_time + i * 3600 * u.second for i in range(hours + 1)])
    return get_horizons_coord(_resolve_observatory(observatory_name), times)

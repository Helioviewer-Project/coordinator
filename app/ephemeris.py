import astropy.units as u
from astropy.time import Time
from sunpy.coordinates import get_horizons_coord


def get_position(observatory_name: str, start_time: Time, end_time: Time):
    time_range = end_time - start_time
    hours = int(time_range.to("hour").value)
    times = Time([start_time + i * 3600 * u.second for i in range(hours + 1)])
    return get_horizons_coord(observatory_name, times)

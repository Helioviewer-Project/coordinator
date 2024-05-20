from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from sunpy.coordinates import frames, transform_with_sun_center
from sunpy.physics.differential_rotation import solar_rotate_coordinate

from frames import get_helioviewer_frame


def hgs2hpc(lat: float, lon: float, event_time: Time, target: Time) -> SkyCoord:
    """
    Takes a coordinate in the Heliographic Stonyhurst coordinate system
    with an assumed earth observer, and returns the coordinate in
    Helioprojective coordinates as seen from Helioviewer at the given
    target time.

    Parameters
    ----------
    lat : float
        Latitude coordinate in degrees
    lon : float
        Longitude coordinate in degrees
    event_time : Time
        Time when the lat/lon coordinates were measured
    target : Time
        Desired observation time
    """
    hv_frame = get_helioviewer_frame(target)
    with transform_with_sun_center():
        coord = SkyCoord(
            lon * u.deg,
            lat * u.deg,
            frame=frames.HeliographicStonyhurst,
            obstime=event_time,
        )
        return solar_rotate_coordinate(coord, hv_frame.observer)

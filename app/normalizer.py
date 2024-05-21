from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from sunpy.coordinates import Helioprojective, transform_with_sun_center
from sunpy.physics.differential_rotation import solar_rotate_coordinate
from frames import get_helioviewer_frame, get_earth_frame


def normalize_hpc(x: float, y: float, event_time: Time, target: Time) -> SkyCoord:
    """
    Accepts a Helioprojective coordinate which is assumed to be measured
    at the given observation time from Earth, and transforms it to
    Helioviewer's point of view

    Parameters
    ----------
    x: float
        X coordinate in arcseconds
    y: float
        Y coordinate in arcseconds
    event_time: Time
        Observation time of the given coordinates
    target: Time
        Desired time for the new coordinates
    """
    with transform_with_sun_center():
        real_coord = SkyCoord(
            x * u.arcsecond, y * u.arcsecond, frame=get_earth_frame(event_time)
        )
        hv_frame = get_helioviewer_frame(target)
        with Helioprojective.assume_spherical_screen(
            hv_frame.observer, only_off_disk=True
        ):
            return solar_rotate_coordinate(real_coord, hv_frame.observer)

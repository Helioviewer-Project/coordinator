from frames import get_helioviewer_frame, get_earth_frame
from astropy.coordinates import SkyCoord
from sunpy.coordinates import frames, transform_with_sun_center
import astropy.units as u

def normalize_hpc(x: float, y: float, obstime: str) -> SkyCoord:
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
    obstime: str
    """
    real_coord = SkyCoord(x*u.arcsecond, y*u.arcsecond, frame=get_earth_frame(obstime))
    return real_coord.transform_to(get_helioviewer_frame(obstime))

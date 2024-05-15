from frames import get_helioviewer_frame
from astropy.coordinates import SkyCoord
from sunpy.coordinates import frames, transform_with_sun_center
import astropy.units as u


def hgs2hpc(lat: float, lon: float, obstime: str) -> SkyCoord:
    """
    Takes a coordinate in the Heliographic Stonyhurst coordinate system
    with an assumed earth observer, and returns the coordinate in

    Parameters
    ----------
    lat : float
        Latitude coordinate in degrees
    lon : float
        Longitude coordinate in degrees
    obstime : str
        Observation time, in any format supported by sunpy
    """
    with transform_with_sun_center():
        coord = SkyCoord(
            lon * u.deg,
            lat * u.deg,
            frame=frames.HeliographicStonyhurst,
            obstime=obstime,
        )
        hpc = coord.transform_to(get_helioviewer_frame(obstime))
        return hpc

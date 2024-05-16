from sunpy.coordinates.frames import Helioprojective, HeliographicStonyhurst
import astropy.units as u

def get_earth_frame(obstime: str):
    """
    Returns the Helioprojective frame as seen from earth at the
    given observation time

    Parameters
    ----------
    obstime: str
        Observation time with both date and time.
    """
    return Helioprojective(observer="earth", obstime=obstime)

def get_helioviewer_frame(obstime: str):
    """
    Returns Helioviewer's Helioprojective frame of reference
    for the given observation time

    Parameters
    ----------
    obstime: str
        Observation time with both date and time. Supports
        all formats supported by sunpy
    """
    # Start with earth's frame of reference
    earth_frame = get_earth_frame(obstime)
    # Adjust the distance parameter to 1AU
    hv_observer = HeliographicStonyhurst(earth_frame.observer.lon, earth_frame.observer.lat, 1*u.au, obstime=obstime)
    # Return a new frame with Helioviewer's point of view as the observer
    return Helioprojective(observer=hv_observer, obstime=obstime)

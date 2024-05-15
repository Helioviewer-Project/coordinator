from sunpy.coordinates.frames import Helioprojective


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
    return Helioprojective(observer="earth", obstime=obstime)

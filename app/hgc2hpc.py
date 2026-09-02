"""
Heliographic Carrington -> Helioprojective conversion.

A Carrington coordinate (latitude, Carrington longitude) names a point fixed
to the Sun's rotating surface. This module turns such a point into the (x, y)
Helioprojective coordinate -- arcseconds on the plane of the sky -- as it
would appear from Helioviewer's point of view.

Two distinct times are involved, and the difference matters:

* ``coord_time`` -- when the lat/lon was *measured*. It fixes the Sun's
  orientation at the moment the feature was recorded.
* ``target``     -- the time you want the result *for*. Because the Sun
  rotates, a feature seen at ``coord_time`` has moved by ``target``;
  ``solar_rotate_coordinate`` carries it across that gap using solar
  differential rotation. When ``target == coord_time`` nothing rotates and
  you simply get a frame conversion.

Carrington longitude is "apparent": it folds in the light-travel time from
the Sun to the observer (~0.08 deg of rotation for Earth), so sunpy requires
an observer to transform out of the frame. The observer defaults to Earth --
matching the convention of Carrington coordinates reported in solar data
products (e.g. NOAA active regions, HMI synoptic maps) -- but may be any
solar-system body sunpy can resolve.
"""

from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from sunpy.coordinates import frames, transform_with_sun_center
from sunpy.physics.differential_rotation import solar_rotate_coordinate
from typing import List, Dict

from frames import get_helioviewer_frame, get_earth_frame


def hgc2hpc(
    lat: float, lon: float, coord_time: Time, target: Time, observer: str = "earth"
) -> SkyCoord:
    """
    Convert a single Heliographic Carrington coordinate into a Helioprojective
    coordinate as seen from Helioviewer at the ``target`` time.

    Parameters
    ----------
    lat : float
        Latitude in degrees.
    lon : float
        Carrington longitude in degrees.
    coord_time : Time
        Time the lat/lon was measured; sets the Sun's orientation to start from.
    target : Time
        Desired observation time. Differential rotation is applied between
        ``coord_time`` and ``target``. Pass the same value as ``coord_time``
        for a pure frame conversion with no rotation.
    observer : str, optional
        Solar-system body the Carrington coordinate is observed from; its
        apparent longitude depends on the observer's distance. Defaults to
        "earth".
    """
    # Helioviewer's Helioprojective point of view at the time we want the
    # answer for (an observer at 1 AU, oriented the same way as Earth).
    hv_frame = get_helioviewer_frame(target)

    # Keep the Sun pinned at the origin for every transform below, so moving
    # between observers can't introduce a spurious translation of the point.
    with transform_with_sun_center():
        # Interpret the input as an (apparent) Carrington coordinate as seen
        # from the observer at the time it was measured. The observer supplies
        # the light-travel-time correction that Carrington longitude depends on.
        coord = SkyCoord(
            lon * u.deg,
            lat * u.deg,
            frame=frames.HeliographicCarrington(obstime=coord_time, observer=observer),
        )
        # Project that surface point onto the sky as Earth saw it at coord_time.
        earth_frame = get_earth_frame(coord_time)
        hpc = coord.transform_to(earth_frame)
        # Differentially rotate the feature from coord_time to target, and
        # express the result from Helioviewer's observer.
        return solar_rotate_coordinate(hpc, hv_frame.observer)


def hgc2hpc_batch(
    coordinates: List[Dict], target: Time, observer: str = "earth"
) -> List[Dict]:
    """
    Vectorised version of :func:`hgc2hpc` for many coordinates that share one
    ``target`` time and ``observer``. Each coordinate keeps its own
    ``coord_time``.

    Parameters
    ----------
    coordinates : List[Dict]
        Dicts with keys ``lat``, ``lon`` (Carrington longitude), and
        ``coord_time``.
    target : Time
        Desired observation time, applied to every coordinate.
    observer : str, optional
        Solar-system body all coordinates are observed from. Defaults to
        "earth".

    Returns
    -------
    List[Dict]
        One ``{"x": ..., "y": ...}`` (arcseconds) per input coordinate, in the
        same order as the input.
    """
    if not coordinates:
        return []

    # Helioviewer's POV at the requested time (shared by every coordinate).
    hv_frame = get_helioviewer_frame(target)

    with transform_with_sun_center():
        # Pull each field into a column so sunpy transforms all points at once
        # instead of one SkyCoord per coordinate.
        lats = [c["lat"] for c in coordinates]
        lons = [c["lon"] for c in coordinates]
        coord_time = [c["coord_time"] for c in coordinates]
        coord = SkyCoord(
            lons,
            lats,
            unit="deg,deg",
            frame=frames.HeliographicCarrington,
            obstime=coord_time,  # per-coordinate measurement time
            observer=observer,  # shared observer for the whole batch
        )
        # Same two steps as the single case, vectorised: project as seen from
        # Earth at each coord_time, then differentially rotate to target.
        earth_frame = get_earth_frame(coord_time)
        hpc = coord.transform_to(earth_frame)
        result = solar_rotate_coordinate(hpc, hv_frame.observer)
    # .item() unwraps each 0-d numpy scalar into a plain Python float so the
    # response serialises cleanly to JSON.
    return [{"x": c.Tx.value.item(), "y": c.Ty.value.item()} for c in result]

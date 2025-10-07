from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from sunpy.coordinates import frames, transform_with_sun_center
from sunpy.physics.differential_rotation import solar_rotate_coordinate
from collections import defaultdict
from typing import List, Dict

from frames import get_helioviewer_frame, get_earth_frame


def hgs2hpc(lat: float, lon: float, coord_time: Time, target: Time) -> SkyCoord:
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
    coord_time : Time
        Time when the lat/lon coordinates were measured
    target : Time
        Desired observation time
    """
    hv_frame = get_helioviewer_frame(target)

    with transform_with_sun_center():
        coord = SkyCoord(
            lon * u.deg,
            lat * u.deg,
            frame=frames.HeliographicStonyhurst(obstime=coord_time),
        )
        # First convert to an hpc coordinate
        earth_frame = get_earth_frame(coord_time)
        hpc = coord.transform_to(earth_frame)
        # Then apply the rotation as seen from Helioviewer
        return solar_rotate_coordinate(hpc, hv_frame.observer)


def hgs2hpc_batch(coordinates: List[Dict], target: Time) -> List[Dict]:
    """
    Batch process multiple HGS to HPC coordinate transformations using vectorization.
    Groups coordinates by coord_time for optimal performance.

    Parameters
    ----------
    coordinates : List[Dict]
        List of coordinate dictionaries with keys: lat, lon, coord_time
    target : Time
        Target observation time (same for all coordinates)

    Returns
    -------
    List[Dict]
        List of results with keys: x, y
    """
    # Same target frame for all)
    hv_frame = get_helioviewer_frame(target)

    # Group coordinates by coord_time for batch processing
    groups = defaultdict(list)
    for idx, coord in enumerate(coordinates):
        coord_time_str = str(coord["coord_time"])
        groups[coord_time_str].append(
            {
                "idx": idx,
                "lat": coord["lat"],
                "lon": coord["lon"],
                "coord_time": coord["coord_time"],
            }
        )

    results = [None] * len(coordinates)

    with transform_with_sun_center():
        for coord_time_str, group in groups.items():
            # Extract arrays of lat/lon for this group
            lats = [c["lat"] for c in group]
            lons = [c["lon"] for c in group]
            coord_time = group[0]["coord_time"]

            # Get earth frame for this coord_time
            earth_frame = get_earth_frame(coord_time)

            # Create single SkyCoord with array of coordinates
            coord = SkyCoord(
                lons * u.deg,
                lats * u.deg,
                frame=frames.HeliographicStonyhurst(obstime=coord_time),
            )

            # Transform all coordinates at once
            hpc = coord.transform_to(earth_frame)

            # Apply rotation to all coordinates at once
            rotated = solar_rotate_coordinate(hpc, hv_frame.observer)

            # Extract results and place them in correct order
            for i, item in enumerate(group):
                results[item["idx"]] = {
                    "x": (
                        rotated.Tx.value[i]
                        if hasattr(rotated.Tx.value, "__iter__")
                        else rotated.Tx.value
                    ),
                    "y": (
                        rotated.Ty.value[i]
                        if hasattr(rotated.Ty.value, "__iter__")
                        else rotated.Ty.value
                    ),
                }

    return results

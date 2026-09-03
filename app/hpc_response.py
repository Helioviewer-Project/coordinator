"""
Serialisation of Helioprojective coordinates into the JSON the API returns.

Every helioprojective endpoint -- /hpc, /hgs2hpc, /hgc2hpc, GET and POST --
answers with the same object per coordinate, so the SkyCoord -> dict mapping
lives here once:

    {"x": float, "y": float, "visible": bool}

x, y
    Helioprojective Tx/Ty in arcseconds, on the plane of the sky.
visible
    False when the opaque Sun hides the point from Helioviewer's observer.
    Helioprojective is a projection, so a point on the far side projects back
    inside the solar disk and is otherwise indistinguishable from a near-side
    point at the same (x, y). This flag is what tells them apart.

    "Visible" is NOT the same as "on-disk": a point beyond the limb is visible
    at any depth. And the visible cap is slightly SMALLER than a hemisphere --
    the limb sits at arccos(rsun / observer_distance) ~= 89.73 deg, so a
    Stonyhurst point at longitude 90 is already hidden.

    Do not reimplement this as a "distance > 1 AU" test: the two disagree for
    off-disk points, which are visible but can sit fractionally beyond 1 AU.
    sunpy's is_visible() does the correct tangent-cone test; use it.
"""

from typing import Dict, List

from astropy.coordinates import SkyCoord


def hpc_dict(coord: SkyCoord) -> Dict:
    """
    Convert one scalar Helioprojective SkyCoord to its response dict.

    is_visible() hands back a 0-d numpy bool, which FastAPI cannot encode (it
    is not a bool subclass, unlike numpy floats) -- bool() is what keeps this a
    200 instead of a 500. .item() unwraps the numpy scalars to plain floats so
    the single and batch paths produce identical numbers.

    Parameters
    ----------
    coord : SkyCoord
        A scalar coordinate in a Helioprojective frame.
    """
    return {
        "x": coord.Tx.value.item(),
        "y": coord.Ty.value.item(),
        "visible": bool(coord.is_visible()),
    }


def hpc_dicts(coords: SkyCoord) -> List[Dict]:
    """
    Convert an array Helioprojective SkyCoord to one dict per element, in the
    same order.

    Each component is pulled out as a whole array and is_visible() is called
    once for the entire batch -- it is vectorised and returns a bool per
    element. Do not iterate the SkyCoord: indexing it rebuilds a complete frame
    object per element (~0.24 s for a 500-point batch, comparable to the
    coordinate transform itself). This form takes under a millisecond.

    Parameters
    ----------
    coords : SkyCoord
        An array coordinate in a Helioprojective frame.
    """
    xs = coords.Tx.value.tolist()
    ys = coords.Ty.value.tolist()
    visible = coords.is_visible().tolist()
    return [{"x": x, "y": y, "visible": v} for x, y, v in zip(xs, ys, visible)]

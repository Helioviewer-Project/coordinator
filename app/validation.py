"""
Contains validation related functions
"""

from typing_extensions import Annotated
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris
from pydantic import AfterValidator, BaseModel, ConfigDict


# This function is used by Pydantic to verify the user input
# is a valid time.
def make_time(value: str) -> Time:
    """
    Returns the given string as an astropy Time value or raises a ValueError
    if the value can't be converted.

    Parameters
    ----------
    value: str
        Value to cast to an astropy time.
    """
    return Time(value)


# Custom validation type which resolves to an astropy.Time instance
AstropyTime = Annotated[str, AfterValidator(make_time)]


# Valid observer names are the solar-system bodies that sunpy/astropy can
# resolve (e.g. "earth", "mars"); the set comes from the active ephemeris.
# Exposed as a constant so the API can advertise the allowed values in its docs.
VALID_OBSERVERS = tuple(sorted(body.lower() for body in solar_system_ephemeris.bodies))


def make_observer(value: str) -> str:
    """
    Normalise and validate a sunpy observer body name, returning it lowercased.
    Raises ValueError (which FastAPI turns into HTTP 422) if the body is not
    one sunpy can resolve.

    Parameters
    ----------
    value: str
        Observer body name, e.g. "earth", "mars" (case-insensitive).
    """
    normalized = value.lower()
    if normalized not in VALID_OBSERVERS:
        raise ValueError(
            f"Unknown observer '{value}'. Must be one of: {list(VALID_OBSERVERS)}"
        )
    return normalized


# Custom validation type which resolves to a valid sunpy observer body name
SunpyObserver = Annotated[str, AfterValidator(make_observer)]


class HvBaseModel(BaseModel):
    """
    Base pydantic model to use for type checking
    """

    # Disable sending extra fields, only fields in
    # the model are allowed
    model_config = ConfigDict(extra="forbid")

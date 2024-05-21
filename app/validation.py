"""
Contains validation related functions
"""

from typing_extensions import Annotated
from astropy.time import Time
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


class HvBaseModel(BaseModel):
    """
    Base pydantic model to use for type checking
    """

    # Disable sending extra fields, only fields in
    # the model are allowed
    model_config = ConfigDict(extra="forbid")

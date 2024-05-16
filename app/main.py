from pydantic import BaseModel, ValidationError, ConfigDict
from flask import Flask, request
from hgs2hpc import hgs2hpc
from normalizer import normalize_hpc

app = Flask("Helioviewer")


class HvBaseModel(BaseModel):
    """
    Base pydantic model to use for type checking
    """

    # Disable sending extra fields, only fields in
    # the model are allowed
    model_config = ConfigDict(extra="forbid")


class Hgs2HpcQueryParameters(HvBaseModel):
    lat: float
    lon: float
    obstime: str


@app.route("/hgs2hpc", methods=["GET"])
def _hgs2hpc():
    try:
        params = Hgs2HpcQueryParameters(**request.args)
        coord = hgs2hpc(params.lat, params.lon, params.obstime)
        return {"x": coord.Tx.value, "y": coord.Ty.value}
    except ValidationError as e:
        return e.errors(), 400


class NormalizeHpcQueryParameters(HvBaseModel):
    x: float
    y: float
    obstime: str

@app.route("/hpc", methods=["GET"])
def _normalize_hpc():
    try:
        params = NormalizeHpcQueryParameters(**request.args)
        coord = normalize_hpc(params.x, params.y, params.obstime)
        return {"x": coord.Tx.value, "y": coord.Ty.value}
    except ValidationError as e:
        return e.errors(), 400


@app.route("/flask-health-check")
def flask_health_check():
    return "success"

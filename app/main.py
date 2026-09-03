from typing import Annotated, List, Union

from astropy.time import Time
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ConfigDict, Field

from hgs2hpc import hgs2hpc, hgs2hpc_batch
from hgc2hpc import hgc2hpc, hgc2hpc_batch
from normalizer import normalize_hpc, normalize_hpc_batch, gse_frame, jsonify_skycoord
from hpc_response import hpc_dict
from ephemeris import get_position
from validation import AstropyTime, HvBaseModel, SunpyObserver, VALID_OBSERVERS

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# The helioprojective handlers deliberately have no response_model: FastAPI
# would then filter the response down to the declared fields, so any key added
# later would be silently dropped, and it would push every item of a batch
# through pydantic validation. These OpenAPI-only examples document the shape
# in /docs without imposing either.
_HPC_RESPONSE = {
    200: {
        "content": {
            "application/json": {
                "example": {"x": 477.6893, "y": -9.1213, "visible": False}
            }
        }
    }
}

_HPC_BATCH_RESPONSE = {
    200: {
        "content": {
            "application/json": {
                "example": {
                    "coordinates": [
                        {"x": 0.0, "y": 10.6243, "visible": True},
                        {"x": 477.6893, "y": -9.1213, "visible": False},
                    ]
                }
            }
        }
    }
}


class Hgs2HpcQueryParameters(HvBaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float
    coord_time: AstropyTime
    # Defaults to coord_time via constructor if None
    target: Union[AstropyTime, None] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.target is None:
            self.target = self.coord_time


@app.get(
    "/hgs2hpc",
    summary="Convert Heliographic Stonyhurst coordinate to Helioprojective coordinate in Helioviewer's POV",
    responses=_HPC_RESPONSE,
)
# def _hgs2hpc(lat: float, lon: float, coord_time: str, target: Union[str, None] = None):
def _hgs2hpc(params: Annotated[Hgs2HpcQueryParameters, Query()]):
    "Convert a latitude/longitude coordinate to the equivalent helioprojective coordinate at the given target time"
    #    try:
    coord = hgs2hpc(params.lat, params.lon, params.coord_time, params.target)
    return hpc_dict(coord)


class Hgs2HpcCoordInput(HvBaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float
    coord_time: AstropyTime


class Hgs2HpcBatchInput(HvBaseModel):
    coordinates: List[Hgs2HpcCoordInput]
    target: AstropyTime


@app.post(
    "/hgs2hpc",
    summary="Convert Heliographic Stonyhurst coordinate to Helioprojective coordinate in Helioviewer's POV",
    responses=_HPC_BATCH_RESPONSE,
)
def _hgs2hpc_post(params: Hgs2HpcBatchInput):
    "Convert a latitude/longitude coordinate to the equivalent helioprojective coordinate at the given target time"
    # Prepare coordinates for batch processing
    coords_input = [
        {"lat": c.lat, "lon": c.lon, "coord_time": c.coord_time}
        for c in params.coordinates
    ]

    results = hgs2hpc_batch(coords_input, params.target)

    return {"coordinates": results}


_OBSERVER_DESC = (
    "Solar-system body the Carrington coordinate is observed from "
    "(case-insensitive). Defaults to earth. Must be one of: "
    f"{', '.join(VALID_OBSERVERS)}. Any other value returns HTTP 422."
)


class Hgc2HpcQueryParameters(HvBaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float
    coord_time: AstropyTime
    observer: SunpyObserver = Field(default="earth", description=_OBSERVER_DESC)
    # Defaults to coord_time via constructor if None
    target: Union[AstropyTime, None] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.target is None:
            self.target = self.coord_time


@app.get(
    "/hgc2hpc",
    summary="Convert Heliographic Carrington coordinate to Helioprojective coordinate in Helioviewer's POV",
    responses=_HPC_RESPONSE,
)
def _hgc2hpc(params: Annotated[Hgc2HpcQueryParameters, Query()]):
    "Convert a Carrington latitude/longitude coordinate to the equivalent helioprojective coordinate at the given target time"
    coord = hgc2hpc(
        params.lat, params.lon, params.coord_time, params.target, params.observer
    )
    return hpc_dict(coord)


class Hgc2HpcCoordInput(HvBaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float
    coord_time: AstropyTime


class Hgc2HpcBatchInput(HvBaseModel):
    coordinates: List[Hgc2HpcCoordInput] = Field(
        description="One or more Carrington coordinates to convert."
    )
    target: AstropyTime
    # One observer applied to every coordinate in the batch; defaults to earth
    observer: SunpyObserver = Field(default="earth", description=_OBSERVER_DESC)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "coordinates": [
                    {"lat": 0, "lon": 117.7, "coord_time": "2012-01-01 00:00:00"},
                    {"lat": 10, "lon": 20, "coord_time": "2013-06-01 00:00:00"},
                ],
                "target": "2024-01-02 00:00:00",
                "observer": "earth",
            }
        },
    )


@app.post(
    "/hgc2hpc",
    summary="Convert Heliographic Carrington coordinate to Helioprojective coordinate in Helioviewer's POV",
    responses=_HPC_BATCH_RESPONSE,
)
def _hgc2hpc_post(params: Hgc2HpcBatchInput):
    "Convert Carrington latitude/longitude coordinates to the equivalent helioprojective coordinates at the given target time"
    coords_input = [
        {"lat": c.lat, "lon": c.lon, "coord_time": c.coord_time}
        for c in params.coordinates
    ]

    results = hgc2hpc_batch(coords_input, params.target, params.observer)

    return {"coordinates": results}


class NormalizeHpcQueryParameters(HvBaseModel):
    x: float
    y: float
    coord_time: AstropyTime
    # Defaults to coord_time via constructor if None
    target: Union[AstropyTime, None] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.target is None:
            self.target = self.coord_time


@app.get(
    "/hpc",
    summary="Get HPC coordinate for Helioviewer POV",
    responses=_HPC_RESPONSE,
)
def _normalize_hpc(params: Annotated[NormalizeHpcQueryParameters, Query()]):
    coord = normalize_hpc(params.x, params.y, params.coord_time, params.target)
    return hpc_dict(coord)


class HpcCoordInput(HvBaseModel):
    x: float
    y: float
    coord_time: AstropyTime


class HpcBatchInput(HvBaseModel):
    coordinates: List[HpcCoordInput]
    target: AstropyTime


@app.post(
    "/hpc",
    summary="Batch normalize HPC coordinates for Helioviewer POV",
    responses=_HPC_BATCH_RESPONSE,
)
def _normalize_hpc_post(params: HpcBatchInput):
    "Normalize multiple HPC coordinates to Helioviewer's POV at the given target time"
    coords_input = [
        {"x": c.x, "y": c.y, "coord_time": c.coord_time} for c in params.coordinates
    ]

    results = normalize_hpc_batch(coords_input, params.target)

    return {"coordinates": results}


class GSECoordInput(HvBaseModel):
    x: float
    y: float
    z: float
    time: AstropyTime


class GSEInput(HvBaseModel):
    coordinates: List[GSECoordInput]


@app.post("/gse2frame", summary="Convert GSE coordinates to Helioviewer 3D coordinates")
def _normalize_gse(params: GSEInput):
    coords = map(lambda c: gse_frame(c.x, c.y, c.z, c.time), params.coordinates)
    return {"coordinates": list(coords)}


class PositionInput(HvBaseModel):
    start: AstropyTime
    stop: AstropyTime


@app.get("/position/{observatory}")
def _get_position(observatory: str, start: AstropyTime, stop: AstropyTime):
    return {"coordinates": jsonify_skycoord(get_position(observatory, start, stop))}


@app.get("/health-check", include_in_schema=False)
def health_check():
    """
    Performs a simple self test to make sure functions used will run
    without exceptions
    """
    normalize_hpc(515, -342, "2012-07-05 13:01:46", "2012-07-05 13:01:46")
    hgs2hpc(9, 9, "2024-01-01", "2024-01-02")
    hgc2hpc(9, 9, "2024-01-01", "2024-01-02")
    gse_frame(0, 0, 0, "2024-01-02")
    jsonify_skycoord(get_position("SDO", Time("2025-01-01"), Time("2025-01-01")))
    return "success"

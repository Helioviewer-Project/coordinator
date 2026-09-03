# Coordinate
This python-based http API supports the main Helioviewer API
(PHP) by providing interfaces to functions written in python.

This allows Helioviewer to take advantage of libraries
in the python ecosystem (i.e. sunpy, astropy) without needing
to fully migrate the Helioviewer back-end to python. The
API is meant to run in parallel with Helioviewer.

## Usage
Running with docker:
```
docker run --rm -t ghcr.io/helioviewer-project/coordinator
```

Running manually with python
```
pip install -r requirements.txt
python -m fastapi run main.py
```

## Routes

The server hosts the following routes

### GET /hgs2hpc

Convert a heliographic stonyhurst coordinate into a helioprojective coordinate.

| query parameter | description |
|-----------------|-------------|
| lat             | Latitude coordinate in degrees |
| lon             | Longitude coordinate in degrees |
| coord_time      | Time that the measurement was taken |
| target          | (Optional) Desired observation time. Applies differential rotation |

Returns:
```
{ x: float, y: float, visible: bool }
```
See [Visibility](#visibility) for what `visible` means.

### GET /hgc2hpc

Convert a heliographic carrington coordinate into a helioprojective coordinate.
Carrington longitude is observer-dependent (it accounts for light travel time),
so an observer is required; it defaults to earth.

| query parameter | description |
|-----------------|-------------|
| lat             | Latitude coordinate in degrees |
| lon             | Carrington longitude coordinate in degrees |
| coord_time      | Time that the measurement was taken |
| target          | (Optional) Desired observation time. Applies differential rotation |
| observer        | (Optional) Solar-system body the coordinate is observed from (case-insensitive). Defaults to earth. See [valid observers](#valid-observers) below; any other value returns 422 |

Returns:
```
{ x: float, y: float, visible: bool }
```
See [Visibility](#visibility) for what `visible` means.

#### Valid observers

`observer` (on both the GET and POST routes) must be one of the solar-system
bodies sunpy can resolve (case-insensitive). Any other value returns HTTP 422.

```
earth, earth-moon-barycenter, jupiter, mars, mercury, moon,
neptune, saturn, sun, uranus, venus
```

### POST /hgc2hpc

Batch version of `GET /hgc2hpc`: convert a list of heliographic carrington
coordinates (one or more) against a single target observation time. The
optional `observer` applies to every coordinate in the batch, defaults to
earth, and follows the same [valid observers](#valid-observers) rule.

```json
{
    "coordinates": [
        { "lat": 0, "lon": 117.7, "coord_time": "2012-01-01 00:00:00" },
        { "lat": 10, "lon": 20, "coord_time": "2013-06-01 00:00:00" }
    ],
    "target": "2024-01-02 00:00:00",
    "observer": "earth"
}
```

Returns:
```json
{
    "coordinates": [
        { "x": float, "y": float, "visible": bool },
        ...
    ]
}
```
See [Visibility](#visibility) for what `visible` means.

### GET /hpc

Normalize a helioprojective coordinate into Helioviewer's coordinate frame.

| query parameter | description |
|-----------------|-------------|
| x               | X position in arcseconds |
| y               | Y position in arcseconds |
| coord_time      | Time that the measurement was taken |
| target          | (Optional) Desired observation time. Applies differential rotation |

Returns:
```
{ x: float, y: float, visible: bool }
```
See [Visibility](#visibility) for what `visible` means.

### Visibility

Every helioprojective response (`/hgs2hpc`, `/hgc2hpc`, `/hpc`; GET and POST)
includes a `visible` boolean: `false` means the opaque Sun hides the point from
Helioviewer's observer.

Helioprojective `(x, y)` is a projection onto the plane of the sky, so a point
on the *far* side of the Sun projects back inside the solar disk and is
otherwise indistinguishable from a near-side point at the same `(x, y)`. For
example, a Stonyhurst coordinate at `lon=150` on 2012-06-01 returns
`x = 477.7`, `y = -9.1` — comfortably inside the ~945 arcsecond disk — but
`"visible": false`.

Caveats:

* **`visible` is not "on-disk".** A point beyond the limb is visible at any
  depth. To test for on-disk, compare `sqrt(x² + y²)` against the apparent
  solar radius (~945 arcseconds at 1 AU).
* **The visible cap is slightly smaller than a hemisphere.** The limb sits at
  `arccos(rsun / D) ≈ 89.73°`, so a Stonyhurst point at `lon=90` is already
  `"visible": false`.
* **On `/hgc2hpc`, `observer` does not affect `visible`.** It only resolves the
  input Carrington longitude's light-travel correction; visibility is always
  judged from Helioviewer's observer.
* `visible` is evaluated **after** differential rotation to `target`, so a
  feature visible at `coord_time` may be hidden at a later `target`.

### POST /gse2frame

Transforms a list of GSE coordinates to Heliographic Stonyhurst coordinates using
a constant frame of reference. The reference frame is the coordinate frame used
for Heliographic Stonyhurst at 2025-01-01 00:00:00 UTC. All coordinate
transformations are done using sunpy and assume the sun remains at the origin
of the system.

```json
{
    "coordinates": [
        {
            "x": number in kilometers,
            "y": number in kilometers,
            "z": number in kilometers,
            "time": string (Y-m-d H:M:S)
        },
        ...
    ]
}
```


Returns the same format, but with the point in the new coordinate frame
```json
{
    "coordinates": [
        {
            "x": number,
            "y": number,
            "z": number,
            "time: string (Y-m-d H:M:S)
        },
        ...
    ]
}
```

### GET /position/{observatory}

Get the position of an observatory over a time range. The `observatory` path
parameter is any body sunpy can resolve (e.g. `SDO`, `SOHO`, `STEREO_A`).

| query parameter | description |
|-----------------|-------------|
| start           | Start of the time range |
| stop            | End of the time range |

Returns a list of positions (in kilometers) in Helioviewer's 3D frame:
```json
{
    "coordinates": [
        { "x": number, "y": number, "z": number, "time": "Y-m-d H:M:S" },
        ...
    ]
}
```

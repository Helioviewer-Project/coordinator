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
docker compose up --wait
```

Running manually with python
```
pip install -r requirements.txt
python -m flask --app main run
```

## Routes

The server hosts the following routes

### GET /hgs2hpc

Convert a heliographic stonyhurst coordinate into a helioprojective coordinate.

| query parameter | description |
|-----------------|-------------|
| lat             | Latitude coordinate in degrees |
| lon             | Longitude coordinate in degrees |
| obstime         | Time that the measurement was taken |

Returns:
```
{ x: float, y: float }
```
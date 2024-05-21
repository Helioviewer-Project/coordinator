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
docker run --rm -t dgarciabriseno/hv-coordinator
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
| event_time      | Time that the measurement was taken |
| target          | (Optional) Desired observation time. Applies differential rotation |

Returns:
```
{ x: float, y: float }
```

### GET /hpc

Normalize a helioprojective coordinate into Helioviewer's coordinate frame.

| query parameter | description |
|-----------------|-------------|
| x               | X position in arcseconds |
| y               | Y position in arcseconds |
| event_time      | Time that the measurement was taken |
| target          | (Optional) Desired observation time. Applies differential rotation |

Returns:
```
{ x: float, y: float }
```
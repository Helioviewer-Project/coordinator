# Carrington endpoints

Convert **Heliographic Carrington** coordinates to **Helioprojective**
coordinates in Helioviewer's point of view.

A Carrington coordinate (latitude, Carrington longitude) names a point fixed to
the Sun's rotating surface. These endpoints turn such a point into the `(x, y)`
Helioprojective coordinate — arcseconds on the plane of the sky — as it would
appear from Helioviewer's vantage point.

## Two times, one job each

| field | meaning |
| --- | --- |
| `coord_time` | When the lat/lon was *measured*. Fixes the Sun's orientation to start from. |
| `target` | The time you want the result *for*. Solar differential rotation is applied from `coord_time` to `target`. If equal to `coord_time` (or omitted on GET), no rotation is applied — just a frame conversion. |

## Observer

Carrington longitude is *apparent*: it includes the light-travel time from the
Sun to the observer (~0.08° of solar rotation for Earth), so sunpy requires an
observer to transform out of the frame. The `observer` defaults to `earth` —
matching the convention of Carrington coordinates in solar data products (NOAA
active regions, HMI synoptic maps) — but may be any solar-system body sunpy can
resolve.

**Valid observers** (case-insensitive); any other value returns `HTTP 422`:

```
earth, earth-moon-barycenter, jupiter, mars, mercury, moon,
neptune, saturn, sun, uranus, venus
```

## `GET /hgc2hpc`

Convert a single Carrington coordinate to a Helioprojective coordinate.

| query parameter | type | description |
| --- | --- | --- |
| `lat` | float | **required** — latitude in degrees, `-90 ≤ lat ≤ 90`. |
| `lon` | float | **required** — Carrington longitude in degrees. |
| `coord_time` | string | **required** — time the coordinate was measured. |
| `target` | string | optional — desired observation time; applies differential rotation. Defaults to `coord_time`. |
| `observer` | string | optional — solar-system body the coordinate is observed from. Defaults to `earth`. |

**Response `200`** — `x`, `y` in arcseconds, plus a `visible` flag
(see [Visibility](#visibility)):

```json
{ "x": 9.060967563950392, "y": 49.638500848914674, "visible": true }
```

**Example:**

```bash
curl "https://coordinator.helioviewer.org/hgc2hpc?lat=0&lon=117.7&coord_time=2012-01-01%2000:00:00&target=2012-01-01%2001:00:00&observer=earth"
```

**Errors** — `422` for missing `lat`/`lon`/`coord_time`, `lat` out of range,
an unparseable time, or an unknown `observer`.

## `POST /hgc2hpc`

Batch version of `GET /hgc2hpc`. Convert one or more Carrington coordinates
against a single `target` and `observer`; each coordinate keeps its own
`coord_time`.

**Request body** (`application/json`):

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

| field | description |
| --- | --- |
| `coordinates` | **required** — list of `{lat, lon, coord_time}`; `lat` must be `-90..90`. |
| `target` | **required** — observation time applied to every coordinate. |
| `observer` | optional — one observer for the whole batch. Defaults to `earth`. |

**Response `200`** — one `{x, y, visible}` per input, in the same order; an
empty list returns `{"coordinates": []}`:

```json
{
  "coordinates": [
    { "x": 236.27, "y": -49.34, "visible": false },
    { "x": 926.12, "y": 156.49, "visible": false }
  ]
}
```

Both coordinates in this example are on the far side of the Sun at the target
time — note that the first still projects to `x = 236″`, well inside the disk.
That is exactly what `visible` is for.

**Errors** — `422` for missing `coordinates`/`target`, `lat` out of range, an
unparseable time, or an unknown `observer`.

## Visibility

Every response carries a `visible` boolean: `false` means the opaque Sun hides
the point from Helioviewer's observer.

Helioprojective `(x, y)` is a projection onto the plane of the sky, so a point
on the far side of the Sun projects back *inside* the solar disk and is
otherwise indistinguishable from a near-side point at the same `(x, y)`. This
bites especially hard for Carrington coordinates, because Carrington longitude
is fixed to the rotating Sun — roughly half of all longitudes are on the far
side at any given time.

- **`visible` is not "on-disk".** A point beyond the limb is visible at any
  depth. To test for on-disk, compare `sqrt(x² + y²)` against the apparent
  solar radius (~945 arcseconds at 1 AU).
- **The visible cap is slightly smaller than a hemisphere** — the limb sits at
  `arccos(rsun / D) ≈ 89.73°`, not 90°.
- **`observer` does not affect `visible`.** It only resolves the input
  Carrington longitude's light-travel correction; visibility is always judged
  from Helioviewer's observer. `observer=mars` changes how the input longitude
  is interpreted, not who is looking.
- `visible` is evaluated **after** differential rotation to `target`, so a
  feature visible at `coord_time` may be hidden at a later `target`.

---

See also `GET /hgs2hpc` (Stonyhurst), and the interactive API docs at `/docs`
(Swagger) and `/redoc`.

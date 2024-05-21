import json
import pytest
from flask.testing import FlaskClient
from ..main import app


@pytest.fixture
def client():
    return app.test_client()


def test_hpc(client: FlaskClient):
    # Missing x
    response = client.get("/hpc?y=0&event_time=2012-01-01")
    assert response.status_code == 400
    # Missing y
    response = client.get("/hpc?x=0&event_time=2012-01-01")
    assert response.status_code == 400
    # Missing event_time
    response = client.get("/hpc?x=0&y=0")
    assert response.status_code == 400

    # Using RHESSI Flare 12070596 as the test subject
    # hpc_x = 515
    # hpc_y = -342
    response = client.get("/hpc?x=515&y=-342&event_time=2012-07-05+13:01:46")
    assert response.status_code == 200
    coord = json.loads(response.get_data())
    assert pytest.approx(coord["x"]) == 523.6178
    assert pytest.approx(coord["y"]) == -347.7228

    # Test invalid time
    response = client.get("/hgs2hpc?lat=0&lon=0&event_time=NotATime")
    assert response.status_code != 500

    # Converting to target time
    response = client.get(
        "/hpc?x=0&y=0&event_time=2012-01-01 00:00:00&target=2012-01-01 01:00:00"
    )
    assert response.status_code == 200
    coord = json.loads(response.get_data())
    # The x coordinate is expected to move to the right approximately 9 arcseconds
    assert 9 < coord["x"] and coord["x"] < 10


def test_hgs2hpc(client: FlaskClient):
    # Missing lat
    response = client.get("/hgs2hpc?lon=0&event_time=2012-01-01")
    assert response.status_code == 400
    # Missing lon
    response = client.get("/hgs2hpc?lat=0&event_time=2012-01-01")
    assert response.status_code == 400
    # Missing event_time
    response = client.get("/hgs2hpc?lat=0&lon=0")
    assert response.status_code == 400

    # Test invalid time
    response = client.get("/hgs2hpc?lat=0&lon=0&event_time=NotATime")
    assert response.status_code == 400

    # Typical request, in this case expect that the hpc x coordinate is 0
    response = client.get("/hgs2hpc?lat=0&lon=0&event_time=2012-01-01 00:00:00")
    assert response.status_code == 200
    coord = json.loads(response.get_data())
    assert coord["x"] == 0

    # Same as the above request, but change the target time to 1 hour ahead
    # This should apply the differential rotation and the x coordinate should
    # move to the right approximately 9 arcseconds
    response = client.get(
        "/hgs2hpc?lat=0&lon=0&event_time=2012-01-01 00:00:00&target=2012-01-01 01:00:00"
    )
    assert response.status_code == 200
    coord = json.loads(response.get_data())
    assert 9 < coord["x"] and coord["x"] < 10

    # Verify correct status is returned when an invalid latitude longitude
    # coordinate is given. latitude/longitude must be between -90 and 90 inclusive.
    # Sunpy has no restriction on longitude, so all values are allowed
    # Test latitude is greater than 90
    response = client.get("/hgs2hpc?lat=90.1&lon=0&event_time=2012-01-01 00:00:00")
    assert response.status_code == 400
    data = json.loads(response.get_data())
    assert data[0]["loc"][0] == "lat"

    # Test latitude is less than -90
    response = client.get("/hgs2hpc?lat=-90.1&lon=0&event_time=2012-01-01 00:00:00")
    assert response.status_code == 400
    data = json.loads(response.get_data())
    assert data[0]["loc"][0] == "lat"


def test_healthcheck(client: FlaskClient):
    assert client.get("/flask-health-check").get_data(as_text=True) == "success"

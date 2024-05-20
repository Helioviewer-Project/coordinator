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
    assert pytest.approx(coord['x']) == 523.6178
    assert pytest.approx(coord['y']) == -347.7228

    # Converting to target time
    response = client.get("/hpc?x=0&y=0&event_time=2012-01-01 00:00:00&target=2012-01-01 01:00:00")
    assert response.status_code == 200
    coord = json.loads(response.get_data())
    # The x coordinate is expected to move to the right approximately 9 arcseconds
    assert (coord['x'] - 9) > 0

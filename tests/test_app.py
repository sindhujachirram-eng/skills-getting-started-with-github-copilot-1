from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "Gym Class" in activities
    assert activities["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity():
    # Arrange
    email = "test.student@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_is_rejected():
    # Arrange
    email = "duplicate.student@mergington.edu"
    first = client.post(f"/activities/Gym Class/signup?email={email}")
    assert first.status_code == 200

    # Act
    second = client.post(f"/activities/Gym Class/signup?email={email}")

    # Assert
    assert second.status_code == 400
    assert second.json()["detail"] == "Student is already registered for this activity"


def test_remove_participant():
    # Arrange
    email = "removable.student@mergington.edu"
    signup = client.post(f"/activities/Gym Class/signup?email={email}")
    assert signup.status_code == 200

    # Act
    response = client.delete(f"/activities/Gym Class/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Gym Class"}

    activities = client.get("/activities").json()
    assert email not in activities["Gym Class"]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange

    # Act
    response = client.delete("/activities/Chess Club/participants?email=missing@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"

"""
Tests for the Mergington High School Activities API
Using Arrange-Act-Assert (AAA) pattern
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import copy

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Wednesdays, 3:30 PM - 4:45 PM",
            "max_participants": 20,
            "participants": []
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": []
        },
        "Basketball League": {
            "description": "Join our competitive basketball team and compete in school tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and play matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 10,
            "participants": []
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(copy.deepcopy(original))


# GET /activities tests
class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Activities are already in the database
        Act: GET /activities
        Assert: Response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_participant_count(self, client, reset_activities):
        """
        Arrange: Gym Class has 2 participants
        Act: GET /activities
        Assert: Response includes correct participant count
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["Gym Class"]["participants"]) == 2
        assert "john@mergington.edu" in data["Gym Class"]["participants"]
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """
        Arrange: Activities exist with all required fields
        Act: GET /activities
        Assert: Each activity has description, schedule, max_participants, and participants fields
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


# POST /signup tests
class TestSignupForActivity:
    def test_signup_success(self, client, reset_activities):
        """
        Arrange: New student email and available activity
        Act: POST to signup endpoint
        Assert: Student is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert "Signed up" in response.json()["message"]
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        Arrange: Student already registered for activity
        Act: Try to signup again with same email
        Assert: Returns 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Activity doesn't exist
        Act: POST to signup endpoint
        Assert: Returns 404 error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_to_empty_activity_succeeds(self, client, reset_activities):
        """
        Arrange: Activity with no participants
        Act: POST to signup endpoint
        Assert: Student is successfully added
        """
        # Arrange
        activity_name = "Debate Team"  # Empty activity
        email = "new.speaker@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
    
    def test_signup_multiple_students_to_same_activity(self, client, reset_activities):
        """
        Arrange: Activity with existing participants
        Act: Signup two different students
        Assert: Both students are added
        """
        # Arrange
        activity_name = "Science Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


# DELETE /unregister tests
class TestUnregisterFromActivity:
    def test_unregister_success(self, client, reset_activities):
        """
        Arrange: Student registered for activity
        Act: DELETE to unregister endpoint
        Assert: Student is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_not_registered_returns_400(self, client, reset_activities):
        """
        Arrange: Student not registered for activity
        Act: DELETE to unregister endpoint
        Assert: Returns 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Activity doesn't exist
        Act: DELETE to unregister endpoint
        Assert: Returns 404 error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """
        Arrange: Student registered for activity
        Act: Unregister, then signup again
        Assert: Can register again after unregistering
        """
        # Arrange
        activity_name = "Gym Class"
        email = "newuser@mergington.edu"
        
        # Act - signup first time
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response2.status_code == 200
        
        # Signup again
        response3 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response3.status_code == 200
        assert email in activities[activity_name]["participants"]


# GET / redirect test
class TestRootEndpoint:
    def test_root_redirects_to_index(self, client):
        """
        Arrange: Request to root path
        Act: GET /
        Assert: Redirects to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
    
    def test_root_redirect_location_is_correct(self, client):
        """
        Arrange: Request to root path with follow_redirects
        Act: GET /
        Assert: Final location is index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert "index.html" in response.headers["location"]

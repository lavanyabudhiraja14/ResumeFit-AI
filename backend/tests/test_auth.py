"""Unit and Integration Tests for Authentication, User Profile, and Interest Onboarding."""

import pytest
from app.core.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.core.interest_taxonomy import VALID_INTEREST_IDS, get_all_categories
from app.core.database import get_db_connection


@pytest.fixture(autouse=True)
def clean_test_db():
    """Ensure clean database state before each test."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users;")
        conn.commit()
    yield



def test_password_hashing_and_verification():
    """Verify passwords are securely hashed with salts and correctly verified."""
    raw_pass = "SuperSecret123!"
    hashed = hash_password(raw_pass)

    assert hashed != raw_pass
    assert "$" in hashed
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_creation_and_decoding():
    """Verify HMAC-SHA256 bearer tokens are signed, verified, and validated."""
    user_id = "test-user-uuid-123"
    email = "engineer@example.com"
    token = create_access_token(user_id=user_id, email=email, expires_delta_seconds=3600)

    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert payload["exp"] > payload["iat"]


def test_interest_taxonomy_structure(client):
    """Verify the single centralized interest taxonomy returns standard categories and IDs."""
    response = client.get("/api/interests")
    assert response.status_code == 200
    data = response.json()

    assert "categories" in data
    assert data["total_interests"] == 18
    assert len(data["categories"]) == 5

    category_names = [c["category"] for c in data["categories"]]
    assert "Software Development" in category_names
    assert "Data & AI" in category_names
    assert "Infrastructure" in category_names
    assert "Design & Product" in category_names
    assert "Other Technology" in category_names

    # Check key stable IDs are present
    all_item_ids = [item["id"] for cat in data["categories"] for item in cat["items"]]
    for expected_id in ["frontend", "backend", "fullstack", "datascience", "ai", "cloud", "devops", "uiux"]:
        assert expected_id in all_item_ids


def test_signup_flow(client):
    """Test user signup creates account, returns token, and initializes onboarding state."""
    payload = {
        "name": "Jane Engineer",
        "email": "jane.engineer@example.com",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    user = data["user"]
    assert user["name"] == "Jane Engineer"
    assert user["email"] == "jane.engineer@example.com"
    assert user["interests"] == []
    assert user["onboarding_completed"] is False


def test_duplicate_signup_rejection(client):
    """Signup with existing email must return 400 Bad Request."""
    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "Password123!",
    }
    res1 = client.post("/api/auth/signup", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/signup", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_login_flow(client):
    """Test login with correct credentials returns valid bearer token and user summary."""
    # Register user
    signup_payload = {
        "name": "Alex Smith",
        "email": "alex.smith@example.com",
        "password": "MyPassword2026!",
    }
    client.post("/api/auth/signup", json=signup_payload)

    # Login
    login_payload = {
        "email": "alex.smith@example.com",
        "password": "MyPassword2026!",
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alex.smith@example.com"


def test_login_invalid_credentials(client):
    """Test login with incorrect password or nonexistent user returns 401."""
    # Wrong password
    res1 = client.post(
        "/api/auth/login",
        json={"email": "alex.smith@example.com", "password": "WrongPassword!"},
    )
    assert res1.status_code == 401

    # Nonexistent user
    res2 = client.post(
        "/api/auth/login",
        json={"email": "ghost.user@example.com", "password": "AnyPassword123!"},
    )
    assert res2.status_code == 401


def test_protected_route_access(client):
    """Test GET /api/users/me requires valid Bearer token."""
    # No auth header -> 401
    res_unauth = client.get("/api/users/me")
    assert res_unauth.status_code == 401

    # Invalid token -> 401
    res_invalid = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert res_invalid.status_code == 401

    # Valid token -> 200
    signup_res = client.post(
        "/api/auth/signup",
        json={"name": "Dev User", "email": "dev.user@example.com", "password": "DevPassword123!"},
    )
    token = signup_res.json()["access_token"]

    res_auth = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_auth.status_code == 200
    profile = res_auth.json()
    assert profile["email"] == "dev.user@example.com"
    assert profile["name"] == "Dev User"
    assert profile["onboarding_completed"] is False


def test_user_interests_onboarding_and_updates(client):
    """Test full interest onboarding flow: empty interests -> multiple selection -> update -> persistence."""
    # 1. Signup
    signup_res = client.post(
        "/api/auth/signup",
        json={"name": "Career Seeker", "email": "seeker@example.com", "password": "SecurePassword123!"},
    )
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check initial interests (empty)
    res_initial = client.get("/api/users/me/interests", headers=headers)
    assert res_initial.status_code == 200
    assert res_initial.json()["interests"] == []
    assert res_initial.json()["onboarding_completed"] is False

    # 3. Submit multiple interests selection
    chosen_interests = ["frontend", "backend", "ai"]
    res_update = client.put(
        "/api/users/me/interests",
        json={"interests": chosen_interests},
        headers=headers,
    )
    assert res_update.status_code == 200
    updated_data = res_update.json()
    assert updated_data["interests"] == chosen_interests
    assert updated_data["onboarding_completed"] is True
    assert len(updated_data["interest_details"]) == 3

    # Details include category and readable names
    names = [d["name"] for d in updated_data["interest_details"]]
    assert "Frontend Development" in names
    assert "Backend Development" in names
    assert "Artificial Intelligence" in names

    # 4. Fetch profile to confirm onboarding_completed is true
    res_profile = client.get("/api/users/me", headers=headers)
    assert res_profile.status_code == 200
    assert res_profile.json()["onboarding_completed"] is True
    assert res_profile.json()["interests"] == chosen_interests

    # 5. Subsequent login reflects onboarding_completed is true
    login_res = client.post(
        "/api/auth/login",
        json={"email": "seeker@example.com", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    assert login_res.json()["user"]["onboarding_completed"] is True
    assert login_res.json()["user"]["interests"] == chosen_interests

    # 6. Update interests with a different combination
    new_interests = ["cloud", "devops", "cybersecurity", "sre"]
    res_update2 = client.put(
        "/api/users/me/interests",
        json={"interests": new_interests},
        headers=headers,
    )
    assert res_update2.status_code == 200
    assert res_update2.json()["interests"] == new_interests


def test_invalid_interest_ids_rejected(client):
    """Test that invalid interest IDs are rejected with 422."""
    signup_res = client.post(
        "/api/auth/signup",
        json={"name": "Validator User", "email": "validator@example.com", "password": "Password123!"},
    )
    token = signup_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Empty list
    res_empty = client.put("/api/users/me/interests", json={"interests": []}, headers=headers)
    assert res_empty.status_code == 422

    # Invalid ID
    res_invalid = client.put(
        "/api/users/me/interests",
        json={"interests": ["frontend", "not_a_real_interest_id"]},
        headers=headers,
    )
    assert res_invalid.status_code == 422

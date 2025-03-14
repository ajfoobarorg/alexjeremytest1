import requests
import uuid
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def log_test(name: str, response: requests.Response, expected_status: int):
    """Log test results with clear formatting"""
    status = "✅ PASS" if response.status_code == expected_status else "❌ FAIL"
    logger.info(f"\n{status} - {name}")
    logger.info(f"Expected status: {expected_status}, Got: {response.status_code}")
    logger.info(f"Response: {response.text}\n")
    return response.status_code == expected_status

def run_tests():
    passed = 0
    total = 0

    # Test 1: Signup with duplicate username
    def test_duplicate_username():
        nonlocal passed, total
        total += 1
        
        # First signup should succeed
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "username": "test_user",
            "email": "test1@example.com",
            "level": "0",
            "timezone": "UTC+00:00",
            "country": "US"
        })
        
        # Second signup with same username should fail
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "username": "test_user",
            "email": "test2@example.com",
            "level": "0",
            "timezone": "UTC+00:00",
            "country": "US"
        })
        if log_test("Duplicate Username", response, 400):
            passed += 1

    # Test 2: Signup with duplicate email
    def test_duplicate_email():
        nonlocal passed, total
        total += 1
        
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "username": "another_user",
            "email": "test1@example.com",  # Same email as first test
            "level": "0",
            "timezone": "UTC+00:00",
            "country": "US"
        })
        if log_test("Duplicate Email", response, 400):
            passed += 1

    # Test 3: Login with non-existent email
    def test_nonexistent_login():
        nonlocal passed, total
        total += 1
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "nonexistent@example.com"
        })
        if log_test("Login with Non-existent Email", response, 404):
            passed += 1

    # Test 4: Get profile with invalid ID
    def test_invalid_profile():
        nonlocal passed, total
        total += 1
        
        response = requests.get(f"{BASE_URL}/profile/{uuid.uuid4()}")
        if log_test("Get Invalid Profile", response, 404):
            passed += 1

    # Test 5: Update profile with invalid ID
    def test_invalid_profile_update():
        nonlocal passed, total
        total += 1
        
        response = requests.post(
            f"{BASE_URL}/profile/{uuid.uuid4()}", 
            json={"username": "new_name"}
        )
        if log_test("Update Invalid Profile", response, 404):
            passed += 1

    # Test 6: Get non-existent game
    def test_nonexistent_game():
        nonlocal passed, total
        total += 1
        
        response = requests.get(f"{BASE_URL}/games/{uuid.uuid4()}")
        if log_test("Get Non-existent Game", response, 404):
            passed += 1

    # Test 7: Make move in non-existent game
    def test_move_nonexistent_game():
        nonlocal passed, total
        total += 1
        
        response = requests.post(
            f"{BASE_URL}/games/{uuid.uuid4()}/move/0/0",
            params={"player_id": str(uuid.uuid4())}
        )
        if log_test("Move in Non-existent Game", response, 404):
            passed += 1

    # Test 8: Invalid matchmaking join (non-existent player)
    def test_invalid_matchmaking():
        nonlocal passed, total
        total += 1
        
        response = requests.post(
            f"{BASE_URL}/matchmaking/join",
            json={"player_id": str(uuid.uuid4())}
        )
        if log_test("Join Matchmaking with Invalid Player", response, 400):
            passed += 1

    # Run all tests
    logger.info("\n🏃 Starting Tests...\n")
    
    test_duplicate_username()
    test_duplicate_email()
    test_nonexistent_login()
    test_invalid_profile()
    test_invalid_profile_update()
    test_nonexistent_game()
    test_move_nonexistent_game()
    test_invalid_matchmaking()

    # Print summary
    logger.info(f"\n📊 Test Summary: {passed}/{total} tests passed")

if __name__ == "__main__":
    run_tests() 
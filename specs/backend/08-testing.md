# Testing Specification

This specification defines the testing requirements for the Ultimate Tic-Tac-Toe API.

## Test Categories

The test suite should include the following categories:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test interactions between components
3. **API Tests** - Test API endpoints using HTTP
4. **Regression Tests** - Test specific scenarios to ensure bugs don't reoccur

## Unit Tests

Unit tests should cover:

### Board Logic

- Test `Board` class functionality
  - Creation with/without initial state
  - Setting and getting values
  - Checking for winners (all possible win configurations)
  - Checking for full board conditions
  - Invalid position handling
  - Invalid value handling
  
- Test `MetaBoard` class functionality
  - Creation from a list of boards
  - Winner detection at meta level
  - Board playability checks
  - Full board detection
  - Invalid board index handling

### Game Service

- Test game creation
- Test move validation
  - Valid moves in correct boards
  - Invalid moves (wrong board, occupied position)
  - Next board determination
  - Time control handling
  - Win/loss/draw detection
- Test game resignation
- Test ELO calculations

### Player Service

- Test player creation
- Test player lookup
- Test ELO adjustment calculations
- Test player stats updates

### Matchmaking Service

- Test adding players to queue
- Test removing players from queue
- Test finding matches
- Test TTL expiration
- Test concurrent access scenarios

## Integration Tests

Integration tests should verify:

- Game flow from creation to completion
- Proper interaction between services
- Database persistence and retrieval
- Time tracking across moves
- ELO and stats updates after game completion

## API Tests

API tests should cover all endpoints:

- Authentication endpoints
  - Signup with valid/invalid data
  - Login with valid/invalid email
  - Logout functionality
  - Cookie setting and clearing

- Profile endpoints
  - Retrieving current user profile
  - Retrieving other player profiles
  - Updating profiles with valid/invalid data

- Game endpoints
  - Game creation
  - Making valid/invalid moves
  - Proper game state updates
  - Game completion scenarios
  - Time control enforcement

- Matchmaking endpoints
  - Joining/canceling matchmaking
  - Match finding and acceptance
  - TTL expiration handling

## Test Environment

### Test Database

- Tests should use a separate test database
- The test database should be reset before each test run
- Test data should be seeded consistently

### Mock Services

- External services should be mocked where appropriate
- Time-dependent operations should be mockable to avoid waiting in tests

## Test Coverage Requirements

- Aim for at least 80% code coverage
- Critical game logic should have near 100% coverage
- Edge cases should be thoroughly tested

## Performance Testing

- Test API response times under normal load
- Test matchmaking system with multiple concurrent users
- Test database performance with a large number of games/players

## Test Structure

Test files should be organized by:

1. Module being tested
2. Type of test (unit, integration, API)

Example:
```
tests/
  unit/
    test_board_logic.py
    test_game_service.py
    test_player_service.py
    test_matchmaking.py
  integration/
    test_game_flow.py
    test_matchmaking_flow.py
  api/
    test_auth_api.py
    test_profile_api.py
    test_game_api.py
    test_matchmaking_api.py
  regression/
    test_specific_bugs.py
```

## CI/CD Integration

Tests should be:

- Fast enough to run on every commit
- Reliable (no flaky tests)
- Parallelizable where possible
- Configured to run automatically in CI/CD pipeline

## Test Fixtures

Common test fixtures should include:

- Player fixtures with predefined attributes
- Game fixtures in various states
- Board fixtures with specific configurations
- Authentication helpers (login, session management)

## Regression Test Requirements

1. Each bug fix should have a corresponding regression test
2. Regression tests should clearly document the issue they prevent
3. Regression tests should be maintainable and not overly specific
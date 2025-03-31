import pytest
import os
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def real_backend_server():
    """Start a real backend server for HTTP-based testing.
    
    This fixture starts an actual server process for true end-to-end testing.
    """
    from tests.http_client import start_server_thread
    print("\n⚡ Starting real HTTP server for end-to-end testing...")
    server = start_server_thread()
    yield server
    print("\n🛑 Stopping real HTTP server...")
    # Server will be stopped by atexit handler

@pytest.fixture
def http_client(real_backend_server):
    """Create a real HTTP client for tests against a running server."""
    from tests.http_client import ApiClient
    print(f"\n🌐 Creating HTTP client for real server testing on port {real_backend_server.port}...")
    return ApiClient(real_backend_server.server_url)
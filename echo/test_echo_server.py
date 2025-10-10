import pytest
import requests
import time
from threading import Thread
from echo_server import serve


@pytest.fixture(scope="module")
def server():
    """Start echo server in background thread"""
    thread = Thread(target=serve, daemon=True)
    thread.start()
    time.sleep(0.5)  # Give server time to start
    yield "http://127.0.0.1:5000"
    # Server will stop when test process ends (daemon thread)


def test_basic_get_request(server):
    """Test basic GET request"""
    response = requests.get(f"{server}/test")
    assert response.status_code == 200
    assert "Request Method: GET" in response.text
    assert "Request Source:" in response.text
    assert "Response Status: 200 OK" in response.text


def test_get_with_custom_headers(server):
    """Test GET request with custom headers"""
    headers = {
        "X-Custom-Header": "TestValue",
        "Authorization": "Bearer token123"
    }
    response = requests.get(f"{server}/api/test", headers=headers)
    assert response.status_code == 200
    assert "X-Custom-Header: TestValue" in response.text
    assert "Authorization: Bearer token123" in response.text


def test_status_query_parameter_404(server):
    """Test status query parameter - 404"""
    response = requests.get(f"{server}/test?status=404")
    assert response.status_code == 404
    assert "Response Status: 404 Not Found" in response.text


def test_status_query_parameter_500(server):
    """Test status query parameter - 500"""
    response = requests.get(f"{server}/test?status=500")
    assert response.status_code == 500
    assert "Response Status: 500 Internal Server Error" in response.text


def test_status_query_parameter_201(server):
    """Test status query parameter - 201"""
    response = requests.get(f"{server}/test?status=201")
    assert response.status_code == 201
    assert "Response Status: 201 Created" in response.text


def test_different_paths(server):
    """Test different URL paths"""
    paths = ["/", "/api/users", "/test/path", "/some/nested/path"]
    for path in paths:
        response = requests.get(f"{server}{path}")
        assert response.status_code == 200
        assert f"Request Method: GET" in response.text


def test_default_status_on_invalid_code(server):
    """Test that invalid status codes default to 200"""
    response = requests.get(f"{server}/test?status=999")
    # Invalid HTTP status code should default to 200
    assert response.status_code == 200


def test_default_status_on_malformed_query(server):
    """Test that malformed status query defaults to 200"""
    response = requests.get(f"{server}/test?status=abc")
    assert response.status_code == 200


def test_user_agent_echo(server):
    """Test that User-Agent header is echoed"""
    headers = {"User-Agent": "CustomBot/1.0"}
    response = requests.get(f"{server}/test", headers=headers)
    assert response.status_code == 200
    assert "User-Agent: CustomBot/1.0" in response.text

def test_root_endpoint(client):
    """
    Test the root endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ticket System API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_check(client):
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

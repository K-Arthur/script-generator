import pytest
from fastapi.testclient import TestClient
from app.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_content():
    return """
    Artificial Intelligence (AI) is revolutionizing industries across the globe.
    From healthcare to transportation, AI technologies are creating new
    possibilities and solving complex problems. Machine learning, a subset of AI,
    enables systems to learn and improve from experience.
    """

def test_get_templates(client):
    response = client.get("/api/templates")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "templates" in response.json()
    templates = response.json()["templates"]
    assert isinstance(templates, dict)
    assert "documentary" in templates
    assert "educational" in templates
    assert "storytelling" in templates

def test_generate_script(client, sample_content):
    response = client.post(
        "/api/generate-script",
        json={
            "content": sample_content,
            "template_name": "documentary",
            "highlighted_concept": "AI",
            "previous_topic": "Technology Basics"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"

def test_get_script_status_not_found(client):
    response = client.get("/api/script-status/nonexistent_id")
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

def test_validate_script(client):
    script = """
    The Impact of Artificial Intelligence

    Artificial Intelligence has become an integral part of our daily lives.
    From smartphones to smart homes, AI technologies are everywhere. This
    revolutionary technology is changing how we work, live, and interact.

    One of the most significant applications of AI is in healthcare. Machine
    learning algorithms can analyze medical images, predict patient outcomes,
    and assist in diagnosis. This has led to more accurate and faster
    medical decisions.

    Looking ahead, AI will continue to evolve and shape our future. While
    challenges exist, the benefits of AI are undeniable. The key lies in
    responsible development and implementation.
    """
    
    response = client.post(
        "/api/validate-script",
        json={
            "script": script,
            "template_name": "documentary"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "validation" in data
    validation = data["validation"]
    assert "readability" in validation
    assert "structure" in validation
    assert "engagement" in validation

def test_export_script(client):
    script = "Test script content for export testing."
    
    # Test TXT export
    response = client.post(
        "/api/export-script",
        json={
            "script": script,
            "format": "txt"
        }
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain"
    assert response.headers["Content-Disposition"] == 'attachment; filename="script.txt"'
    assert response.content.decode() == script
    
    # Test HTML export
    response = client.post(
        "/api/export-script",
        json={
            "script": script,
            "format": "html"
        }
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html"
    assert response.headers["Content-Disposition"] == 'attachment; filename="script.html"'
    assert "<!DOCTYPE html>" in response.content.decode()
    
    # Test Markdown export
    response = client.post(
        "/api/export-script",
        json={
            "script": script,
            "format": "md"
        }
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/markdown"
    assert response.headers["Content-Disposition"] == 'attachment; filename="script.md"'

def test_invalid_export_format(client):
    response = client.post(
        "/api/export-script",
        json={
            "script": "Test script",
            "format": "invalid"
        }
    )
    assert response.status_code == 400
    assert "Error exporting script" in response.json()["detail"]

def test_upload_file(client):
    content = b"Test content for file upload"
    files = {"file": ("test.txt", content, "text/plain")}
    response = client.post("/api/upload-file", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["content"] == content.decode()

def test_upload_file_invalid(client):
    response = client.post("/api/upload-file")
    assert response.status_code == 422  # Validation error

def test_generate_script_invalid_request(client):
    response = client.post(
        "/api/generate-script",
        json={
            "content": ""  # Empty content should fail
        }
    )
    assert response.status_code == 422  # Validation error

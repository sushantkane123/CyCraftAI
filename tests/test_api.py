"""
Pytest Integration Tests for CyCraft AI FastAPI Backend
"""

from fastapi.testclient import TestClient
from cycraft.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_alerts():
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    assert len(alerts) >= 1
    assert "ALT-" in alerts[0]["id"]


def test_get_assets():
    response = client.get("/api/v1/asm/assets")
    assert response.status_code == 200
    assets = response.json()
    assert isinstance(assets, list)
    assert len(assets) >= 1
    assert "core-auth-api" in assets[0]["name"]


def test_trigger_attack():
    response = client.post("/api/v1/alerts/trigger-simulated-attack", json={"scenario": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "INTERCEPTED"
    assert "alert_id" in data


def test_ingest_real_logs():
    """Test the new real log ingestion feature"""
    logs = """powershell.exe -enc SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0AA==
smbclient -L //DC01 -U anonymous
aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AdministratorAccess"""

    response = client.post(
        "/api/v1/ingest/logs/text",
        data={"logs": logs}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["events_ingested"] >= 1
    assert "alerts_generated" in data


def test_chat_copilot():
    """
    Test the AI Copilot with the new real-data version.
    Must use stream=False to get JSON response.
    """
    # Ingest real logs first
    logs = "powershell.exe -enc SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0AA==\nFailed login attempt for sa"
    client.post("/api/v1/ingest/logs/text", data={"logs": logs})

    # Use stream=False to get normal JSON
    response = client.post(
        "/api/v1/chat",
        json={"message": "Summarize today's top critical threats", "stream": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 10


def test_get_mitre_matrix():
    response = client.get("/api/v1/mitre/matrix")
    assert response.status_code == 200
    matrix = response.json()
    assert isinstance(matrix, list)
    assert matrix[0]["tactic"] == "Initial Access"


def test_get_forensic_tree():
    response = client.get("/api/v1/forensics/process-tree/DEV-WIN-SRV09")
    assert response.status_code == 200
    data = response.json()
    assert "rootProcess" in data
    assert data["rootProcess"]["name"] == "services.exe"


def test_system_config():
    response = client.get("/api/v1/system/config")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "CyCraft AI - Driverless SOC & Automated Incident Response"


def test_system_reset():
    response = client.post("/api/v1/system/reset-database")
    assert response.status_code == 200
    assert response.json()["status"] == "RESET"
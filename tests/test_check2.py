import os
from fastapi.testclient import TestClient
print("CWD:", os.getcwd())
print("DB URL env:", os.environ.get("DATABASE_URL"))
from bradlyai.main import app
print("Settings DB URL:", __import__("bradlyai").config.settings.DATABASE_URL)
from bradlyai.database import engine
print("Engine URL:", engine.url)
client = TestClient(app)
r = client.get("/health")
print("Health:", r.status_code)
from bradlyai.database import SessionLocal
from bradlyai.models.user import UserModel
db = SessionLocal()
print("Users:", db.query(UserModel).count())
db.close()

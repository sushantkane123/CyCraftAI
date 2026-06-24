import os
print("CWD:", os.getcwd())
print("DB URL env:", os.environ.get("DATABASE_URL"))
import bradlyai.config as c
print("Settings DB URL:", c.settings.DATABASE_URL)
import bradlyai.database as d
print("Engine URL:", d.engine.url)
from bradlyai.database import SessionLocal
from bradlyai.models.user import UserModel
db = SessionLocal()
print("Users:", db.query(UserModel).count())
db.close()

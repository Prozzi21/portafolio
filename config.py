import os
from dotenv import load_dotenv

load_dotenv()

TURSO_URL = os.environ.get("TURSO_URL", "")
TURSO_TOKEN = os.environ.get("TURSO_TOKEN", "")

USE_TURSO = bool(TURSO_URL and TURSO_TOKEN)

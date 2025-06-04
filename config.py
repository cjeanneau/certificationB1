import os
from pathlib import Path
from dotenv import load_dotenv


# Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = os.path.join(BASE_DIR, "data")

# Loading environment variables
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)


DB_NAME = os.getenv("DB_NAME")
PG_USER = os.getenv("PG_USER") # Exemple : un utilisateur dédié à votre projet
PG_PASSWORD = os.getenv("PG_PASSWORD") # Assurez-vous d'utiliser un mot de passe sécurisé
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")

# URL de connexion PostgreSQL
DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{DB_NAME}"

#FastAPI

API_TITLE = "conseil immo"
API_VERSION = "1.0"
API_DESCRIPTION = "Pour aider les investisseurs dans leurs investissements"

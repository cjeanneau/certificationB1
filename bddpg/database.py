# bddpg/database.py

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from config import DATABASE_URL
import logging
import sys

from .models import *
print(DATABASE_URL)

# Configuration du logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Affichage dans le terminal
        logging.FileHandler('bddpg.log', mode='a')  # Fichier de log en mode append
    ],
    force = True  # Force la configuration du logging pour écraser les précédentes configurations
)
logger = logging.getLogger(__name__)

# Création de l'engine SQLModel
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Mettre à True pour voir les requêtes SQL
    pool_pre_ping=True,
    pool_recycle=300,
)

def create_db_and_tables(drop: bool = False) -> None:
    """
    Crée la base de données et les tables si elles n'existent pas.
    Si `drop` est True, les tables existantes seront supprimées avant la création.
    """
    
    if drop:
        logger.info("Suppression des tables existantes...")
        SQLModel.metadata.drop_all(engine)
        logger.info("Tables supprimées avec succès")
    
    logger.info("Création des tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tables créées avec succès")


def get_session() -> Generator[Session, None, None]:
    """Générateur de session pour FastAPI Depends"""
    with Session(engine) as session:
        yield session

# Pour les scripts ou tests
def get_session_sync() -> Session:
    """Retourne une session synchrone pour utilisation directe"""
    return Session(engine)

if __name__ == "__main__":
    print("Creation de la BD")
    create_db_and_tables() # Crée les tables si elles m'existent pas


# data_process/fill_communes.py

### Script pour remplir la base de données PostgreSQL avec les codes Insee et postaux des communes françaises.

import pandas as pd
import os
import time 
import chardet

from config import DATA_DIR

from sqlmodel import Session
from bddpg import engine 
from bddpg import CommuneCreate, commune_crud
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Affichage dans le terminal
        logging.FileHandler('fill_communes.log', mode='a')  # fichier de log en mode append
    ],
    force=True  # Force la configuration du logging pour écraser les précédentes configurations
)
logger = logging.getLogger(__name__)

# Chemin vers le fichier CSV des codes communes
file_location = os.path.join(DATA_DIR, "codes_communes.csv")

def load_communes_file(file_path : str) -> pd.DataFrame:
    """
    Traite le fichier des codes communes pour créer un DataFrame.

    Parameters:
        file_path (str): Chemin vers le fichier CSV des codes communes

    Returns:
        pd.DataFrame: DataFrame contenant les données des communes
    """
    start_time = time.time()

    colonnes_to_keep = [
        '#Code_commune_INSEE',
        'Nom_de_la_commune',
        'Code_postal'
    ]
    
    # Lecture du fichier CSV
    df_communes = pd.read_csv(file_path, dtype=str, encoding=detect_encoding(file_path), sep=';', usecols=colonnes_to_keep)
    
    # Nettoyage des colonnes
    df_communes.columns = [col.strip().lower() for col in df_communes.columns]
    
    # Affichage du temps de traitement
    logger.info(f"Temps de traitement pour {file_path}: {time.time() - start_time:.2f} secondes")
    
    return df_communes

def detect_encoding(file_path: str) -> str:
    """
    Détecte l'encodage d'un fichier.
    
    Parameters:
        file_path (str): Chemin vers le fichier
    
    Returns:
        str: L'encodage détecté
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def load_communes_to_PG(df_communes: pd.DataFrame):
    """
    Enregistre le DataFrame des communes dans la base de données PostgreSQL.

    Parameters:
        df_communes (pd.DataFrame): DataFrame contenant les données des communes
    
    Returns:
        None
    """
    with Session(engine) as session:
        try:
            for _, row in df_communes.iterrows():
                commune = CommuneCreate(
                    code_insee_commune=row['#code_commune_insee'],
                    nom_commune=row['nom_de_la_commune'],
                    code_postal=row['code_postal']
                )
                if not commune_crud.get_by_code_insee(session, commune.code_insee_commune):
                    created_commune = commune_crud.create(session, commune)
                    logger.info(f"Commune créée: {created_commune}")
                else:
                    logger.info(f"La commune {row['nom_de_la_commune']} existe déjà, pas de création.")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des communes: {str(e)}")
            raise


def fill_communes():
    """
    Fonction principale pour remplir la base de données PostgreSQL avec les codes Insee et postaux des communes françaises.
    
    Parameters:
        file_location (str): Chemin vers le fichier CSV des codes communes
    
    Returns:
        None
    """
    file_location = os.path.join(DATA_DIR, "codes_communes.csv")
    logger.info("Début de l'enregistrement des communes dans la base de données PostgreSQL...")
    df_communes = load_communes_file(file_location)
    load_communes_to_PG(df_communes)
    logger.info("Enregistrement terminé.")

if __name__ == "__main__":
    
    fill_communes()

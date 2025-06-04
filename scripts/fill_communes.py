# fill_communes.py
### Script pour remplir la base de données PostgreSQL avec les codes Insee et postaux des communes françaises.

import pandas as pd
import os
import time 
import chardet
from config import DATA_DIR
from app.database import engine  
from sqlmodel import Session

from app.models.commune import CommuneCreate  
from app.crud.commune import commune_crud  
file_location = os.path.join(DATA_DIR, "codes_communes.csv")

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

def process_communes(file_path):
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
    print(f"Temps de traitement pour {file_path}: {time.time() - start_time:.2f} secondes")
    
    return df_communes

def df_to_pg(df_communes):
    """
    Enregistre le DataFrame des communes dans la base de données PostgreSQL.

    Parameters:
        df_communes (pd.DataFrame): DataFrame contenant les données des communes
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
                    print("Commune créée:", created_commune)
                else:
                    print("La commune existe déjà, pas de création.")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement des communes: {str(e)}")
            raise


if __name__ == "__main__":
    
    df_communes = process_communes(file_location)
    print(df_communes.head())
    print(df_communes.shape)
    

    print("Enregistrement des communes dans la base de données PostgreSQL...")
    df_to_pg(df_communes)
    print("Enregistrement terminé.")

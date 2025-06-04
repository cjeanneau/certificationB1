# dvf2pg.py

import pandas as pd
import os
from config import DATA_DIR
import time 
from app.models.transaction_dvf import TransactionDVFCreate  
from app.crud.commune import commune_crud  
file_location = os.path.join(DATA_DIR, "01_DVF", "ValeursFoncieres-2024.txt" )

col_dvf_to_keep = [
    'Date mutation',
    'Nature mutation',
    'Valeur fonciere',
    'No voie',
    'Type de voie',
    'Code voie',
    'Voie',
    'Code postal',
    'Commune',
    'Code departement',
    'Code commune',
    'Prefixe de section',
    'Section',
    'No plan',
    'Code type local', 
    'Type local', 
    'Surface reelle bati', 
    'Nombre pieces principales',
    'Surface terrain'
    ]



def process_dvf2dataframe(file_path, col_to_keep, dpt):
    """
    Traite le fichier DVF pour extraire les données d'un département spécifique.

    Parameters:
        file_path (str): Chemin vers le fichier DVF source
        col_to_keep (list): Liste des colonnes à conserver dans le DataFrame
        dpt (str): Code du département à extraire (ex: "37")

    Returns:
        pd.DataFrame: DataFrame contenant les données DVF filtrées pour le département

    Performance:
        - Lecture par chunks de 100000 lignes
        - Filtrage sur le département
        - Concaténation finale des chunks filtrés

    Example:
        >>> df = process_dvf2dataframe(
        ...     file_path="ValeursFoncieres-2024.txt",
        ...     col_to_keep=['Date mutation', 'Code departement'],
        ...     dpt="37"
        ... )
    """
    start_time = time.time()
    
    dvf_list = []
    for chunk in pd.read_csv(file_path, sep='|', dtype=str, chunksize=100000, usecols = col_to_keep):
        ligne = chunk[chunk["Code departement"] == dpt]
        if not ligne.empty:
            dvf_list.append(ligne)
    df = pd.concat(dvf_list, ignore_index=True)    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nTemps d'exécution: {duration:.2f} secondes")
    
    return df



if __name__ == "__main__":
    
    # Ci-dessous, executé une premiere fois pour créer le fichier CSV ci-après.
    ############ On pourra sans doute travailler avec toutes les données plutot que le dpt37############
    #df = process_dvf2dataframe(file_path=file_location, dpt="37", col_to_keep=col_dvf_to_keep) # 5.17 seconds
    #print(df.head())
    #print(df.shape)
    # Sauvegarde du DataFrame dans un fichier CSV
    #output_file = os.path.join(DATA_DIR, "01_DVF", "dvf_37_2024.csv")
    #df.to_csv(output_file, index=False, sep=";")
    #print(f"DataFrame sauvegardé dans {output_file}")  
    
    
    start_time = time.time()
    file_location = os.path.join(DATA_DIR, "01_DVF", "dvf_37_2024.csv")
    df = pd.read_csv(file_location, sep=';', dtype=str)
    print(df.head())
    print(df.shape)
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nTemps d'exécution: {duration:.2f} secondes")

    for index, row in df.iterrows():
        transactio = 

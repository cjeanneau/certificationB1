# data_process/external_api/retrieve_id_ban.py

# Requete API pour récupérer l'"id" (identifiant_ban) à partir d'une adresse et du code insee,
# à partir de : api-adresse.data.gouv.fr/search/
# LIMITATION :  50 requetes/seconde/IP

import requests
import time

def retrieve_id_ban(adresse:str , code_insee:str) -> tuple:
    """
    Récupère l'ID BAN et le score pour une adresse donnée et un code INSEE.
    
    Args:
        adresse (str): L'adresse à rechercher.
        code_insee (str): Le code INSEE de la commune.
    
    Returns:
        str: L'ID BAN si trouvé, sinon None.
        float: Le score associé à l'ID BAN, ou None si non trouvé.
    """
    
    base_url_ban = "https://api-adresse.data.gouv.fr/search/"
    params = {
        'q': adresse,
        'citycode': code_insee,
        'limit': 1
    }

    try:
        response = requests.get(base_url_ban, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['features']:
                id_ban = data['features'][0]['properties']['id']
                score_ban = data['features'][0]['properties']['score']
                return id_ban, score_ban
            else:
                return None, None
        else:
            print(f"Erreur lors de la requête: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Exception lors de la récupération de l'ID BAN: {str(e)}")
        return None, None
    finally:
        # Pause pour éviter de surcharger l'API qui esr limitée à 50 requetes/seconde/IP
        time.sleep(0.02)

def test():
    """
    Fonction de test de la fonction  retrieve_id_ban(adresse, code_insee)
    
    Returns:
        None
    """


    from scripts.fill_dvf import load_dvf_file, clean_dvf_data
    import os
    from app.utils.parser import safe_int_conversion
    from config import DATA_DIR
    import pandas as pd

    # Chemin du fichier DVF
    file_path = os.path.join(DATA_DIR,"ValeursFoncieres-2023.txt")

    # Charger et nettoyer les données DVF
    df = load_dvf_file(file_path)
    df = clean_dvf_data(df)


    # Afficher les 10 premières lignes du DataFrame nettoyé
    df_cleaned = df.head(10)
    print(df_cleaned)
    #print(df_cleaned[['adresse_normalisee', 'code_insee_commune']])


    for _, row in df_cleaned.iterrows():
        adresse_parts = []
        if pd.notna(row['No voie']) and row['No voie'].strip():
            adresse_parts.append(row['No voie'].strip())
        if pd.notna(row['Type de voie']) and row['Type de voie'].strip():
            adresse_parts.append(row['Type de voie'].strip())
        if pd.notna(row['Voie']) and row['Voie'].strip():
            adresse_parts.append(row['Voie'].strip())
        adresse_normalisee = ' '.join(adresse_parts) if adresse_parts else None
    
        # Construction du code INSEE complet
        code_dept = safe_int_conversion(row['Code departement']) #convertit string en entier
        code_commune = safe_int_conversion(row['Code commune']) #convertit string en entier
        if code_dept is not None and code_commune is not None:
            code_insee_complet = (code_dept * 1000) + code_commune
            code_insee_commune = str(code_insee_complet).zfill(5)  # Formatage sur 5 chiffres
        else:
            print(f"Le code insee commune n'est pas identifiable, l'enregistrement est ignorée")
            continue    #On passe à la ligne suivante

        if adresse_normalisee is None or not adresse_normalisee.strip():
            print(f"L'adresse normalisée est vide pour l'enregistrement : {row}")
            continue
        # Requête à l'API pour récupérer l'ID BAN
        print(f"\nRecherche de l'ID BAN pour l'adresse : {adresse_normalisee}, Code INSEE : {code_insee_commune}")
        id_ban, score = retrieve_id_ban(adresse_normalisee, code_insee_commune)
        if id_ban is None:
            print(f"Aucun ID BAN trouvé pour l'adresse : {adresse_normalisee}, Code INSEE : {code_insee_commune}")
            continue
        
        print(f"ID BAN trouvé : {id_ban}, score ban : {score}")
    return
    
if __name__ == "__main__":
    print("Test de la fonction retrieve_id_ban et un peu plus...")
    #test()
    



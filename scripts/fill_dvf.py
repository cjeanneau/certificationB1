#!/usr/bin/env python
# coding: utf-8



import os
import pandas as pd
from config import DATA_DIR
from app.database import engine  
from sqlmodel import Session
from app.utils.parser import safe_int_conversion
from app.crud.bien_immobilier import bien_immobilier_crud
from app.models.bien_immobilier import BienImmobilierCreate
from app.models.transaction_dvf import TransactionDVFCreate
from app.crud.transaction_dvf import transaction_dvf_crud 
import time
from scripts.retrieve_id_ban import retrieve_id_ban


def load_dvf_file(file_path: str) -> pd.DataFrame:
    """
    Charge le fichier DVF dans un DataFrame pandas.
    
    Parameters:
        file_path (str): Chemin vers le fichier DVF
    
    Returns:
        pd.DataFrame: DataFrame contenant les données du fichier DVF
    """
    df = pd.DataFrame()
    # Vérification de l'existence du fichier
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
    # Chargement du fichier DVF
    print(f"Chargement du fichier DVF depuis {file_path}...")

    col_to_keep = [
        'Date mutation',
        'Nature mutation',
        'Valeur fonciere',
        'No voie',
        'B/T/Q',
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
    
    col_type = {
        'Nature mutation' : 'object',
        'Valeur fonciere' : 'float32',
        'No voie' : 'object',
        'B/T/Q' : 'object',
        'Type de voie' : 'object',
        'Code voie' : 'object',
        'Voie' : 'object',
        'Code postal' : 'object',
        'Commune' : 'object',
        'Code departement' : 'object',
        'Code commune' : 'object',
        'Prefixe de section' : 'object',
        'Section' : 'object',
        'No plan' : 'Int16',
        'Code type local' : 'Int8',
        'Type local' : 'object',
        'Surface reelle bati' : 'Int32',
        'Nombre pieces principales' : 'Int8',
        'Surface terrain' : 'Int32'
    }
    
    df = pd.read_csv(
        file_path,
        sep='|',  # Le séparateur est une barre verticale
        decimal=',',  # Le séparateur décimal est une virgule
        usecols=col_to_keep,  # On ne garde que les colonnes nécessaires
        dtype=col_type,  # On spécifie les types de colonnes
        parse_dates=['Date mutation'],  # On parse la colonne des dates
        na_values=['NULL', '', '-']  # Valeurs à considérer comme
    )
    return df

def clean_dvf_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le DataFrame DVF.
    
    Parameters:
        df (pd.DataFrame): DataFrame contenant les données DVF
    
    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    # On supprime les lignes dont la nature de mutation est 'Echange'
    df = df[df['Nature mutation'] != 'Echange']
    
    # On élimine les lignes dont les valeurs foncières sont manquantes
    df = df[df['Valeur fonciere'].notna()]
    
    # Les valeurs foncières en virgule flottante ne nous intéressent pas vraiment, on va les convertir en entiers
    df['Valeur fonciere'] = df['Valeur fonciere'].astype('int32')
    
    # Supprimer les doublons (conserver la première occurrence)
    df = df.drop_duplicates()
    # On va compléter les NaN des Surfaces et nombre de pièces par 0
    df.loc[:, 'Surface reelle bati'] = df['Surface reelle bati'].fillna(0)
    df.loc[:, 'Surface terrain'] = df['Surface terrain'].fillna(0)
    df.loc[:, 'Nombre pieces principales'] = df['Nombre pieces principales'].fillna(0)
    
    # De même sur la colonne B/T/Q par un champ vide
    df.loc[:, 'B/T/Q'] = df['B/T/Q'].fillna('')
    df.loc[:, 'No voie'] = df['No voie'].fillna('')
    df.loc[:, 'Type de voie'] = df['Type de voie'].fillna('')
    df.loc[:, 'Voie'] = df['Voie'].fillna('')
    df.loc[:, 'Code postal'] = df['Code postal'].fillna('')
    df.loc[:, 'Prefixe de section'] = df['Prefixe de section'].fillna('')
    df.loc[:, 'Section'] = df['Section'].fillna('')
    
    # Le prix d'un terrain étant insignifiant dans le prix d'un bien immobilier,
    # nous allons supprimer les lignes : 
    #     dont le type de local est Nan car ils n'ont pas de surface bati 
    #     dont le type de local est Dépendances car ils n'ont que des que des surfaces de terrain.
    # Ce choix est propre au projet qui ne concernera que les investissmeent en surface bati soit :  maisons, appartements et locaux industriels 
    filtre = (df['Type local'].isna()) | (df['Type local'] == 'Dépendance') 
    df = df[~filtre]


    # On regroupe les transactions par date et valeurs et on crée un id_transaction pour chacun de ces couples
    df.loc[:, 'Date mutation'] = pd.to_datetime(df['Date mutation'], format='%d/%m/%Y', errors='coerce') # on s'assure que toutes les dates soient au même format pour le tri, c'est mieux !
    df = df.sort_values(by=['Date mutation', 'Valeur fonciere', 'Code departement', 'Code commune']).reset_index(drop=True) 
    col_id_transaction = df.groupby(['Date mutation', 'Valeur fonciere', 'Code departement', 'Code commune', 'Code voie']).ngroup()
    df.insert(loc=0, column='id_transaction', value=col_id_transaction)

    # On ne garde que les transactions avec une ligne unique car il y a souvent les memes biens qui apparaissent 2 fois sur la même transaction
    # Sans doute dû à des corrections dans les champs.
    id_transaction_count = df['id_transaction'].value_counts()
    unique_id_transactions_values = id_transaction_count[id_transaction_count == 1].index
    unique_id_transactions_list = unique_id_transactions_values.tolist()
    df =  df[df['id_transaction'].isin(unique_id_transactions_list)]

    # On efface les lignes dont la valeur fonciere est inférieure à 1€ car ce n'est pas représentatif.
    # On pourra sans doute augmenter cette valeur autour de 1000€ ou plus
    filtre = df['Valeur fonciere'] <= 1
    df = df[~filtre]
    # Et on retire les lignes dont la surface reelle bati est nulle car seul le bati nous interesse
    df = df[df['Surface reelle bati'] != 0]

    # On va recréer l'index du dataframe pour qu'il soit propre
    df.reset_index(drop=True, inplace=True)
    
    return df


def save_dvf__df_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Sauvegarde le DataFrame DVF dans un fichier CSV.
    
    Parameters:
        df (pd.DataFrame): DataFrame contenant les données DVF
        output_path (str): Path et Nom du fichier de sortie
    """

    # On sauvegarde le DataFrame dans un fichier CSV
    df.to_csv(output_path, index=False, sep=';')
    print(f"Le fichier a été sauvegardé sous {output_path}")


def load_dvf_to_PG(df: pd.DataFrame, index = 0):
    """
    Enregistre le DataFrame DVF dans la base de données PostgreSQL.
    
    Parameters:
        df (pd.DataFrame): DataFrame contenant les données DVF
        index (int): Index de départ pour l'enregistrement des transactions (par défaut 0)
    
    Returns:
        None
    """
    for index, row in df.iterrows():
        try:
            # Construction de l'adresse normalisée
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

            # Construction de la référence cadastrale
            reference_cadastrale_parcelle = row['Prefixe de section'] + row['Section'] + str(row['No plan'])
            id, score = retrieve_id_ban(adresse_normalisee, code_insee_commune)
           
            bien = BienImmobilierCreate(
                code_insee_commune=code_insee_commune,
                adresse_normalisee=adresse_normalisee,
                code_postal=row['Code postal'] if pd.notna(row['Code postal']) else None,
                reference_cadastrale_parcelle=reference_cadastrale_parcelle,
                type_bien=row['Type local'] if pd.notna(row['Type local']) else None,
                surface_reelle_bati=row['Surface reelle bati'] if pd.notna(row['Surface reelle bati']) else None,
                nombre_pieces_principales=row['Nombre pieces principales'] if pd.notna(row['Nombre pieces principales']) else None,
                surface_terrain_totale=row['Surface terrain'] if pd.notna(row['Surface terrain']) else None,
                source_info_principale="DVF",
                id_ban = id if id else None,
                score_ban = score if score else None
            )

            transaction = TransactionDVFCreate(
                    id_bien=0,
                    date_mutation=row['Date mutation'].date(),
                    nature_mutation=row['Nature mutation'],
                    valeur_fonciere=row['Valeur fonciere']
                )
            
            with Session(engine) as session:
                try:    
                         # Vérifier si le bien existe déjà avec tous les champs
                        existing_bien = bien_immobilier_crud.get_by_all_fields(session, bien)
                        if existing_bien:
                            print(f"Bien existant trouvé avec ID: {existing_bien.id_bien}")
                            created_bien = existing_bien
                        else:
                            created_bien = bien_immobilier_crud.create(session, bien)
                            print(f"Nouveau bien créé avec ID: {created_bien.id_bien}")
                        print(f"Ligne d'index {index} enregistrée avec succès pour le bien ID: {created_bien.id_bien}")
                        # Maintenant que le bien est créé, on peut enregistrer la transaction
                        transaction = TransactionDVFCreate(
                            id_bien=created_bien.id_bien,
                            date_mutation=row['Date mutation'].date(),
                            nature_mutation=row['Nature mutation'],
                            valeur_fonciere=row['Valeur fonciere']
                        )
                        # Vérifier si la transaction existe déjà
                        existing_transaction = transaction_dvf_crud.get_by_all_fields(session, transaction)
                        if existing_transaction:
                            print(f"Transaction existante trouvée avec ID: {existing_transaction.id_transaction}")
                            created_transaction = existing_transaction
                        else:
                            created_transaction = transaction_dvf_crud.create(session, transaction)
                            print(f"Nouvelle transaction créée avec ID: {created_transaction.id_transaction}")

                        print(f"Transaction DVF {index} enregistrée avec succès pour le bien ID: {created_bien.id_bien}")
                except Exception as e:
                    print(f"Erreur lors de la création du bien: {e}")
                    session.rollback()  # Annule la transaction en cas d'erreur
                    continue

        except Exception as e:
            print(f"Erreur ligne idex : {index}: {e}")
    print(f"Toutes les transactions DVF ont été traitées et enregistrées avec succès jusqu'à l'index : {index} !")


def fill_dvf():
    """
    Fonction principale pour charger, nettoyer et enregistrer les données DVF dans la base de données PostgreSQL.
    
    Elle traite les fichiers contenu dans {DATA_DIR} qui commencent par "ValeursFoncieres-" et se terminent par ".txt".
    Elle charge les données dans un DataFrame, les nettoie, puis les enregistre dans la base de données postgreSQL.
    
    """
    start_time = time.time()
    intermediate_time = start_time
    for file in os.listdir(DATA_DIR):
        if file.startswith("ValeursFoncieres-") & file.endswith(".txt"):
            
            file_path = os.path.join(DATA_DIR, file)
            df = load_dvf_file(file_path)
            print(f"{file} : Chargement du fichier DVF terminé en {(time.time() - intermediate_time):.2f} secondes. Nombre de lignes : {len(df)}")
            df_cleaned = clean_dvf_data(df)
            print(f"{file} : Nettoyage du DataFrame terminé en {(time.time() - intermediate_time):.2f} secondes. Nombre de lignes après nettoyage : {len(df_cleaned)}")
            load_dvf_to_PG(df_cleaned, index=0)
            intermediate_time = time.time()
            print(f"{file} : Chargement en Base de Données terminé en {(intermediate_time - start_time):.2f} secondes.")
    print("\nTous les fichiers DVF ont été traités et sauvegardés avec succès !")
    print("Fin du script.")
    end_time = time.time()
    print(f"\nTemps total: {(end_time - start_time):.2f} secondes")


if __name__ == "__main__":
    
    # test retrieve_id_ban()
    file = "ValeursFoncieres-2023.txt"
    file_path = os.path.join(DATA_DIR, file)
    df = load_dvf_file(file_path)
    df_cleaned = clean_dvf_data(df)
    df = df_cleaned.head(50)
    print(len(df))
    start_time = time.time()
    load_dvf_to_PG(df, index=0)
    end_time = time.time()
    print(f"Temps total pour le test : {(end_time - start_time):.2f} secondes")









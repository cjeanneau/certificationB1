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
    print("Compte les Nan avant ")
    print(df['Prefixe de section'].isna().sum()) # On vérifie s'il y a des NaN dans la colonne 'Prefixe de section'
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
    
    print("Compte les Nan apres ")
    print(df['Prefixe de section'].isna().sum()) 
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
    print(df['Prefixe de section'].dtype)
    print("Compte les Nan avant le for ")
    print(df['Prefixe de section'].isna().sum()) 

    for index, row in df.iterrows():
        print(row['Prefixe de section'])
        print(type(row['Prefixe de section']))
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
            print(f"Adresse normalisée: {adresse_normalisee}")
            print(type(adresse_normalisee))
        
            # Construction du code INSEE complet
            code_dept = safe_int_conversion(row['Code departement']) #convertit string en entier
            code_commune = safe_int_conversion(row['Code commune']) #convertit string en entier
            if code_dept is not None and code_commune is not None:
                code_insee_complet = (code_dept * 1000) + code_commune
                code_insee_commune = str(code_insee_complet).zfill(5)  # Formatage sur 5 chiffres
            else:
                print(f"Le code insee commune n'est pas identifiable, l'enregistrement est ignorée")
                continue    #On passe à la ligne suivante
            print(f"Code INSEE complet: {code_insee_commune}")
            print(type(code_insee_commune))


            # Construction de la référence cadastrale
            #if pd.notna(row['Prefixe de section']) and pd.notna(row['Section']) and pd.notna(row['No plan']):
            print(f"Prefixe de section: {type(row['Prefixe de section'])}")
            print(f"Section: {type(row['Section'])}")
            print(f"No plan: {type(str(row['No plan']))}")
            reference_cadastrale_parcelle = row['Prefixe de section'] + row['Section'] + str(row['No plan'])
            print(f"Référence cadastrale parcelle: {reference_cadastrale_parcelle}")    
            input()
        
            bien = BienImmobilierCreate(
                code_insee_commune=code_insee_commune,
                adresse_normalisee=adresse_normalisee,
                code_postal=row['Code postal'] if pd.notna(row['Code postal']) else None,
                reference_cadastrale_parcelle=reference_cadastrale_parcelle,
                type_bien=row['Type local'] if pd.notna(row['Type local']) else None,
                surface_reelle_bati=row['Surface reelle bati'] if pd.notna(row['Surface reelle bati']) else None,
                nombre_pieces_principales=row['Nombre pieces principales'] if pd.notna(row['Nombre pieces principales']) else None,
                surface_terrain_totale=row['Surface terrain'] if pd.notna(row['Surface terrain']) else None,
                source_info_principale="DVF"
            )

            transaction = TransactionDVFCreate(
                    id_bien=0,
                    date_mutation=row['Date mutation'].date(),
                    nature_mutation=row['Nature mutation'],
                    valeur_fonciere=row['Valeur fonciere']
                )
            
            with Session(engine) as session:
                try:
                        created_bien = bien_immobilier_crud.create(session, bien)
                        # Maintenant que le bien est créé, on peut enregistrer la transaction
                        transaction = TransactionDVFCreate(
                            id_bien=created_bien.id_bien,
                            date_mutation=row['Date mutation'].date(),
                            nature_mutation=row['Nature mutation'],
                            valeur_fonciere=row['Valeur fonciere']
                        )
                        created_transaction = transaction_dvf_crud.create(session, transaction)
                        print(f"Transaction DVF {index} enregistrée avec succès pour le bien ID: {created_bien.id_bien}")
                except Exception as e:
                    print(f"Erreur lors de la création du bien: {e}")
                    session.rollback()  # Annule la transaction en cas d'erreur
                    continue

        except Exception as e:
            print(f"Erreur ligne idex : {index}: {e}")
    print(f"Toutes les transactions DVF ont été traitées et enregistrées avec succès jusqu'à l'index : {index} !")






def fill_dvf():
    
    list_years = [2024, 2023]
    for file in os.listdir(DATA_DIR):
        if file.startswith("ValeursFoncieres-") & file.endswith(".txt"):
            input(f" Pour traiter le fichier {file}, Appuyez sur Entrée ... ou Ctrl+C pour quitter.")
            file_path = os.path.join(DATA_DIR, file)
            df = load_dvf_file(file_path)
            print(f"Chargement du fichier DVF terminé. Nombre de lignes : {len(df)}")
            df_cleaned = clean_dvf_data(df)
            print(f"Nettoyage du DataFrame terminé. Nombre de lignes après nettoyage : {len(df_cleaned)}")
            df_cleaned.info()
            sample_df = df_cleaned.head(2)
            print(sample_df['Prefixe de section'].dtype)
        
            load_dvf_to_PG(sample_df, index=0)
            #output_file = f"dvf_{year}_cleaned.csv"
            #file_path = os.path.join(os.getcwd(), "data", "01_DVF", output_file)
            #save_dvf__df_to_csv(df_cleaned, file_path)
            
            #print(f"Traitement du fichier {file} terminé avec succès !")
            #print (f"Nombre de lignes dans le DataFrame nettoyé : {len(df_cleaned)}")
            #df_cleaned.info()

    print("Tous les fichiers DVF ont été traités et sauvegardés avec succès !")
    #print(f"Fichiers sauvegardés dans le répertoire : {os.path.join(os.getcwd(), 'data', '01_DVF')}")
    print("Fin du script.")




if __name__ == "__main__":
    
    fill_dvf()









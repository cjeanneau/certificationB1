import pandas as pd
import csv
import os
from config import DATA_DIR


file_location = os.path.join(DATA_DIR, "01_DVF", "DVF2024_100000lignes.txt" )


df_ori = pd.read_csv(file_location, sep='|', dtype=str)
#print(df.shape)
print(df_ori.info())

#print(df.columns.tolist())


def diplay_line_by_line_col_not_empty(df):
    """
    Fonction pour afficher chaque ligne d'un df et ses colonnes à condition qu'elles ne soients pas vide
    Args : dataFrame df
    Output :  affichage surle terminal
    """
    for index, row in df.iterrows():
        print(f"\n--- Ligne {index + 1} ---")
        for col, val in row.items():
            if pd.notna(val) and val.strip() != "":
                print(f"{col}: {val}")
        input("\nAppuie sur Entrée pour continuer...")



col_to_drop = ['Identifiant de document', 'Reference document', '1 Articles CGI', '2 Articles CGI', '3 Articles CGI', '4 Articles CGI', '5 Articles CGI']
col_to_keep = [
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

col_to_keep = col_to_keep + ['No disposition','Nombre de lots', '1er lot', 'Surface Carrez du 1er lot', '2eme lot', 'Surface Carrez du 2eme lot']
#On ne garde que les colonnes listées ci-dessus
#df = df[col_to_keep]
#print (df.head(20))
#print(df.info())

# Si nous n'avons pas de valeurs foncières, les lignes ne nous intéressent pas 
#df = df[~df['Valeur fonciere'].isna()]

# Et regardons ceux qui n'ont pas cette information
#print(df[df['Type local'].isna()])
## Ce sont peut-etre des terrains uniquement
#df_4100 = df[df['Code postal'] == '4100']
#print(df_4100)



# Je vais finalement charger que le lignes de mon fichier qui m'intéressent, 
# c'est à dire celle deont le code départment est 37
file_location = os.path.join(DATA_DIR, "01_DVF", "ValeursFoncieres-2024.txt" )

dvf_37 = []
for chunk in pd.read_csv(file_location, sep='|', dtype=str, chunksize=100000, usecols = col_to_keep):
    lignes_37 = chunk[chunk["Code departement"] == "37"]
    dvf_37.append(lignes_37)

df = pd.concat(dvf_37, ignore_index=True)

print(df.info())

#Voyons les types de local ou code type
print(df['Type local'].value_counts())
pd.set_option('display.max_rows', 100)
#print(df.sort_values(by=['Date mutation', 'Valeur fonciere','Section', 'No plan']).iloc[100:200])

#df_with_type_local = df[~df['Type local'].isna()]

#print(df_with_type_local.info())
#print(df_with_type_local.sort_values(by=['Date mutation', 'Valeur fonciere', 'Section', 'No plan']).head(50))

#print("Nombre de type locaux industriels et assimilés :")
#print(df[df['Type local'] == 'Local industriel. commercial ou assimilé'].shape[0])
# on a cette information avec value_counts() ci-dessus

# Voyons comment sont les appartements d'un même immeuble
print(df[(df['Type local'] == 'Appartement') & (df['Code postal'] == '37000') & (df['Voie'].str.contains('OCKEGHEM', case=True, na=False))].sort_values('No voie').head(100))


# Remarque Si sur même jour, même valeur fonciere,  même section et No plan :
#   Si il y a plusieurs Maisons alors Si elles ont la même surface et des surfaces de terrain differentes, il faut les ajouter pour avoir la taille totale du terrain. 
#   Si il y a plusieurs maisons de taille differente, ce sont bien des maisons séparées appartenant à la même vente
#   Si il y a des dépendances, elles peuvent être ignorées (de sont des terres adjacentes qui ont peu de valeur), attention elles peuvent etre dans une autre section cadastrale
#   S'il y a des locaux industriels, on ne va pas enregistrer les données

# Pour un immeuble on peut avoir plusieurs appartements mais il est diffcile de les différencier. Pour le 
# moment ce n'est pas grave puisqu'à une adresse on définira un prix moyen au m2. 


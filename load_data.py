from bddpg import  create_db_pgsql
from data_process import fill_communes
from data_process import fill_dvf
from data_process import fill_graphe

delete_table = True  # Mettre à True pour supprimer les tables existantes

def main():
    """
    Fonction principale pour créer la base de données PostgreSQL et remplir les tables.
    
    Returns:
        None
    """
    print("Création de la base de données PostgreSQL et des tables...")
    #create_db_pgsql()
    print("Base de données et tables créées.")

    print("Remplissage des communes...")
    #fill_communes()
    print("Remplissage des communes terminé.")

    print("Remplissage des transactions DVF...")
    #fill_dvf()
    print("Remplissage des transactions DVF terminé.")
    
    print("Remplissage du graphe des communes limitrophes...")
    fill_graphe()
    print("Remplissage du graphe des communes limitrophes terminé.")

    print("Processus terminé.")

if __name__ == "__main__":
    main()
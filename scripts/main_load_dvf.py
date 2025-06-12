from scripts.create_db_pgsql import create_db_pgsql
from scripts.fill_communes import fill_communes
from scripts.fill_dvf import fill_dvf


def main():
    """
    Fonction principale pour créer la base de données PostgreSQL et remplir les tables.
    
    Returns:
        None
    """
    print("Création de la base de données PostgreSQL et des tables...")
    create_db_pgsql()
    
    print("Remplissage des communes...")
    fill_communes()
    
    print("Remplissage des transactions DVF...")
    fill_dvf()
    
    print("Processus terminé.")

if __name__ == "__main__":
    main()


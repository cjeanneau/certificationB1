from app.database import engine, get_session_sync, create_db_and_tables
import logging


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_pgsql(drop_tables: bool = False):
    """Fonction principale pour créer la base de données et les tables
    Args:
        drop_tables (bool): Si True, supprime les tables existantes avant de les recréer.
    """
    logger.info("Démarrage de la création de la base de données PostgreSQL")
    try:
        # Création des tables
        create_db_and_tables(drop=drop_tables) # Mettre a True pour supprimer les tables existantes
        
        # Test de la connexion avec une session
        with get_session_sync() as session:  
            logger.info("Connexion à la base de données réussie")
            # Vous pouvez ajouter ici du code pour peupler la base
           
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de la base de données: {str(e)}")
        raise
    else:
        logger.info("Base de données créée avec succès")

if __name__ == "__main__":
    create_db_pgsql()

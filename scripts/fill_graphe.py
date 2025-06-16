
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrap_city import get_soup, get_communes_limitrophes, get_infos_commune, get_commune_name
from scripts.neo4j_commune_service import commune_graph_service
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_commune_limitrophes(id_origin: int, communes_limitrophes: dict):
    """Traite les communes limitrophes et crée les relations"""
    for direction, commune_to_register in communes_limitrophes.items():
        print(f"Orientation : {direction}")
        for commune_info in commune_to_register:
            nom_comm_limit = commune_info['nom']
            url_comm_limit = commune_info['url']
            print(f"{nom_comm_limit} - {url_comm_limit}")
            
            id_limitrophe = None
            
            if nom_comm_limit and url_comm_limit:
                # Créer la commune limitrophe (avec scraped=False)
                id_limitrophe = commune_graph_service.create_temporary_commune_and_return_id(
                    nom=nom_comm_limit,
                    url=url_comm_limit,
                    scraped=False
                )
                logger.info(f"DEBUG: ID pour {nom_comm_limit}: {id_limitrophe}")
            elif not url_comm_limit:
                # Chercher une commune existante par nom
                id_existing = commune_graph_service.get_commune_id_by_name(nom_comm_limit)
                if id_existing is not None:
                    id_limitrophe = id_existing
                else:
                    logger.warning(f"Pas de commune limitrophe trouvée pour {nom_comm_limit} dans la direction {direction}")
                    continue
            
            if id_limitrophe is not None:
                print(f"Création de la relation entre {id_origin} et {id_limitrophe} dans la direction {direction}")
                # Créer la relation
                commune_graph_service.add_relation_limitrophe_by_id(
                    node_id_origin=id_origin,
                    node_id_target=id_limitrophe,
                    direction=direction
                )

def process_single_commune(commune: dict) -> bool:
    """Traite une seule commune - retourne True si traitement réussi"""
    logger.info(f"{commune['nom']} - ({commune['url']})")
    
    if not commune['url']:
        return False
        
    try:
        soup = get_soup(commune['url'])                
        infos_commune = get_infos_commune(soup)
        
    
        # Mettre à jour la commune avec les infos scrappées
        id_origin = commune_graph_service.create_commune_and_return_id(
            nom=commune['nom'],
            pays=infos_commune.get('Pays', None),
            region=infos_commune.get('Région', None),
            departement=infos_commune.get('Département', None),
            code_commune=infos_commune.get('Code commune', None),
            code_postaux=infos_commune.get('Code postal', None),
            url=commune['url'],
            scraped=False  # Pas encore terminé
        )

       
        if id_origin is None:
            logger.error(f"Impossible de créer/mettre à jour la commune {commune['nom']}")
            # DEBUG: Essayer avec des valeurs par défaut
            logger.info(f"DEBUG: Tentative avec valeurs par défaut...")
            id_origin = commune_graph_service.create_commune_and_return_id(
                nom=commune['nom'],
                pays="FR",
                region="Centre-Val de Loire",
                departement="Indre-et-Loire",
                code_commune=f"TEMP_{commune['nom'].replace(' ', '_').replace('-', '_')}",
                code_postaux="37000",
                url=commune['url'],
                scraped=False
            )
            logger.info(f"DEBUG: ID avec valeurs par défaut: {id_origin}")
            
            if not id_origin:
                return False
        
        # Scrapper les communes limitrophes
        logger.info(f"Scrapping des communes limitrophes pour {commune['nom']}")
        communes_limitrophes = get_communes_limitrophes(soup)
        
        # Traiter les communes limitrophes
        process_commune_limitrophes(id_origin, communes_limitrophes)
        
        # Marquer la commune d'origine comme scrappée
        commune_graph_service.mark_commune_as_scraped_by_id(node_id=id_origin)
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de {commune['nom']}: {str(e)}")
        return False

def process_communes_batch(limitation_region: str):
    """Traite un lot de communes non scrappées"""
    communes_non_scrappes = commune_graph_service.get_communes_not_scraped_by_region(limitation_region)
    
    if not communes_non_scrappes:
        logger.info("Aucune commune à scrapper.")
        return False
    
    logger.info(f"{len(communes_non_scrappes)} communes à scrapper dans la région {limitation_region}")
    
    for commune in communes_non_scrappes:
        process_single_commune(commune)
    
    return True

def initialize_database_with_seed():
    """Initialise la base avec la commune de départ (Tours)"""
    logger.info("Initialisation de la base de données Neo4j...")
    commune_graph_service.clear_database()
    logger.info("Base de données Neo4j initialisée")
    
    # Créer Tours comme commune de départ
    url_tours = "https://fr.wikipedia.org/wiki/Tours"    
    commune_graph_service.create_temporary_commune_and_return_id(
        nom="Tours",
        url=url_tours,
    )
    logger.info("🏛️ Commune de départ 'Tours' créée")

def run_scrapping_iterations(limitation_region: str, max_iterations: int = 2):
    """Execute plusieurs itérations de scrapping"""
    for iteration in range(1, max_iterations + 1):
        logger.info(f"=== Itération {iteration}/{max_iterations} ===")
        
        has_communes = process_communes_batch(limitation_region)
        
        if not has_communes:
            logger.info("🎉 Aucune commune à traiter - arrêt des itérations")
            break
        
        if iteration < max_iterations:
            logger.info("⏸️ Pause entre itérations...")
            time.sleep(2)

if __name__ == "__main__":
    limitation_region = "Centre-Val de Loire"
    
    #On efface la base de donnees Neo4j avant de commencer
    commune_graph_service.clear_database()

    # 1. Initialiser la base avec Tours
    initialize_database_with_seed()
    
    # 2. Exécuter les itérations de scrapping
    run_scrapping_iterations(limitation_region, max_iterations=20)
    
    logger.info("Fin du processus de scrapping")
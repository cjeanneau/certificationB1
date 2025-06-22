import sys
import logging
from bs4 import BeautifulSoup
from bddn4j import commune_graph_service
from data_process  import (
    get_soup,
    get_communes_limitrophes,
    get_infos_commune,
    get_commune_name    
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Affichage dans le terminal
        logging.FileHandler('fill_graphe.log', mode='a')  # fichier de log en mode append
    ],
    force=True  # Force la configuration du logging pour écraser les précédentes configurations
)
logger = logging.getLogger(__name__)


def fill_graphe():
    # Efface la la base de données Neo4j avant de commencer
    commune_graph_service.clear_database()

    # Initialise la base avec la commune de départ (Tours)
    nom_tours = "TOURS"
    url_tours = "https://fr.wikipedia.org/wiki/Tours"
    init_a_node(nom_tours, url_tours)
        
    # Je pourrais remplacer la boucle suivante par une comparaison 
    # entre le nombre de noeud total précédent et courant pour sortir de la  boucle.

    for iteration in range(0, 15):  # Nombre d'itérations à ajuster selon les besoins
        print("======================================================")
        print("==================== Itération {} ====================".format(iteration + 1))
        print("======================================================")
        process_communes_not_scrapped()
        
        print("==================== Fin  Itération {} ====================".format(iteration + 1))
        print(f"********************** Nombre de communes : {commune_graph_service.get_nombre_total_noeuds()} **********************")
        #input()

def init_a_node(nom,url):
    try:
        logger.info(f"Initialisation du noeud pour la commune : {nom} - URL : {url}")
        id_node = commune_graph_service.create_temporary_commune_and_return_id(
            nom=nom,
            url=url,
        )
        logger.info(f"Noeud {id_node} initialisé avec '{nom}' - '{url}'")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du noeud pour {nom}: {str(e)}")
        return None
    
def process_communes_not_scrapped():
    # on récupère la liste des communes à srcapper
    communes_to_be_scrapped = commune_graph_service.get_communes_not_scraped()
    
    for commune in communes_to_be_scrapped:
        soup= get_soup(commune['url'])
        if not soup:
            logger.error(f"Erreur lors de la récupération de la page pour {commune['nom']} - URL : {commune['url']}")
            continue
        logger.info(f"Commune à scrapper : {commune['nom']} - URL : {commune['url']}")
        # Ici on rajoute un test pour limiter au departement 
      
        if isin_departement("Indre-et-Loire", soup):
            logger.info(f"La commune {commune['nom']} est en Indre-et-Loire => On la scrappe")
            process_single_commune(commune, soup)
        else :
            # Si la commune n'est pas dans le département, on efface son noeud
            id_to_delete = commune_graph_service.get_commune_id_by_name_and_url(commune['nom'], commune['url'])
            commune_graph_service.delete_commune_by_id(id_to_delete)
            logger.info(f"La commune {commune['nom']} n'est pas en Indre-et-Loire => On supprime son noeud {id_to_delete}")


def isin_departement(dpt: str, soup: BeautifulSoup) -> bool:
    """Vérifie si la commune appartient à la région spécifiée"""
    # Ici on pourrait implémenter une logique plus complexe pour vérifier la région
    # Par exemple, en utilisant une liste de communes connues de cette région
    # Pour l'instant, on va juste vérifier si le nom de la commune contient le nom de la région
    print("Entree dans la fionction isin_departement")
    commune_info = get_infos_commune(soup)
    if not commune_info:
        logger.error(f"Erreur lors de la récupération des infos pour {get_commune_name(soup)}")
        return False
    
    extracted_dpt = commune_info.get('Département', None)
    if extracted_dpt is None:
        logger.error(f"Aucun département trouvé pour {get_commune_name(soup)}")
        return False
    
    if dpt in extracted_dpt:
        return True
    
    return False    

def process_single_commune(commune: dict, soup: BeautifulSoup) -> bool:
    """Traite une seule commune - retourne True si traitement réussi"""
    #logger.info(f"{commune['nom']} - ({commune['url']})")
    
    #if not commune['url']:
    #    return False
        
    try:
        #soup = get_soup(commune['url'])                
        infos_commune = get_infos_commune(soup)
        
        # Mettre à jour la commune avec les infos scrappées
        id_origin = commune_graph_service.create_commune_and_return_id(
            nom=commune['nom'].upper(),
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
                nom=commune['nom'].upper(),
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

def process_commune_limitrophes(id_origin: int, communes_limitrophes: dict):
    """Traite les communes limitrophes et crée les relations"""
    for direction, commune_to_register in communes_limitrophes.items():
        print(f"Orientation : {direction} : ")
        for commune_limits in commune_to_register:
            nom_comm_limit = commune_limits['nom'].upper()
            url_comm_limit = commune_limits['url']
            logger.info(f"Traitement de la commune limitrophe : {nom_comm_limit} - URL : {url_comm_limit}")
            
            id_limitrophe = None
            # Vérifier si la commune limitrophe a un nom et une URL            
            if nom_comm_limit and url_comm_limit:
                # Créer le noeud temporaire de la commune limitrophe
                # si le noeud n'existe pas
                id_limitrophe = commune_graph_service.get_commune_id_by_name_and_url(nom_comm_limit, url_comm_limit)
                if id_limitrophe is None:
                    logger.info(f"Création de la commune limitrophe {nom_comm_limit} avec l'URL {url_comm_limit}")
                    # Créer la commune limitrophe et récupérer son ID
                    # On marque scraped à False car on ne l'a pas encore scrappée
                    id_limitrophe = commune_graph_service.create_temporary_commune_and_return_id(
                        nom=nom_comm_limit,
                        url=url_comm_limit,
                        scraped=False
                    )
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
 

if "__name__" == "__main__":
       print("Pour test des fonctions)")
       # fill_graphe()
        

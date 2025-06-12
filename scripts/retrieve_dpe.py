# fonctions de récupération d'un dpe émis après juillet 2021.
# à partir de https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/
# Documentation : https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/api-docs.json


# Limitations : 
#  600 requêtes par intervalle de 60 secondes
#  Sa vitesse de téléchargement totale sera limitée à 2 MB/s pour les contenus statiques 
# (fichiers de données, pièces jointes, etc.) et à 500 kB/s pour les autres appels

import requests
import time
def retrieve_all_dpe_by_date(date_etablissement: str) -> list:
    """
    Récupère TOUS les DPE émis à une date donnée (avec pagination via next URL).
    Args:
        date_etablissement (str): La date d'établissement du DPE au format 'YYYY-MM-DD'.
    Returns:
        list: Une liste complète de tous les DPE de cette date.

    *** Note : cette méthode utilise l'URL de la page suivante fournie par l'API ***
    """
    base_url_dpe = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
    all_results = []
    page_size = 1000
    next_url = None
    page_num = 1
    fields = [
        "numero_dpe",
        "date_etablissement_dpe",
        "adresse_brut",
        "code_postal_brut",
        "adresse_ban",
        "identifiant_ban",
        "score_ban",
        "surface_habitable_logement",
        "etiquette_dpe",
        "etiquette_ges"
    ]
    while True:
        if next_url:
            # Utiliser l'URL complète fournie par l'API
            url = next_url
            params = {}
        else:
            # Première requête
            url = base_url_dpe
            params = {
                'qs': f"date_etablissement_dpe:{date_etablissement}",
            'size': page_size,
            'select': f"{','.join(fields)}"
            }
        
        print(f"Page {page_num} - URL: {url}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            if not results:  # Plus de résultats
                break
                
            all_results.extend(results)
            print(f"Page {page_num}: {len(results)} DPE récupérés (Total: {len(all_results)})")
            
            # Récupérer l'URL de la page suivante
            next_url = data.get('next')
            if not next_url:  # Plus de pages
                break
                
            page_num += 1
            time.sleep(0.1)  # Respect des limites API
            
        except requests.RequestException as e:
            print(f"Erreur page {page_num}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            break
    
    print(f"Total final: {len(all_results)} DPE pour le {date_etablissement}")
    return all_results


def retrieve_all_dpe_by_date_bak(date_etablissement: str) -> list:
    """
    Récupère TOUS les DPE émis à une date donnée (avec pagination).
    *** Limits : L'API ne fournit pqas plus de 10000 résultats avec cette methode. ***

    Args:
        date_etablissement (str): La date d'établissement du DPE au format 'YYYY-MM-DD'.
        
    Returns:
        list: Une liste complète de tous les DPE de cette date.
        
    *** Note : cette méthode utilise la pagination par page et non l'URL de la page suivante fournie par l'API ***
    *** Limits : L'API ne fournit pqas plus de 10000 résultats avec cette methode. ***
    """
    
    base_url_dpe = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
    all_results = []
    page = 1
    page_size = 1000
    fields = [
        "numero_dpe",
        "date_etablissement_dpe",
        "adresse_brut",
        "code_postal_brut",
        "adresse_ban",
        "identifiant_ban",
        "score_ban",
        "surface_habitable_logement",
        "etiquette_dpe",
        "etiquette_ges"
    ]
    
    while True:
        params = {
            'qs': f"date_etablissement_dpe:{date_etablissement}",
            'size': page_size,
            'page': page,
            'select': f"{','.join(fields)}"
        }

        try:
            response = requests.get(base_url_dpe, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            if not results:  # Plus de résultats
                break
                
            all_results.extend(results)
            print(f"Page {page + 1}: {len(results)} DPE récupérés (Total: {len(all_results)})")
            
            # Vérifier s'il y a encore des pages
            if len(results) < page_size:  # Dernière page
                break
                
            page += 1
            time.sleep(0.1)  # Respect des limites API
            
        except requests.RequestException as e:
            print(f"Erreur page {page}: {str(e)}")
            break
    
    print(f"Total final: {len(all_results)} DPE pour le {date_etablissement}")
    return all_results

def main():
    """
    Fonction de test de la fonction retrieve_all_dpe_by_date(date_etablissement)
    
    Returns:
        None
    """
    date_etablissement = "2025-05-27"  # Exemple de date
    dpe_list = retrieve_all_dpe_by_date(date_etablissement)
    
    if dpe_list:
        print(f"Nombre total de DPE récupérés pour le {date_etablissement}: {len(dpe_list)}")
        """print("Exemples de DPE récupérés:")
        for dpe in dpe_list[:10]:
            print(f"numero_dpe : {dpe.get('numero_dpe')} \
                \ndate_etablissement_dpe : {dpe.get('date_etablissement_dpe')} \
                \nadresse_brut : {dpe.get('adresse_brut')} \
                \ncode_postal_brut: {dpe.get('code_postal_brut')} \
                \nadresse_ban : {dpe.get('adresse_ban')} \
                \nidentifiant_ban : {dpe.get('identifiant_ban')} \
                \nscore_ban : {dpe.get('score_ban')} \
                \nsurface_habitable_logement : {dpe.get('surface_habitable_logement')} \
                \nEtiquette DPE: {dpe.get('etiquette_dpe')} \
                \nEtiquette GES: {dpe.get('etiquette_ges')}")  
            print("-" * 80)"""
    else:
        print("Aucun DPE trouvé pour cette date.")

if __name__ == "__main__":
    main()

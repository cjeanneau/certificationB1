import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging

base_url = "https://fr.wikipedia.org"

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

# verif robots.txt
#robots_url = f"{base_url}/robots.txt" 
#response = requests.get(robots_url)
#print("Règles robots.txt : ")
#print(response.text[:500])  

### On peut scrapper la page car il n'y a pas de restriction dans le fichier robots.txt


def get_soup(url: str) -> BeautifulSoup:
    """Récupère le contenu HTML d'une page et le parse avec BeautifulSoup"""
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Page récupérée avec succès : {response.status_code}")
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def get_commune_name(soup: BeautifulSoup) -> str:
    """Récupère le nom de la commune à partir du titre de la page"""
    title = soup.find('h1', class_='firstHeading')
    if title:
        commune_name = title.text.strip()
        return commune_name
    else:
        print("Titre de la page introuvable.")
        return None

def get_infos_commune(soup: BeautifulSoup) -> dict:
    #response = requests.get(url_commune, headers=headers)
    #response.raise_for_status()
    #print(f"Page récupérée avec succès : {response.status_code}")
    #html_content = response.text

    #Parse le contenu HTML avec BeautifulSoup
    #soup = BeautifulSoup(html_content, 'html.parser')

    # on récupère le titre de la page pour le nom de la commune
    #title = soup.find('h1', class_='firstHeading')
    #commune_name = title.text.strip()
    #print(f"Titre de la page : {commune_name}")

    # On définit notre dictionnaire pour stocker les infos
    info_dict = {}

    # On récupère les liens infos sur le cadre à doite de lq page
    infobox = soup.find('table', class_='infobox_v2')

    if infobox is None:
        print("Aucune infobox trouvée pour cette commune.")
        return info_dict
    
    # On récupère les lignes <tr>de l'infobox
    rows = infobox.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])
        if len(cells) >= 2:
            label = cells[0].get_text().strip()
            value = cells[1].get_text().strip()
            info_dict[label] = value
    return info_dict


def get_communes_limitrophes(soup: BeautifulSoup) -> dict:
    
    title = soup.find('h1', class_='firstHeading')
    ville = title.text.strip()

    h2_geo = soup.find('h2', id='Géographie')
    if not h2_geo:
        print("{ville} : Aucun chapitre Géographie trouvé dans la page.")
        return {}
    
    print(f"{ville} : Chapitre Géographie trouvé !")
    current_element = h2_geo.parent.find_next_sibling()
    
    # Orientations cardinales pour tableau 3x3
    orientations = [
        ['Nord-Ouest', 'Nord', 'Nord-Est'],
        ['Ouest', 'Centre', 'Est'],
        ['Sud-Ouest', 'Sud', 'Sud-Est']
    ]

    while current_element:
        # On parcours tous les éléments du chapitre h2 Géographie jusuq'au chapitre h2 suivant
        if current_element.find('h2'):
            print("On a trouvé un h2, on sort de la boucle")
            break
        
        # Chercher une table dans l'élément courant
        # selon les villes, il peut y avoir plusieurs tables masi une seule nous intéresse
        table = current_element.find('table')
        if table:
            caption = table.find('caption')
            caption_value = caption.get_text() if caption else "Pas de caption"
            print(f"Table caption : {caption_value}")

            # On traite la table dont Caption est "Communes limitrophes de {ville}"
            if caption and f"Communes limitrophes de {ville}" in caption.get_text():
                print(f"{ville} :Tableau des communes limitrophes trouvé !")
                tbody = table.find('tbody')
                rows = tbody.find_all('tr')

                '''
                ****** Ca fonctionne mais pas tres lisible => Réécriture pour plus de clarté ******
                # Extraire les noms des communes depuis les liens
                communes_dict = {}
                cell_index = 0
                for row in rows:
                    cells = row.find_all('td')
                    for cell in cells:
                        communes = []
                        links = cell.find_all('a')
                        for link in links:
                            commune = link.get_text()
                            href = link.get('href')
                            communes.append((commune, href))
                        cell_index += 1
                        communes_dict[cell_index] = communes

                print("Communes limitrophes :", communes)
                '''
                # Réécriture pour plus de clarté
                # On initialise un dictionnaire pour stocker et retourner les communes limitrophes
                communes_limitrophes = {}
                
                # Lecture de chaque ligne <tr> contenant les 3 lignes <td>
                for row_idx, row in enumerate(rows):
                    cells = row.find_all('td')
                    
                    # Lecture de chaque cellule <td> contenant des balises <a>
                    for cell_idx, cell in enumerate(cells):
                        # On vérifie qu'on est dans les limites du tableau 3x3
                        if row_idx < 3 and cell_idx < 3:
                            orientation = orientations[row_idx][cell_idx]
                            
                            # On extrait les communes de cette cellule
                            communes_in_cell = []
                            links = cell.find_all('a')
                            
                            for link in links:
                                commune_name = link.get_text().strip()
                                commune_href = link.get('href')
                                commune_url = base_url + commune_href if commune_href else None
                                
                                communes_in_cell.append({
                                    'nom': commune_name,
                                    'url': commune_url
                                })
                            
                            # Si pas de liens, récupérer le texte brut
                            if not communes_in_cell:
                                text_content = cell.get_text().strip()
                                if text_content and text_content != ville:  # Éviter la ville centrale
                                    communes_in_cell.append({
                                        'nom': text_content,
                                        'url': None
                                    })
                            
                            # Ajouter au dictionnaire final
                            if communes_in_cell:
                                communes_limitrophes[orientation] = communes_in_cell
                return communes_limitrophes
        current_element = current_element.find_next_sibling()
    return {}
    

if  __name__ == "__main__":
    
    # Exemple d'utilisation pour test

    start_url =f"{base_url}/wiki/Tours"
    soup_tours = get_soup(start_url)
    dict = get_infos_commune(soup_tours)
    print ("="*50)
    for row in dict:
        print(f"{row} : {dict[row]}")
    print ("="*50)
    dict2 = get_communes_limitrophes(soup_tours)
    for key, value in dict2.items():
        print(f"Cellule {key} : {value}")
    print ("="*50)
    print ("="*50)
    

    url_ndoe = "https://fr.wikipedia.org/wiki/Notre-Dame-d%27O%C3%A9"
    soup_ndoe = get_soup(url_ndoe)
    dict_ndoe = get_infos_commune(soup_ndoe)
    print ("="*50)
    for row in dict_ndoe:
        print(f"{row} : {dict_ndoe[row]}")
    print ("="*50)
    dict2_ndoe = get_communes_limitrophes(soup_ndoe)
    for key, value in dict2_ndoe.items():
        print(f"Cellule {key} : {value}")

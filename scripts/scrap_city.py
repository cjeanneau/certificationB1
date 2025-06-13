import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import logging

base_url = "https://fr.wikipedia.org"
start_url =f"{base_url}/wiki/Tours"

# verif robots.txt
robots_url = f"{base_url}/robots.txt" 
response = requests.get(robots_url)
#print("Règles robots.txt : ")
#print(response.text[:500])  

# on recupere la page
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
response = requests.get(start_url, headers=headers)
response.raise_for_status()
print(f"Page récupérée avec succès : {response.status_code}")
html_content = response.text

"""Parse le contenu HTML avec BeautifulSoup"""
soup = BeautifulSoup(html_content, 'html.parser')

# on récupère le titre de la page
title = soup.find('h1', class_='firstHeading')
print(f"Titre de la page : {title.text.strip()}")

# On récupère les liens infos sur le cadre à doite de lq page
infobox = soup.find('table', class_='infobox_v2')
rows = infobox.find_all('tr')
for row in rows:
    # Chercher les cellules
    cells = row.find_all(['th', 'td'])
    if len(cells) >= 2:
        label = cells[0].get_text().strip()
        value = cells[1].get_text().strip()
        # On récupère les champs qui nous intéressent
        # Code postal
        if 'Codes postal' in label:
            print(f"Code(s) postal(aux) : {value}")
        # Région
            print(f"Région : {value}")
        # Pays
        if 'Pays' in label:
            print(f"Pays : {value}")

h2_geo = soup.find('h2', id='Géographie')
current_element = h2_geo.parent.find_next_sibling()

while current_element:
    # Condition de sortie : si on trouve un div contenant un h2
    #print(f"Current element : {current_element.name}")
    #print(f"Current element find h2 : {current_element.find('h2')}")
    if current_element.find('h2'):
        print("On a trouvé un h2, on sort de la boucle")
        break
    
    # Chercher une table dans l'élément courant
    table = current_element.find('table')
    if table:
        caption = table.find('caption')
        caption_value = caption.get_text() if caption else "Pas de caption"
        print(f"Table caption : {caption_value}")
        if caption and f"Communes limitrophes de {title.text.strip()}" in caption.get_text():
            print("Caption trouvée !")
            table_communes = table
            if table_communes is not None:
                print("Table trouvée avec succès")
                tbody = table_communes.find('tbody')
                rows = tbody.find_all('tr')

                # Extraire les noms des communes depuis les liens
                communes = []
                for row in rows:
                    cells = row.find_all('td')
                    for cell in cells:
                        links = cell.find_all('a')
                        for link in links:
                            communes.append(link.get_text())

                print("Communes limitrophes :", communes)
            else:
                print("table_communes est None - problème inattendu")

            #break
    
    current_element = current_element.find_next_sibling()

"""
if table_communes is not None:
    print("Table trouvée avec succès")
    tbody = table_communes.find('tbody')
    rows = tbody.find_all('tr')

    # Extraire les noms des communes depuis les liens
    communes = []
    for row in rows:
        cells = row.find_all('td')
        for cell in cells:
            links = cell.find_all('a')
            for link in links:
                communes.append(link.get_text())

    print("Communes limitrophes :", communes)
else:
    print("table_communes est None - problème inattendu")




section_geographie = soup.find('h2', id='Géographie')
print(f"section geogaphie find 'h2' : {section_geographie.name}")
section_geographie = section_geographie.parent
print(f"section geogaphie parent : {section_geographie.name}")

while section_geographie.name:
    print(section_geographie.contents[0].name)
    if section_geographie.name == 'h2':
        break
    section_geographie = section_geographie.find_next_sibling()
    #print(f"section geogaphie apres next_sibling : {section_geographie.name}")
    # On affiche le contenu de la section géographie        
    #print("Section Géographie :")
    #print(section_geographie.name)
    #print(len(section_geographie.find_all('table')))
    is_h2 = section_geographie.name == 'h2'
    table_communes = section_geographie.find('table')
    #print("table_communes est :", table_communes)
    #print("Type :", type(table_communes))

    if table_communes is not None:
        print("Table trouvée avec succès")
        tbody = table_communes.find('tbody')
        rows = tbody.find_all('tr')

        # Extraire les noms des communes depuis les liens
        communes = []
        for row in rows:
            cells = row.find_all('td')
            for cell in cells:
                links = cell.find_all('a')
                for link in links:
                    communes.append(link.get_text())

        print("Communes limitrophes :", communes)
    else:
        print("table_communes est None - problème inattendu")
    
    input()
"""
# app/services/neo4j_commune_service.py
from typing import List, Dict, Optional
from .neo4j_connection import neo4j_service

class CommuneGraphService:
    def __init__(self):
        self.neo4j = neo4j_service
    
    def create_temporary_commune_and_return_id(self, nom: str, url: str = None, scraped: bool = False) -> Optional[int]:
        """Crée une commune et retourne son ID Neo4j ou None si l'opération échoue."""
        
        query = """
        MERGE (c:Commune {nom: $nom, url: $url}) 
        SET c.scraped = $scraped,
            c.updated_at = datetime()
        RETURN id(c) as node_id, c
        """

        result = self.neo4j.execute_write(query, {
            'nom': nom,
            'url': url,
            'scraped': scraped
        })
        return result['node_id'] if result else None
    

    def create_commune_and_return_id(self, nom: str, pays: str, departement: str, code_postaux: str, code_commune: str, region: str = None, url: str = None, scraped: bool = False) -> Optional[int]:
        """Crée une commune et retourne son ID Neo4j ou None si l'opération échoue"""
        
        # On cherche d'abord à mettre à jour un nœud existant basé sur nom et url
        # (car c'est comme ça que le nœud temporaire a été créé)
        query = """
        MERGE (c:Commune {nom: $nom, url: $url})
        SET c.pays = $pays,
            c.region = $region,
            c.departement = $departement,
            c.code_postaux = $code_postaux,
            c.code_commune = $code_commune,
            c.scraped = $scraped,
            c.updated_at = datetime()
        RETURN id(c) as node_id
        """
        
        result = self.neo4j.execute_write(query, {
            'nom': nom,
            'pays': pays,
            'region': region,
            'departement': departement,
            'code_postaux': code_postaux,
            'code_commune': code_commune,
            'url': url,
            'scraped': scraped
        })
            
        return result['node_id'] if result else None
    

    '''def create_commune_and_return_id(self, nom: str, pays: str, departement: str, code_postaux: str, code_commune: str, region: str = None, url: str = None, scraped: bool = False) -> Optional[int]:
        """Crée une commune et retourne son ID Neo4j ou None  si l'opération échoue"""

        if code_commune:
            print("# Le code commune existe donc on peut merger sur ce code")
            query = """
            MERGE (c:Commune {code_commune: $code_commune})
            SET c.nom = $nom,
                c.pays = $pays,
                c.region = $region,
                c.departement = $departement,
                c.code_postaux = $code_postaux,
                c.url = $url,
                c.scraped = $scraped,
                c.updated_at = datetime()
            RETURN id(c) as node_id, c
            """
        else:
            # Le code commune n'existe pas c'est le caas de la création d'une noeud temporaire
            print("# on merge alors sur nom et url")
            query = """
            MERGE (c:Commune {nom: $nom, url: $url})
            SET c.pays = $pays,
                c.region = $region,
                c.departement = $departement,
                c.code_postaux = $code_postaux,
                c.scraped = $scraped,
                c.updated_at = datetime()
            RETURN id(c) as node_id
            """

        result = self.neo4j.execute_write(query, {
            'nom': nom,
            'pays': pays,
            'region': region,  
            'departement': departement,
            'code_postaux': code_postaux,
            'code_commune': code_commune,
            'url': url,
            'scraped': scraped
        })
        return result['node_id'] if result else None
    '''
    '''
    def create_commune(self, nom: str, pays: str, departement: str, code_postaux: str, code_commune: str, region: str = None, url: str = None, scraped: bool = False):
        """Crée ou met à jour une commune dans le graphe"""
        query = """
        MERGE (c:Commune {code_commune: $code_commune})
        SET c.nom = $nom,
            c.pays = $pays,
            c.region = $region,
            c.departement = $departement,
            c.code_postaux = $code_postaux,
            c.url = $url,
            c.scraped = $scraped,
            c.updated_at = datetime()
        RETURN c
        """
        return self.neo4j.execute_write(query, {
            'nom': nom,
            'pays': pays,
            'region': region,  
            'departement': departement,
            'code_postaux': code_postaux,
            'code_commune': code_commune,
            'url': url,
            'scraped': scraped
        })
'''
    


        
    # Méthodes avec graphe orienté
    def add_relation_limitrophe(self, code_commune_origin: str, code_commune_target: str, direction: str):
        """Ajoute une relation limitrophe **ORIENTE** entre deux communes"""
        query = """
        MATCH (c1:Commune {code_commune: $code_origin})
        MATCH (c2:Commune {code_commune: $code_target})
        MERGE (c1)-[r:LIMITROPHE {direction: $direction}]->(c2)
        SET r.created_at = datetime()
        RETURN r
        """
        return self.neo4j.execute_write(query, {
            'code_origin': code_commune_origin,
            'code_target': code_commune_target,
            'direction': direction
        })
    
    def add_relation_limitrophe_by_id_bak(self, node_id_origin: int, node_id_target: int, direction: str):
        """Ajoute une relation limitrophe en utilisant les IDs des nœuds"""
        query = """
        MATCH (c1:Commune) WHERE id(c1) = $id_origin
        MATCH (c2:Commune) WHERE id(c2) = $id_target
        MERGE (c1)-[r:LIMITROPHE {direction: $direction}]->(c2)
        SET r.created_at = datetime()
        RETURN r
        """
        return self.neo4j.execute_write(query, {
            'id_origin': node_id_origin,
            'id_target': node_id_target,
            'direction': direction
        })
    

    def add_relation_limitrophe_by_id(self, node_id_origin: int, node_id_target: int, direction: str):
        """Ajoute une relation limitrophe en utilisant les IDs des nœuds"""
        query = """
        MATCH (c1:Commune) WHERE id(c1) = $id_origin
        MATCH (c2:Commune) WHERE id(c2) = $id_target
        MERGE (c1)-[r:LIMITROPHE]->(c2)
        ON CREATE SET r.direction = [$direction], r.created_at = datetime()
        ON MATCH SET r.direction = CASE 
            WHEN $direction IN r.direction THEN r.direction 
            ELSE r.direction + [$direction] 
        END
        RETURN r
        """
        return self.neo4j.execute_write(query, {
            'id_origin': node_id_origin,
            'id_target': node_id_target,
            'direction': direction
        })
    
    def get_communes_limitrophes(self, code_commune: str) -> List[Dict]:
        """Récupère toutes les communes limitrophes (**ORIENTE**)"""
        query = """
        MATCH (c:Commune {code_commune: $code_commune})-[r:LIMITROPHE]->(limitrophe:Commune)
        RETURN limitrophe.name as name, 
               limitrophe.code_commune as code_commune,
               limitrophe.region as region,
               r.direction as direction
        ORDER BY r.direction, limitrophe.name
        """
        return self.neo4j.execute_query(query, {'code_commune': code_commune})
    
    def get_commune_id_by_name(self, nom: str) -> Optional[int]:
        """Récupère l'ID d'une commune par son nom"""
        query = """
        MATCH (c:Commune {nom: $nom})
        RETURN id(c) as node_id
        """
        result = self.neo4j.execute_query(query, {'nom': nom})
        return result[0]['node_id'] if result else None

    def get_communes_by_direction(self, code_commune: str, direction: str) -> List[Dict]:
        """Récupère les communes dans une direction spécifique"""
        query = """
        MATCH (c:Commune {code_commune: $code_commune})-[r:LIMITROPHE {direction: $direction}]->(limitrophe:Commune)
        RETURN limitrophe.name as name, 
               limitrophe.code_commune as code_commune,
               limitrophe.region as region
        ORDER BY limitrophe.name
        """
        return self.neo4j.execute_query(query, {
            'code_commune': code_commune,
            'direction': direction
        })
    
    def mark_commune_as_scraped(self, code_commune: str):
        """Marque une commune comme scrappée"""
        query = """
        MATCH (c:Commune {code_commune: $code_commune})
        SET c.scraped = true, c.scraped_at = datetime()
        RETURN c
        """
        return self.neo4j.execute_write(query, {'code_commune': code_commune})
    
    def mark_commune_as_scraped_by_id(self, node_id: int):
        """Marque une commune comme scrappée"""
        query = """
        MATCH (c:Commune) WHERE id(c) = $id
        SET c.scraped = true, c.scraped_at = datetime()
        RETURN c
        """
        return self.neo4j.execute_write(query, {'id': node_id})
    
    def get_communes_not_scraped(self) -> List[Dict]:
        """Récupère les communes pas encore scrappées"""
        query = """
        MATCH (c:Commune)
        WHERE c.scraped = false OR c.scraped IS NULL
        RETURN c.nom as nom, c.code_commune as code_commune, c.url as url
        ORDER BY c.nom
        """
        return self.neo4j.execute_query(query)
    
    def get_communes_not_scraped_by_region(self, region: str = None) -> List[Dict]:
        """Récupère les communes pas encore scrappées d'une région spécifique"""
        query = """
        MATCH (c:Commune)
        WHERE (c.scraped = false OR c.scraped IS NULL)
        AND ($region IS NULL OR c.region = $region OR c.region IS NULL)
        RETURN c.nom as nom, c.code_commune as code_commune, c.url as url
        ORDER BY c.nom
        """
        return self.neo4j.execute_query(query, {'region': region})


    def get_commune_stats(self, code_commune: str) -> Dict:
        """Statistiques d'une commune (nombre de voisins par direction)"""
        query = """
        MATCH (c:Commune {code_commune: $code_commune})-[r:LIMITROPHE]->(limitrophe:Commune)
        RETURN r.direction as direction, count(limitrophe) as count
        ORDER BY direction
        """
        return self.neo4j.execute_query(query, {'code_commune': code_commune})

    def clear_database(self):
        """Supprime toutes les communes et relations"""
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        return self.neo4j.execute_write(query)
    

# Instance globale
commune_graph_service = CommuneGraphService()

if __name__ == "__main__":

    # Exemple d'utilisation

    # Nettoyer la base avant les tests
    commune_graph_service.clear_database()  
    
    
    # Créer ou mettre à jour une commune
    commune_graph_service.create_commune(nom="Tours", code_commune="37000", pays="fr", departement="IetL",code_postaux="37000", region="Test Region", url="http://example.com", scraped=False)
    print("Commune Tours créée ou mise à jour.")
    commune_graph_service.create_commune(nom="Mettray", code_commune="37130", pays="fr", departement="IetL",code_postaux="37000", region="Test Region", url="http://example.com/test2", scraped=False)
    print("Commune Mettray créée ou mise à jour.")

    # Ajouter une relation limitrophe orientée
    commune_graph_service.add_relation_limitrophe("37000", "37130", "Nord")
    print("Relation limitrophe orientée ajoutée.")
    commune_graph_service.add_relation_limitrophe("37130", "37000", "Sud")
    
    print("Relation limitrophe orientée ajoutée.")
    # Récupérer les communes limitrophes orientées
    limitrophes = commune_graph_service.get_communes_limitrophes("37000")
    print("Limitrophes orientées de 12345 :", limitrophes)
    
    limitrophes = commune_graph_service.get_communes_limitrophes("37130")
    print("Limitrophes orientées de 67890:", limitrophes)
    
    # Marquer la commune comme scrappée
    #commune_graph_service.mark_commune_as_scraped("12345")
    print("Commune marquée comme scrappée.")
    
    # Récupérer les communes non scrappées
    non_scrapées = commune_graph_service.get_communes_not_scraped()
    print("Communes non scrappées:", non_scrapées)

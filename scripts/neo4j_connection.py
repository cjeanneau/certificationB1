# app/services/neo4j_connection.py
from neo4j import GraphDatabase
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "admin_neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Exécute une requête et retourne les résultats"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Exécute une requête d'écriture"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return result.single()

# Instance globale
neo4j_service = Neo4jService()
from fastapi import FastAPI
from sqlmodel import SQLModel, select


from bddpg import get_session_sync, commune_crud, create_db_and_tables
from bddn4j import commune_graph_service, neo4j_service

from api.auth_routes import router as auth_router
from api.dpe_routes import router as dpe_router
from api.eval_routes import router as eval_router


# Crée ou met à jour les  les tables PostgreSQL avec SQLModel
#postgres_engine = get_engine()
#SQLModel.metadata.create_all(postgres_engine)
create_db_and_tables(drop=False)  # Ne pas supprimer les tables existantes

app = FastAPI(
    title="API Immobilier - Données DVF & Communes",
    description="API pour les données de DPE récents, et valeurs immobilières avec Neo4j (graphe des communes) et PostgreSQL (DVF, DPE)",
    version="1.0.0"
)

# routage des points d'authentification
app.include_router(auth_router)      # Routes d'authentification
app.include_router(dpe_router)      # Routes pour les DPE
app.include_router(eval_router)     # Routes pour l'évaluation immobilière

@app.get("/")
def welcome():
    return {
        "message": "API Immobilier v1.0 - Multi-bases ! 🏠📊",
        "description": "Données immobilières et communes limitrophes",
        "features": [
            "Graphe des communes (Neo4j)",
            "Données DVF (PostgreSQL)",
            "Scrapping Wikipedia des communes",
            "Relations géographiques"
        ],
        "databases": {
            "neo4j": "Graphe des communes et relations limitrophes",
            "postgresql": "Données DVF et DPE"
        },
        "endpoints": {
            "info": ["GET /", "GET /health"],
            "communes": "À implémenter selon vos besoins",
            "dvf": "À implémenter selon vos besoins"
        }
    }

@app.get("/health")
def health_check():
    """Vérification de santé des 2 bases de données"""
    # On teste la disponibilité de la base postgresql
    try:
        with get_session_sync() as session:
            # Test de connexion à PostgreSQL
            #result = session.exec(select(Commune).limit(1))
            result = commune_crud.get_all(session)
            postgres_status = "ok" if result else "error"
            postgres_data = "available" if result else "unavailable"

    except Exception as e:
            postgres_status = f"error: {str(e)}"
            postgres_data = {"error": "Connection failed"}
        

    # On teste la disponibilité de la base Neo4j
    try:
        query = "MATCH (n:Commune) RETURN n LIMIT 1"
        result = neo4j_service.execute_query(query)
        neo4j_status = "ok" if result else "error"
        neo4j_data = "available" if result else "unavailable"
    except Exception as e:
        neo4j_status = f"error: {str(e)}"
        neo4j_data = {"error": "Connection failed"}


    overall_status = "ok" if postgres_status == "ok" and neo4j_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "version" : "1.0.0",
        "security": "JWT enabled", 
        "databases": {
             "postgresql":{
                    "status": postgres_status,
                    "data": postgres_data
             },
             "neo4j":{
                    "status": neo4j_status,
                    "data": neo4j_data
             }
        }
    }



if __name__ == "__main__":
    import uvicorn
    print("Démarrage de l'API Immobilier...")
    print("PostgreSQL: Données DVF et DPE")
    print("Neo4j: Graphe des communes")
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    print("API Immobilier démarrée sur http://localhost:8000")
    print("Utilisez Swagger UI pour explorer les endpoints : http://localhost:8000/docs")
    print("Bonne utilisation ! 🏠📊")

# Projet de certification Dev IA Bloc1

# Démarrage/arrêt des containers contenant les Bases de données Neo4j et PostgreSql

``` bash
cd PROJECT_DIRECTORY
docker-compose up       # pour démarrer les containers
docker-compose down     # pour arrêter les containers
```

# Creation de la database, des tables
# Remplissage dela base postgreSQL (using file and API requests)
# Remplissage de la base Neo4j (using scraping)
```bash
cd [...]/certificationB1/
python load_data.py # inside teh script, lines can be commented 
```

# Execution du serveur fastapi:

```bash
cd [...]/certificationB1/
uvicorn app.main:app --reload
```

# Structure du projet 

    # TO BE UPDATED #
.
├── api
│   ├── __init__.py
│   └── README.md
├── bddn4j
│   ├── __init__.py
│   ├── neo4j_commune_service.py
│   └── neo4j_connection.py
├── bddpg
│   ├── crud
│   │   ├── __init__.py
│   │   ├── bien_immobilier.py
│   │   ├── commune.py
│   │   ├── dpe.py
│   │   ├── test_crud.py
│   │   └── transaction_dvf.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── bien_immobilier.py
│   │   ├── commune.py
│   │   ├── dpe.py
│   │   └── transaction_dvf.py
│   ├── __init__.py
│   ├── create_db_pgsql.py
│   └── database.py
├── data_process
│   ├── external_api
│   │   ├── __init__.py
│   │   ├── retrieve_dpe.py
│   │   └── retrieve_id_ban.py
│   ├── scraping
│   │   ├── __init__.py
│   │   └── scrap_city.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── __init__.py
│   ├── fill_communes.py
│   ├── fill_dvf.py
│   └── fill_graphe.py
├── config.py
├── docker-compose.yml
├── dockerfile
├── load_data.py
├── main.py
├── README.md
└── requirements.txt


# Projet de certification Dev IA Bloc1

### 1. Cloner le dépôt

```bash
git clone PROJECT_DIRECTORY
   cd PROJECT_DIRECTORY
```
### 2. Copier .env.example en .env
```bash
cp .env.example .env
```

### 3.Editer et compléter le fichier .env
```bash
nano .env # ou tout autre édietru de votre choix
```

### 4. Démarrage/arrêt des containers contenant les Bases de données Neo4j et PostgreSql

``` bash
docker-compose up       # pour démarrer les containers
# docker-compose down     # pour arrêter les containers
```
### 5. Vérification du fonctionnement
```bash 
docker-compose ps
docker-compose logs
```

## Récolte des donnees et remplissage des bases

### 6. script de remplissage des bases
```bash
python load_data.py #  script dont les lignes peuvent etre commentées
```

## Démarrage de l'application fastapi

### 7. Mise en place de l'environnement 
```bash
 python3 -m venv ENV
 source ENV/bin/activate 
 pip install -r requirements.txt
 ```

 ### 8. Démarrage du serveur fastapi
```bash
python main.py
```

## Accès aux services :

On considère une installation locale, dans le cas contraire il faudra adapter le localhost par le nom de domaine ou l'adresse ip.

serveur fastapi : localhost:8000/
Swagger UI : localhost:8000/docs

BDD PostgreSql : localhost:5432 
(pas d'interface web, utiliser un outil comme DBeaver, pgAdmin ou autre)

BDD neo4j : localhost:7687
Interface web : localhost:7474


## Structure du projet 

.
├── api
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── dpe_routes.py
│   └── eval_routes.py
├── auth
│   ├── __init__.py
│   ├── auth_service.py
│   ├── dependencies.py
│   └── jwt_handler.py
├── bddn4j
│   ├── __init__.py
│   ├── neo4j_commune_service.py
│   └── neo4j_connection.py
├── bddpg
│   ├── crud
│   ├── models
│   ├── __init__.py
│   ├── create_db_pgsql.py
│   ├── database.py
│   ├── restore_pgsql.sh
│   └── save_pgsql.sh
├── data_process
│   ├── external_api
│   ├── scraping
│   ├── utils
│   ├── __init__.py
│   ├── fill_communes.py
│   ├── fill_dvf.py
│   └── fill_graphe.py
├── exceptions
│   └── custom_exceptions.py
├── schemas
│   ├── __init__.py
│   ├── dpe.py
│   └── response.py
├── services
│   ├── __init__.py
│   ├── dpe_services.py
│   └── eval_services.py
├── config.py
├── create_users.py
├── docker-compose.yml
├── dockerfile
├── load_data.py
├── main.py
├── README.md
└── requirements.txt



## PostgreSQL : Processus de sauvegarde et restauration de la base de donnees 

## Sauvegarde
### Prérequis : Avoir un fichier .env convenablement configuré
```bash
cd PROJECT_DIRECTORY/bddpg
chmod +x save_pgsql.sh
./save_pgsql.sh
```

## Restauration
```bash
cd PROJECT_DIRECTORY/bddpg
chmod +x restore_pgsql.sh
./restore_pgsql.sh {DB_NAME}_dump_${TIMESTAMP}.sql.gz
```


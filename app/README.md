# Structure du projet recommandée
project/
├── config.py              # Configuration de la base de données
├── database.py            # Configuration SQLModel et connexion
├── models/
│   ├── __init__.py
│   ├── commune.py         # Modèle Commune
│   ├── bien_immobilier.py # Modèle Bien Immobilier
│   ├── transaction_dvf.py # Modèle Transaction DVF
│   └── dpe.py             # Modèle DPE
├── crud/
│   ├── __init__.py
│   ├── commune.py         # CRUD Commune
│   ├── bien_immobilier.py # CRUD Bien Immobilier
│   ├── transaction_dvf.py # CRUD Transaction DVF
│   └── dpe.py             # CRUD DPE
├── schemas/
│   ├── __init__.py
│   ├── commune.py         # Schémas Pydantic pour API
│   ├── bien_immobilier.py
│   ├── transaction_dvf.py
│   └── dpe.py
├── services/
│   ├── __init__.py
│   └── statistics.py     # Services métier (statistiques, etc.)
├── main.py               # Point d'entrée FastAPI
└── create_tables.py      # Script de création des tables

# Creation de la database et des tables
```bash
cd [...]/certificationB1/
python -m app.create_database
```

# Execution du serveur fastapi:

```bash
cd [...]/certificationB1/
uvicorn app.main:app --reload
```

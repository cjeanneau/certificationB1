#!/bin/bash

# Charger les variables d'environnement depuis le fichier .env
if [ -f ../.env ]; then
    export $(grep -v '^#' ../.env | sed 's/[[:space:]]*=[[:space:]]*/=/' | xargs)
else
    echo "Erreur: Le fichier .env est introuvable"
    exit 1
fi

# Vérifier que toutes les variables nécessaires sont définies
if [ -z "$DB_NAME" ] || [ -z "$PG_USER" ] || [ -z "$PG_PASSWORD" ] || [ -z "$PG_HOST" ] || [ -z "$PG_PORT" ]; then
    echo "Erreur: Une ou plusieurs variables d'environnement manquent (DB_NAME, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT)"
    exit 1
fi

# Générer le nom du fichier de dump avec timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILE="${DB_NAME}_dump_${TIMESTAMP}.sql.gz"

echo "Début du dump de la base de données $DB_NAME..."
echo "Fichier de sortie: $DUMP_FILE"

# Exporter le mot de passe pour éviter la demande interactive
export PGPASSWORD="$PG_PASSWORD"

# Effectuer le dump
pg_dump -c -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB_NAME" | gzip -c > "$DUMP_FILE"

# Vérifier si le dump s'est bien passé
if [ $? -eq 0 ]; then
    echo "Dump réussi: $DUMP_FILE"
    echo "Taille du fichier: $(du -h "$DUMP_FILE" | cut -f1)"
else
    echo "Erreur lors du dump"
    exit 1
fi


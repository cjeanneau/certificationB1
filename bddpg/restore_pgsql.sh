#!/bin/bash

# Charger les variables d'environnement depuis le fichier .env
if [ -f ../.env ]; then
    export $(grep -v '^#' ../.env | sed 's/[[:space:]]*=[[:space:]]*/=/' | xargs)
else
    echo "Erreur: Le fichier .env est introuvable"
    exit 1
fi

# Vérifier que le nom de base est défini
if [ -z "$DB_NAME" ]; then
    echo "Erreur: La variable DB_NAME est obligatoire"
    exit 1
fi

# Définir des valeurs par défaut
PG_HOST=${PG_HOST:-localhost}
PG_PORT=${PG_PORT:-5432}
PG_USER=${PG_USER:-$(whoami)}

# Vérifier qu'un fichier de dump est fourni en argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <fichier_dump.sql.gz>"
    echo "Exemple: $0 mabase_dump_20250623_143022.sql.gz"
    exit 1
fi

DUMP_FILE="$1"

# Vérifier que le fichier existe
if [ ! -f "$DUMP_FILE" ]; then
    echo "Erreur: Le fichier $DUMP_FILE n'existe pas"
    exit 1
fi

echo "Restauration de la base de données $DB_NAME depuis $DUMP_FILE..."

# Exporter le mot de passe pour éviter la demande interactive
if [ -n "$PG_PASSWORD" ]; then
    export PGPASSWORD="$PG_PASSWORD"
fi

# Demander confirmation
read -p "Attention: Cette opération va écraser la base $DB_NAME. Continuer? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Restauration annulée"
    exit 0
fi

# Restaurer selon le type de fichier
if [[ "$DUMP_FILE" == *.gz ]]; then
    echo "Restauration depuis un fichier compressé..."
    gunzip -c "$DUMP_FILE" | psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB_NAME"
else
    echo "Restauration depuis un fichier non compressé..."
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB_NAME" < "$DUMP_FILE"
fi

# Vérifier si la restauration s'est bien passée
if [ $? -eq 0 ]; then
    echo "Restauration réussie"
else
    echo "Erreur lors de la restauration"
    exit 1
fi

# Nettoyer la variable de mot de passe
unset PGPASSWORD
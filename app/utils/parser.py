# app/utils/parser.py 
# Fonctions utilitaires pour la convertir les données avec gestion des erreurs
import pandas as pd
from decimal import Decimal, InvalidOperation


def safe_decimal_conversion(value: str | float | int | None) -> Decimal | None:
    """
    Convertit une valeur en Decimal de manière sécurisée.
    
    Parameters:
        value: Valeur à convertir (str, float, int, etc.)
    
    Returns:
        Decimal ou None si conversion impossible
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    
    try:
        # Nettoyer la chaîne (enlever espaces, remplacer virgule par point)
        if isinstance(value, str):
            value = value.strip().replace(',', '.')
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        print(f"Erreur de conversion pour la valeur: {value}")
        return None

def safe_date_conversion_pandas(value: str | None) -> pd.Timestamp | None:
    """
    Convertit une chaîne de date avec pandas (plus robuste).
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    
    try:
        # Pandas peut gérer plusieurs formats automatiquement
        date_obj = pd.to_datetime(value, format="%d/%m/%Y", dayfirst=True).date()
        return date_obj
    except (ValueError, TypeError):
        print(f"Erreur de conversion de date pour la valeur: {value}")
        return None


def safe_int_conversion(value: str | float | int | None) -> int | None:
    """
    Convertit une valeur en entier de manière sécurisée.
    
    Parameters:
        value: Valeur à convertir (str, float, int, etc.)
    
    Returns:
        int ou None si conversion impossible
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        print(f"Erreur de conversion entier pour la valeur: {value}")
        return None

def safe_float_conversion(value: str | float | int | None) -> float | None:
    """
    Convertit une valeur en float de manière sécurisée.
    
    Parameters:
        value: Valeur à convertir (str, float, int, etc.)
    
    Returns:
        float ou None si conversion impossible
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    
    try:
        if isinstance(value, str):
            value = value.strip().replace(',', '.')
        return float(value)
    except (ValueError, TypeError):
        print(f"Erreur de conversion float pour la valeur: {value}")
        return None
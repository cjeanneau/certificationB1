#schemas/dpe.py
# Schemas pour les routes liées aux DPE (Diagnostic de Performance Énergétique)

# *************** PAS IMPLEMENTE ni UTILISE ***************

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class DpeRecentSearch(BaseModel):
    code_postal: str = Field(..., description="Code postal de la ville des dpe à rechercher", example="75001")
    nb_jour: int = Field(30, description="Nombre de jours pour la recherche des DPE récents", example=30)

   
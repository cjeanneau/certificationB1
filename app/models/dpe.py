# models/dpe.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from .bien_immobilier import BienImmobilier

class DPEBase(SQLModel):
    """Classe de base pour DPE"""
    id_bien: int = Field(foreign_key="bien_immobilier.id_bien")
    date_etablissement_dpe: date = Field(index=True)
    etiquette_dpe: Optional[str] = Field(default=None, max_length=5, index=True)
    etiquette_ges: Optional[str] = Field(default=None, max_length=5, index=True)
    score_ban: Optional[float] = Field(default=None, ge=0, le=1)
    score_ademe: Optional[float] = Field(default=None, ge=0)

class DPE(DPEBase, table=True):
    """Modèle DPE pour la base de données"""
    __tablename__ = "dpe"
    
    id_dpe: Optional[int] = Field(default=None, primary_key=True)
    
    # Relations
    bien_immobilier: "BienImmobilier" = Relationship(back_populates="dpes")

class DPECreate(DPEBase):
    """Schéma pour la création d'un DPE"""
    pass

class DPERead(DPEBase):
    """Schéma pour la lecture d'un DPE"""
    id_dpe: int

class DPEUpdate(SQLModel):
    """Schéma pour la mise à jour d'un DPE"""
    date_etablissement_dpe: Optional[date] = Field(default=None)
    etiquette_dpe: Optional[str] = Field(default=None, max_length=5)
    etiquette_ges: Optional[str] = Field(default=None, max_length=5)
    score_ban: Optional[float] = Field(default=None, ge=0, le=1)
    score_ademe: Optional[float] = Field(default=None, ge=0)

class DPEReadWithBien(DPERead):
    """Schéma pour la lecture d'un DPE avec son bien"""
    bien_immobilier: "BienImmobilierRead"
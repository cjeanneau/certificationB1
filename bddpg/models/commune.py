# bddpg/models/commune.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .bien_immobilier import BienImmobilier

class CommuneBase(SQLModel):
    """Classe de base pour Commune"""
    code_insee_commune: str = Field(max_length=10, index=True)
    nom_commune: str = Field(max_length=255, index=True)
    code_postal: str = Field(max_length=5, index=True)

class Commune(CommuneBase, table=True):
    """Modèle Commune simplifié avec redondance acceptable"""
    __tablename__ = "commune"
    
    id_commune: Optional[int] = Field(default=None, primary_key=True)  # PK auto-générée
    
    # Relations
    biens_immobiliers: List["BienImmobilier"] = Relationship(back_populates="commune")

# Schémas
class CommuneCreate(CommuneBase):
    """Schéma pour la création d'une commune"""
    pass

class CommuneRead(CommuneBase):
    """Schéma pour la lecture d'une commune"""
    id_commune: int

class CommuneUpdate(SQLModel):
    """Schéma pour la mise à jour d'une commune"""
    nom_commune: Optional[str] = None
    code_postal: Optional[str] = None

'''
#Removed d
#from ..crud.bien_immobilier import BienImmobilierRead


if TYPE_CHECKING:
    from .bien_immobilier import BienImmobilier

class CommuneBase(SQLModel):
    """Classe de base pour Commune avec les champs communs"""
    nom_commune: str = Field(max_length=255, index=True)
    code_postal: Optional[str] = Field(default=None, max_length=5)

class Commune(CommuneBase, table=True):
    """Modèle Commune pour la base de données"""
    __tablename__ = "commune"
    
    code_insee_commune: str = Field(primary_key=True, max_length=10)
    
    # Relations
    biens_immobiliers: List["BienImmobilier"] = Relationship(back_populates="commune")

class CommuneCreate(CommuneBase):
    """Schéma pour la création d'une commune"""
    code_insee_commune: str = Field(max_length=10)

class CommuneRead(CommuneBase):
    """Schéma pour la lecture d'une commune"""
    code_insee_commune: str

class CommuneUpdate(SQLModel):
    """Schéma pour la mise à jour d'une commune"""
    nom_commune: Optional[str] = Field(default=None, max_length=255)
    code_departement: Optional[str] = Field(default=None, max_length=5)
    code_region: Optional[str] = Field(default=None, max_length=5)

class CommuneReadWithBiens(CommuneRead):
    """Schéma pour la lecture d'une commune avec ses biens"""
    biens_immobiliers: List["BienImmobilierRead"] = []
'''
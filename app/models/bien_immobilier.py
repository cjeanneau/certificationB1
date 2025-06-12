# models/bien_immobilier.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from .commune import Commune
    from .transaction_dvf import TransactionDVF
    from .dpe import DPE

class BienImmobilierBase(SQLModel):
    """Classe de base pour BienImmobilier"""
    code_insee_commune: str = Field(foreign_key="commune.code_insee_commune", max_length=10)
    adresse_normalisee: Optional[str] = Field(default=None)
    code_postal: Optional[str] = Field(default=None, max_length=10)
    reference_cadastrale_parcelle: Optional[str] = Field(default=None, max_length=50)
    type_bien: Optional[str] = Field(default=None, max_length=50, index=True)
    surface_reelle_bati: Optional[int] = Field(default=None, ge=0)
    nombre_pieces_principales: Optional[int] = Field(default=None, ge=0)
    surface_terrain_totale: Optional[int] = Field(default=None, ge=0)
    source_info_principale: Optional[str] = Field(default=None, max_length=10)
    id_ban = Optional[str] = Field(default=None, max_length=50, index=True)
    score_ban: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class BienImmobilier(BienImmobilierBase, table=True):
    """Modèle BienImmobilier pour la base de données"""
    __tablename__ = "bien_immobilier"
    
    id_bien: Optional[int] = Field(default=None, primary_key=True)
    
    # Relations
    commune: "Commune" = Relationship(back_populates="biens_immobiliers")
    transactions_dvf: List["TransactionDVF"] = Relationship(back_populates="bien_immobilier")
    dpes: List["DPE"] = Relationship(back_populates="bien_immobilier")

class BienImmobilierCreate(BienImmobilierBase):
    """Schéma pour la création d'un bien immobilier"""
    pass

class BienImmobilierRead(BienImmobilierBase):
    """Schéma pour la lecture d'un bien immobilier"""
    id_bien: int

class BienImmobilierUpdate(SQLModel):
    """Schéma pour la mise à jour d'un bien immobilier"""
    code_insee_commune: Optional[str] = Field(default=None, max_length=10)
    adresse_normalisee: Optional[str] = Field(default=None)
    code_postal: Optional[str] = Field(default=None, max_length=10)
    reference_cadastrale_parcelle: Optional[str] = Field(default=None, max_length=50)
    type_bien: Optional[str] = Field(default=None, max_length=50)
    surface_reelle_bati: Optional[int] = Field(default=None, ge=0)
    nombre_pieces_principales: Optional[int] = Field(default=None, ge=0)
    surface_terrain_totale: Optional[int] = Field(default=None, ge=0)
    source_info_principale: Optional[str] = Field(default=None, max_length=10)
    id_ban = Optional[str] = Field(default=None, max_length=50, index=True)
    score_ban: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class BienImmobilierReadWithRelations(BienImmobilierRead):
    """Schéma pour la lecture d'un bien avec ses relations"""
    commune: "CommuneRead"
    transactions_dvf: List["TransactionDVFRead"] = []
    dpes: List["DPERead"] = []
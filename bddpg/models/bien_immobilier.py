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
    id_commune: Optional[int] = Field(default=None,foreign_key="commune.id_commune")
    adresse_normalisee: Optional[str] = Field(default=None)
    reference_cadastrale_parcelle: Optional[str] = Field(default=None, max_length=50)
    type_bien: Optional[str] = Field(default=None, max_length=50, index=True)
    surface_reelle_bati: Optional[int] = Field(default=None, ge=0)
    nombre_pieces_principales: Optional[int] = Field(default=None, ge=0)
    surface_terrain_totale: Optional[int] = Field(default=None, ge=0)
    source_info_principale: Optional[str] = Field(default=None, max_length=10)
    #score_ban: Optional[float] = Field(default=None, ge=0.0, le=1.0)

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

class BienImmobilierUpdate(BienImmobilierBase):
    """Schéma pour la mise à jour d'un bien immobilier"""
    id_bien: int = Field(default=None, primary_key=True)
    adresse_normalisee: Optional[str] = Field(default=None)
    reference_cadastrale_parcelle: Optional[str] = Field(default=None, max_length=50)
    type_bien: Optional[str] = Field(default=None, max_length=50)
    surface_reelle_bati: Optional[int] = Field(default=None, ge=0)
    nombre_pieces_principales: Optional[int] = Field(default=None, ge=0)
    surface_terrain_totale: Optional[int] = Field(default=None, ge=0)
    source_info_principale: Optional[str] = Field(default=None, max_length=10)
    score_ban: Optional[float] = Field(default=None, ge=0.0, le=1.0)


#class BienImmobilierReadWithRelations(BienImmobilierRead):
#    """Schéma pour la lecture d'un bien avec ses relations"""
#    commune: "CommuneRead"
#    transactions_dvf: List["TransactionDVFRead"] = []
#    dpes: List["DPERead"] = []
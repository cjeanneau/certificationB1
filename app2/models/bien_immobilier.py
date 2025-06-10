from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import date


class BienImmobilierBase(SQLModel):
    """Classe de base pour BienImmobilier"""
    code_insee_commune: str = Field(foreign_key="commune.code_insee_commune", max_length=5)
    adresse_normalisee: Optional[str] = Field(default=None)
    code_postal: Optional[str] = Field(default=None, max_length=5)
    coordonnee_x: Optional[float] = Field(default=None)
    coordonnee_y: Optional[float] = Field(default=None)
    geopoint: Optional[str] = Field(default=None)
    reference_cadastrale_parcelle: Optional[str] = Field(default=None, max_length=50)
    type_bien: Optional[str] = Field(default=None, max_length=50, index=True)
    surface_reelle_bati: Optional[int] = Field(default=None, ge=0)
    nombre_pieces_principales: Optional[int] = Field(default=None, ge=0)
    surface_terrain_totale: Optional[int] = Field(default=None, ge=0)
    date_premiere_apparition: Optional[date] = Field(default=None)
    source_info_principale: Optional[str] = Field(default=None, max_length=10)


class BienImmobilier(BienImmobilierBase, table=True):
    """Modèle BienImmobilier pour la base de données, hérite de notre la classe de base définit ci-dessus"""
    __tablename__ = "bien_immobilier"
    
    id_bien: Optional[int] = Field(default=None, primary_key=True) #autoincrement par defaut avec sqlmodel
    

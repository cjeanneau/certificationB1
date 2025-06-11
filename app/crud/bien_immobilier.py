# crud/bien_immobilier.py
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from ..models.bien_immobilier import BienImmobilier, BienImmobilierCreate, BienImmobilierUpdate
#from ..models.commune import Commune

class BienImmobilierCRUD:
    """Classe CRUD pour les opérations sur les biens immobiliers"""
    
    def create(self, session: Session, bien_data: BienImmobilierCreate) -> BienImmobilier:
        """Crée un nouveau bien immobilier"""
        db_bien = BienImmobilier.model_validate(bien_data.model_dump())
        session.add(db_bien)
        session.commit()
        session.refresh(db_bien)
        return db_bien
    
    def get_by_id(self, session: Session, id_bien: int) -> Optional[BienImmobilier]:
        """Récupère un bien immobilier par son ID"""
        statement = select(BienImmobilier).where(BienImmobilier.id_bien == id_bien)
        return session.exec(statement).first()
    
    def get_by_reference_cadastrale(self, session: Session, ref_cadastrale: str) -> Optional[BienImmobilier]:
        """Récupère un bien immobilier par son ID"""
        statement = select(BienImmobilier).where(BienImmobilier.reference_cadastrale_parcelle == ref_cadastrale)
        return session.exec(statement).first()
    
    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[BienImmobilier]:
        """Récupère tous les biens immobiliers avec pagination"""
        statement = select(BienImmobilier).offset(skip).limit(limit)
        return list(session.exec(statement).all())
    
    def get_by_all_fields(self, session: Session, bien_data: BienImmobilierCreate) -> Optional[BienImmobilier]:
        """
        Récupère un bien immobilier en vérifiant tous les champs pertinents
        pour éviter les doublons avant un insert
        """
        statement = select(BienImmobilier).where(
        BienImmobilier.code_insee_commune == bien_data.code_insee_commune,
        BienImmobilier.adresse_normalisee == bien_data.adresse_normalisee,
        BienImmobilier.code_postal == bien_data.code_postal,
        BienImmobilier.reference_cadastrale_parcelle == bien_data.reference_cadastrale_parcelle,
        BienImmobilier.type_bien == bien_data.type_bien,
        BienImmobilier.surface_reelle_bati == bien_data.surface_reelle_bati,
        BienImmobilier.nombre_pieces_principales == bien_data.nombre_pieces_principales,
        BienImmobilier.surface_terrain_totale == bien_data.surface_terrain_totale
        )
        return session.exec(statement).first()

    def get_by_commune(self, session: Session, code_insee: str) -> List[BienImmobilier]:
        """Récupère tous les biens d'une commune"""
        statement = select(BienImmobilier).where(
            BienImmobilier.code_insee_commune == code_insee
        )
        return list(session.exec(statement).all())
    
    def get_by_type(self, session: Session, type_bien: str) -> List[BienImmobilier]:
        """Récupère tous les biens d'un type donné"""
        statement = select(BienImmobilier).where(
            BienImmobilier.type_bien == type_bien
        )
        return list(session.exec(statement).all())
    
    def get_by_surface_range(self, session: Session, surface_min: int, surface_max: int) -> List[BienImmobilier]:
        """Récupère les biens dans une fourchette de surface"""
        statement = select(BienImmobilier).where(
            BienImmobilier.surface_reelle_bati >= surface_min,
            BienImmobilier.surface_reelle_bati <= surface_max
        )
        return list(session.exec(statement).all())
    
    def get_with_commune(self, session: Session, id_bien: int) -> Optional[BienImmobilier]:
        """Récupère un bien avec les informations de sa commune"""
        statement = select(BienImmobilier).where(
            BienImmobilier.id_bien == id_bien
        ).options(selectinload(BienImmobilier.commune))
        return session.exec(statement).first()
    
    def search_by_address(self, session: Session, adresse: str) -> List[BienImmobilier]:
        """Recherche des biens par adresse (recherche partielle)"""
        statement = select(BienImmobilier).where(
            BienImmobilier.adresse_normalisee.ilike(f"%{adresse}%")
        )
        return list(session.exec(statement).all())
    
    def update(self, session: Session, id_bien: int, bien_update: BienImmobilierUpdate) -> Optional[BienImmobilier]:
        """Met à jour un bien immobilier"""
        db_bien = self.get_by_id(session, id_bien)
        if not db_bien:
            return None
        
        bien_data = bien_update.model_dump(exclude_unset=True)
        for field, value in bien_data.items():
            setattr(db_bien, field, value)
        
        session.add(db_bien)
        session.commit()
        session.refresh(db_bien)
        return db_bien
    
    def delete(self, session: Session, id_bien: int) -> bool:
        """Supprime un bien immobilier"""
        db_bien = self.get_by_id(session, id_bien)
        if not db_bien:
            return False
        
        session.delete(db_bien)
        session.commit()
        return True
    
    def count(self, session: Session) -> int:
        """Compte le nombre total de biens immobiliers"""
        statement = select(BienImmobilier)
        return len(list(session.exec(statement).all()))
    
    def count_by_commune(self, session: Session, code_insee: str) -> int:
        """Compte le nombre de biens dans une commune"""
        statement = select(BienImmobilier).where(
            BienImmobilier.code_insee_commune == code_insee
        )
        return len(list(session.exec(statement).all()))

# Instance globale
bien_immobilier_crud = BienImmobilierCRUD()
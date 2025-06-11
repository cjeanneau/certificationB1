# crud/commune.py
from sqlmodel import Session, select
from typing import List, Optional
from ..models.commune import Commune, CommuneCreate, CommuneUpdate

class CommuneCRUD:
    """Classe CRUD pour les opérations sur les communes"""
    
    def create(self, session: Session, commune_data: CommuneCreate) -> Commune:
        """Crée une nouvelle commune"""
        db_commune = Commune.model_validate(commune_data.model_dump())
        session.add(db_commune)
        session.commit()
        session.refresh(db_commune)
        return db_commune
    
    def get_by_code_insee(self, session: Session, code_insee: str) -> Optional[Commune]:
        """Récupère une commune par son code INSEE"""
        statement = select(Commune).where(Commune.code_insee_commune == code_insee)
        return session.exec(statement).first()
    
    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[Commune]:
        """Récupère toutes les communes avec pagination"""
        statement = select(Commune).offset(skip).limit(limit).order_by(Commune.nom_commune)
        return list(session.exec(statement).all())
    
    def get_by_departement(self, session: Session, code_departement: str) -> List[Commune]:
        """Récupère toutes les communes d'un département"""
        statement = select(Commune).where(
            Commune.code_departement == code_departement
        ).order_by(Commune.nom_commune)
        return list(session.exec(statement).all())
    
    def search_by_name(self, session: Session, nom_commune: str) -> List[Commune]:
        """Recherche des communes par nom (recherche partielle)"""
        statement = select(Commune).where(
            Commune.nom_commune.ilike(f"%{nom_commune}%")
        ).order_by(Commune.nom_commune)
        return list(session.exec(statement).all())
    
    def update(self, session: Session, code_insee: str, commune_update: CommuneUpdate) -> Optional[Commune]:
        """Met à jour une commune"""
        db_commune = self.get_by_code_insee(session, code_insee)
        if not db_commune:
            return None
        
        commune_data = commune_update.model_dump(exclude_unset=True)
        for field, value in commune_data.items():
            setattr(db_commune, field, value)
        
        session.add(db_commune)
        session.commit()
        session.refresh(db_commune)
        return db_commune
    
    def delete(self, session: Session, code_insee: str) -> bool:
        """Supprime une commune"""
        db_commune = self.get_by_code_insee(session, code_insee)
        if not db_commune:
            return False
        
        session.delete(db_commune)
        session.commit()
        return True
    
    def count(self, session: Session) -> int:
        """Compte le nombre total de communes"""
        statement = select(Commune)
        return len(list(session.exec(statement).all()))

# Instance globale
commune_crud = CommuneCRUD()
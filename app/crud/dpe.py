# crud/dpe.py
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date
from ..models.dpe import DPE, DPECreate, DPEUpdate

class DPECRUD:
    """Classe CRUD pour les opérations sur les DPE"""
    
    def create(self, session: Session, dpe_data: DPECreate) -> DPE:
        """Crée un nouveau DPE"""
        db_dpe = DPE.model_validate(dpe_data.model_dump())
        session.add(db_dpe)
        session.commit()
        session.refresh(db_dpe)
        return db_dpe
    
    def get_by_id(self, session: Session, id_dpe: int) -> Optional[DPE]:
        """Récupère un DPE par son ID"""
        statement = select(DPE).where(DPE.id_dpe == id_dpe)
        return session.exec(statement).first()
    
    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[DPE]:
        """Récupère tous les DPE avec pagination"""
        statement = select(DPE).offset(skip).limit(limit).order_by(
            DPE.date_etablissement_dpe.desc()
        )
        return list(session.exec(statement).all())
    
    def get_by_bien(self, session: Session, id_bien: int) -> List[DPE]:
        """Récupère tous les DPE d'un bien"""
        statement = select(DPE).where(
            DPE.id_bien == id_bien
        ).order_by(DPE.date_etablissement_dpe.desc())
        return list(session.exec(statement).all())
    
    def get_latest_by_bien(self, session: Session, id_bien: int) -> Optional[DPE]:
        """Récupère le DPE le plus récent d'un bien"""
        statement = select(DPE).where(
            DPE.id_bien == id_bien
        ).order_by(DPE.date_etablissement_dpe.desc()).limit(1)
        return session.exec(statement).first()
    
    def get_by_etiquette_dpe(self, session: Session, etiquette: str) -> List[DPE]:
        """Récupère les DPE par étiquette DPE"""
        statement = select(DPE).where(
            DPE.etiquette_dpe == etiquette
        ).order_by(DPE.date_etablissement_dpe.desc())
        return list(session.exec(statement).all())
    
    def get_by_etiquette_ges(self, session: Session, etiquette: str) -> List[DPE]:
        """Récupère les DPE par étiquette GES"""
        statement = select(DPE).where(
            DPE.etiquette_ges == etiquette
        ).order_by(DPE.date_etablissement_dpe.desc())
        return list(session.exec(statement).all())
    
    def get_by_date_range(self, session: Session, date_debut: date, date_fin: date) -> List[DPE]:
        """Récupère les DPE dans une fourchette de dates"""
        statement = select(DPE).where(
            DPE.date_etablissement_dpe >= date_debut,
            DPE.date_etablissement_dpe <= date_fin
        ).order_by(DPE.date_etablissement_dpe.desc())
        return list(session.exec(statement).all())
    
    def get_by_score_range(self, session: Session, score_min: float, score_max: float, 
                          score_type: str = "ban") -> List[DPE]:
        """Récupère les DPE dans une fourchette de score"""
        if score_type == "ban":
            statement = select(DPE).where(
                DPE.score_ban >= score_min,
                DPE.score_ban <= score_max,
                DPE.score_ban.is_not(None)
            )
        else:  # ademe
            statement = select(DPE).where(
                DPE.score_ademe >= score_min,
                DPE.score_ademe <= score_max,
                DPE.score_ademe.is_not(None)
            )
        return list(session.exec(statement).all())
    
    def get_statistics_by_etiquette(self, session: Session) -> dict:
        """Retourne des statistiques par étiquette DPE"""
        from sqlmodel import func
        
        # Compter par étiquette DPE
        statement_dpe = select(
            DPE.etiquette_dpe,
            func.count(DPE.id_dpe).label("count")
        ).where(
            DPE.etiquette_dpe.is_not(None)
        ).group_by(DPE.etiquette_dpe)
        
        results_dpe = session.exec(statement_dpe).all()
        
        # Compter par étiquette GES
        statement_ges = select(
            DPE.etiquette_ges,
            func.count(DPE.id_dpe).label("count")
        ).where(
            DPE.etiquette_ges.is_not(None)
        ).group_by(DPE.etiquette_ges)
        
        results_ges = session.exec(statement_ges).all()
        
        return {
            "etiquettes_dpe": {row.etiquette_dpe: row.count for row in results_dpe},
            "etiquettes_ges": {row.etiquette_ges: row.count for row in results_ges}
        }
    
    def update(self, session: Session, id_dpe: int, dpe_update: DPEUpdate) -> Optional[DPE]:
        """Met à jour un DPE"""
        db_dpe = self.get_by_id(session, id_dpe)
        if not db_dpe:
            return None
        
        dpe_data = dpe_update.model_dump(exclude_unset=True)
        for field, value in dpe_data.items():
            setattr(db_dpe, field, value)
        
        session.add(db_dpe)
        session.commit()
        session.refresh(db_dpe)
        return db_dpe
    
    def delete(self, session: Session, id_dpe: int) -> bool:
        """Supprime un DPE"""
        db_dpe = self.get_by_id(session, id_dpe)
        if not db_dpe:
            return False
        
        session.delete(db_dpe)
        session.commit()
        return True
    
    def count(self, session: Session) -> int:
        """Compte le nombre total de DPE"""
        statement = select(DPE)
        return len(list(session.exec(statement).all()))
    
    def count_by_bien(self, session: Session, id_bien: int) -> int:
        """Compte le nombre de DPE pour un bien"""
        statement = select(DPE).where(DPE.id_bien == id_bien)
        return len(list(session.exec(statement).all()))

# Instance globale
dpe_crud = DPECRUD()
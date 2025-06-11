# crud/transaction_dvf.py
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date
from decimal import Decimal
from ..models.transaction_dvf import TransactionDVF, TransactionDVFCreate, TransactionDVFUpdate

class TransactionDVFCRUD:
    """Classe CRUD pour les opérations sur les transactions DVF"""
    
    def create(self, session: Session, transaction_data: TransactionDVFCreate) -> TransactionDVF:
        """Crée une nouvelle transaction DVF"""
        db_transaction = TransactionDVF.model_validate(transaction_data.model_dump())
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
        return db_transaction
    
    def get_by_id(self, session: Session, id_transaction: int) -> Optional[TransactionDVF]:
        """Récupère une transaction DVF par son ID"""
        statement = select(TransactionDVF).where(TransactionDVF.id_transaction == id_transaction)
        return session.exec(statement).first()
    
    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[TransactionDVF]:
        """Récupère toutes les transactions DVF avec pagination"""
        statement = select(TransactionDVF).offset(skip).limit(limit).order_by(
            TransactionDVF.date_mutation.desc()
        )
        return list(session.exec(statement).all())
    
    def get_by_all_fields(self, session: Session, transaction_data: TransactionDVFCreate) -> Optional[TransactionDVF]:
        statement = select(TransactionDVF).where(
        TransactionDVF.id_bien == transaction_data.id_bien,
        TransactionDVF.date_mutation == transaction_data.date_mutation,
        TransactionDVF.nature_mutation == transaction_data.nature_mutation,
        TransactionDVF.valeur_fonciere == transaction_data.valeur_fonciere
        )
        return session.exec(statement).first()
    
    def get_by_bien(self, session: Session, id_bien: int) -> List[TransactionDVF]:
        """Récupère toutes les transactions d'un bien"""
        statement = select(TransactionDVF).where(
            TransactionDVF.id_bien == id_bien
        ).order_by(TransactionDVF.date_mutation.desc())
        return list(session.exec(statement).all())
    
    def get_by_date_range(self, session: Session, date_debut: date, date_fin: date) -> List[TransactionDVF]:
        """Récupère les transactions dans une fourchette de dates"""
        statement = select(TransactionDVF).where(
            TransactionDVF.date_mutation >= date_debut,
            TransactionDVF.date_mutation <= date_fin
        ).order_by(TransactionDVF.date_mutation.desc())
        return list(session.exec(statement).all())
    
    def get_by_nature_mutation(self, session: Session, nature_mutation: str) -> List[TransactionDVF]:
        """Récupère les transactions par nature de mutation"""
        statement = select(TransactionDVF).where(
            TransactionDVF.nature_mutation == nature_mutation
        ).order_by(TransactionDVF.date_mutation.desc())
        return list(session.exec(statement).all())
    
    def get_by_price_range(self, session: Session, prix_min: Decimal, prix_max: Decimal) -> List[TransactionDVF]:
        """Récupère les transactions dans une fourchette de prix"""
        statement = select(TransactionDVF).where(
            TransactionDVF.valeur_fonciere >= prix_min,
            TransactionDVF.valeur_fonciere <= prix_max
        ).order_by(TransactionDVF.valeur_fonciere.desc())
        return list(session.exec(statement).all())
    
    def get_recent_transactions(self, session: Session, days: int = 30, limit: int = 100) -> List[TransactionDVF]:
        """Récupère les transactions récentes"""
        from datetime import datetime, timedelta
        date_limite = datetime.now().date() - timedelta(days=days)
        
        statement = select(TransactionDVF).where(
            TransactionDVF.date_mutation >= date_limite
        ).order_by(TransactionDVF.date_mutation.desc()).limit(limit)
        return list(session.exec(statement).all())
    
    def get_average_price_by_period(self, session: Session, date_debut: date, date_fin: date) -> Optional[Decimal]:
        """Calcule le prix moyen sur une période"""
        from sqlmodel import func
        statement = select(func.avg(TransactionDVF.valeur_fonciere)).where(
            TransactionDVF.date_mutation >= date_debut,
            TransactionDVF.date_mutation <= date_fin,
            TransactionDVF.valeur_fonciere.is_not(None)
        )
        result = session.exec(statement).first()
        return Decimal(str(result)) if result else None
    
    def update(self, session: Session, id_transaction: int, transaction_update: TransactionDVFUpdate) -> Optional[TransactionDVF]:
        """Met à jour une transaction DVF"""
        db_transaction = self.get_by_id(session, id_transaction)
        if not db_transaction:
            return None
        
        transaction_data = transaction_update.model_dump(exclude_unset=True)
        for field, value in transaction_data.items():
            setattr(db_transaction, field, value)
        
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
        return db_transaction
    
    def delete(self, session: Session, id_transaction: int) -> bool:
        """Supprime une transaction DVF"""
        db_transaction = self.get_by_id(session, id_transaction)
        if not db_transaction:
            return False
        
        session.delete(db_transaction)
        session.commit()
        return True
    
    def count(self, session: Session) -> int:
        """Compte le nombre total de transactions"""
        statement = select(TransactionDVF)
        return len(list(session.exec(statement).all()))
    
    def count_by_bien(self, session: Session, id_bien: int) -> int:
        """Compte le nombre de transactions pour un bien"""
        statement = select(TransactionDVF).where(TransactionDVF.id_bien == id_bien)
        return len(list(session.exec(statement).all()))

# Instance globale
transaction_dvf_crud = TransactionDVFCRUD()
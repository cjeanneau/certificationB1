# models/transaction_dvf.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date



if TYPE_CHECKING:
    from .bien_immobilier import BienImmobilier

class TransactionDVFBase(SQLModel):
    """Classe de base pour TransactionDVF"""
    id_bien: int = Field(foreign_key="bien_immobilier.id_bien")
    date_mutation: date = Field(index=True)
    nature_mutation: Optional[str] = Field(default=None, max_length=50)
    valeur_fonciere: int = Field(gt=0)

class TransactionDVF(TransactionDVFBase, table=True):
    """Modèle TransactionDVF pour la base de données"""
    __tablename__ = "transaction_dvf"
    
    id_transaction: Optional[int] = Field(default=None, primary_key=True)
    
    # Relations
    bien_immobilier: "BienImmobilier" = Relationship(back_populates="transactions_dvf")

class TransactionDVFCreate(TransactionDVFBase):
    """Schéma pour la création d'une transaction DVF"""
    pass

class TransactionDVFRead(TransactionDVFBase):
    """Schéma pour la lecture d'une transaction DVF"""
    id_transaction: int

class TransactionDVFUpdate(SQLModel):
    """Schéma pour la mise à jour d'une transaction DVF"""
    date_mutation: Optional[date] = Field(default=None)
    nature_mutation: Optional[str] = Field(default=None, max_length=50)
    valeur_fonciere: int = Field(gt=0)

class TransactionDVFReadWithBien(TransactionDVFRead):
    """Schéma pour la lecture d'une transaction avec son bien"""
    #bien_immobilier: "BienImmobilierRead"
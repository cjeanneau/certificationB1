# models/__init__.py
from .commune import (
    Commune, CommuneBase, CommuneCreate, CommuneRead, 
    CommuneUpdate, #CommuneReadWithBiens
)
from .bien_immobilier import (
    BienImmobilier, BienImmobilierBase, BienImmobilierCreate, 
    BienImmobilierRead, BienImmobilierUpdate, #BienImmobilierReadWithRelations
)
from .transaction_dvf import (
    TransactionDVF, TransactionDVFBase, TransactionDVFCreate,
    TransactionDVFRead, TransactionDVFUpdate, TransactionDVFReadWithBien
)
from .dpe import (
    DPE, DPEBase, DPECreate, DPERead, DPEUpdate, DPEReadWithBien
)

from .user import User, UserLogin, UserCreate, UserResponse, Token

__all__ = [
    # Commune
    "Commune", "CommuneBase", "CommuneCreate", "CommuneRead", 
    "CommuneUpdate", #"CommuneReadWithBiens",
    # Bien Immobilier
    "BienImmobilier", "BienImmobilierBase", "BienImmobilierCreate", 
    "BienImmobilierRead", "BienImmobilierUpdate", #"BienImmobilierReadWithRelations",
    # Transaction DVF
    "TransactionDVF", "TransactionDVFBase", "TransactionDVFCreate",
    "TransactionDVFRead", "TransactionDVFUpdate", "TransactionDVFReadWithBien",
    # DPE
    "DPE", "DPEBase", "DPECreate", "DPERead", "DPEUpdate", "DPEReadWithBien",
    # User
    "User", "UserLogin", "UserCreate", "UserResponse", "Token"
]
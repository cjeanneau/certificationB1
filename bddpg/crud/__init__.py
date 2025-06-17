# crud/__init__.py

from .commune import CommuneCRUD, commune_crud
from .bien_immobilier import BienImmobilierCRUD, bien_immobilier_crud
from .transaction_dvf import TransactionDVFCRUD, transaction_dvf_crud
from .dpe import DPECRUD, dpe_crud

__all__ = [
    # Classes CRUD
    "CommuneCRUD",
    "BienImmobilierCRUD", 
    "TransactionDVFCRUD",
    "DPECRUD",
    # Instances globales
    "commune_crud",
    "bien_immobilier_crud",
    "transaction_dvf_crud",
    "dpe_crud",
]


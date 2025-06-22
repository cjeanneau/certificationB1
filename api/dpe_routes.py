from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from bddpg import User, UserLogin, UserCreate, get_session_sync
from schemas import success_response
from auth import get_current_active_user, require_admin, require_user_or_admin
from services import DPEServices


router = APIRouter(prefix="/api/v1/dpe", tags=["Diagnostic DPE"])

@router.get("/recent")
def get_recent_dpes(cp: str, nb_jour: int = 30):
    
    """Récupérer tous les dpe depuis une date """
    try:
        dpes = DPEService.retrieve_recent_dpe_by_cp(cp, nb_jour)
        if dpes is None:
            raise HTTPException(status_code=404, detail="Aucun DPE trouvé pour ce code postal")
        return dpes
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des utilisateurs")

@router.get("/{num_dpe}")
def get_dpe_by_num(num_dpe: str):
    """Récupérer un DPE spécifique par son numéro de DPE"""
    try:
        dpe = DPEService.retrieve_dpe_by_num_dpe(num_dpe)
        if not dpe:
            raise HTTPException(status_code=404, detail="DPE non trouvé")
        return dpe
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du DPE")
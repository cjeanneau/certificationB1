from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlmodel import Session
from bddpg import User, UserLogin, UserCreate, get_session_sync
from schemas import success_response
from auth import get_current_active_user, require_admin, require_user_or_admin
from services import EvalServices


router = APIRouter(prefix="/api/v1/dpe", tags=["Evaluation immobilière"])


@router.get("/eval/advanced")
def eval_filtered(
    cp: Optional[str] = None,
    code_insee: Optional[str] = None,
    type_bien: Optional[str] = None,
    surface_min: Optional[float] = None,
    surface_max: Optional[float] = None,
    etiquette_dpe: Optional[int] = None
):
    """Evaluation avancée (accès user et admin)"""
    try:
        if cp is None and code_insee is None:
            raise HTTPException(status_code=400, detail="Code postal ou code INSEE requis")
        if cp is not None and len(cp) != 5:
            raise HTTPException(status_code=400, detail="Le code postal doit comporter 5 chiffres")
        if code_insee is not None and len(code_insee) != 5:
            raise HTTPException(status_code=400, detail="Le code INSEE doit comporter 5 chiffres")
        
        if cp and not code_insee:
            return EvalServices.eval_multifields_cp(
                cp=cp,
                type_bien=type_bien,
                surface_min=surface_min,
                surface_max=surface_max,
                etiquette_dpe=etiquette_dpe
            )
        """
        elif code_insee and not cp:
            return EvalServices.eval_multifields_code_insee(
                code_insee=code_insee,
                type_bien=type_bien,
                surface_min=surface_min,
                surface_max=surface_max,
                etiquette_dpe=etiquette_dpe
            )
        """
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de l'évaluation des biens immobiliers")
    

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlmodel import Session
from bddpg import User, UserLogin, UserCreate, get_session_sync
from schemas import success_response
from auth import get_current_active_user, require_admin, require_user_or_admin
from services import EvalServices


router = APIRouter(prefix="/api/v1/eval", tags=["Evaluation immobilière"])


@router.get("/by_cp")
def eval_filtered(
    cp: Optional[str] = None,
    type_bien: Optional[str] = None,
    surface_min: Optional[float] = None,
    surface_max: Optional[float] = None,
    etiquette_dpe: Optional[str] = None
):
    """Evaluation avancée (accès user et admin)"""
    try:
       
        if cp is not None and len(cp) != 5:
            raise HTTPException(status_code=400, detail="Le code postal doit comporter 5 chiffres")
            
        return EvalServices.eval_by_cp(
            cp=cp,
            type_bien=type_bien,
            surface_min=surface_min,
            surface_max=surface_max,
            etiquette_dpe=etiquette_dpe
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'évaluation des biens immobiliers")
    

@router.get("/by_insee")
def eval_filtered(
    code_insee: Optional[str] = None,
    type_bien: Optional[str] = None,
    surface_min: Optional[float] = None,
    surface_max: Optional[float] = None,
    etiquette_dpe: Optional[str] = None
):
    """Evaluation avancée (accès user et admin)"""
    try:

        if code_insee is not None and len(code_insee) != 5:
            raise HTTPException(status_code=400, detail="Le code postal doit comporter 5 chiffres")
            
        return EvalServices.eval_by_insee(
                code_insee=code_insee,
                type_bien=type_bien,
                surface_min=surface_min,
                surface_max=surface_max,
                etiquette_dpe=etiquette_dpe
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'évaluation des biens immobiliers")
    


@router.get("/couronne1")
def display_couronne1(code_insee: str):

    try:
        return EvalServices.display_city_first_ring(code_insee=code_insee)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'évaluation des biens immobiliers")
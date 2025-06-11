# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from .database import get_session
from config import API_TITLE, API_VERSION, API_DESCRIPTION

# Import des modèles
from .models import (
    # Commune
    CommuneCreate, CommuneRead, CommuneUpdate, CommuneReadWithBiens,
    # Bien Immobilier
    BienImmobilierCreate, BienImmobilierRead, BienImmobilierUpdate, BienImmobilierReadWithRelations,
    # Transaction DVF
    TransactionDVFCreate, TransactionDVFRead, TransactionDVFUpdate, TransactionDVFReadWithBien,
    # DPE
    DPECreate, DPERead, DPEUpdate, DPEReadWithBien
)

# Import des CRUD
from .crud import (
    commune_crud, bien_immobilier_crud, transaction_dvf_crud, dpe_crud
)

# Import des services
from .services import statistics_service

# Création de l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# === ROUTES COMMUNES ===

@app.post("/communes/", response_model=CommuneRead)
def create_commune(
    commune: CommuneCreate,
    session: Session = Depends(get_session)
):
    """Crée une nouvelle commune"""
    return commune_crud.create(session, commune)

@app.get("/communes/", response_model=List[CommuneRead])
def read_communes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Récupère la liste des communes"""
    return commune_crud.get_all(session, skip=skip, limit=limit)

@app.get("/communes/{code_insee}", response_model=CommuneRead)
def read_commune(
    code_insee: str,
    session: Session = Depends(get_session)
):
    """Récupère une commune par son code INSEE"""
    commune = commune_crud.get_by_code_insee(session, code_insee)
    if not commune:
        raise HTTPException(status_code=404, detail="Commune non trouvée")
    return commune

@app.get("/communes/{code_insee}/with-biens", response_model=CommuneReadWithBiens)
def read_commune_with_biens(
    code_insee: str,
    session: Session = Depends(get_session)
):
    """Récupère une commune avec ses biens"""
    commune = commune_crud.get_by_code_insee(session, code_insee)
    
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from bddpg import get_session_sync
from .auth_service import AuthService
#from exceptions import ValidationError

# Sécurité HTTP Bearer (pour récupérer le token des headers)
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session_sync)
):
    """Dépendance pour récupérer l'utilisateur actuel"""
    try:
        token = credentials.credentials
        user = AuthService.get_current_user(db, token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_active_user(current_user = Depends(get_current_user)):
    """Dépendance pour vérifier que l'utilisateur est actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )
    return current_user

def require_admin(current_user = Depends(get_current_active_user)):
    """Dépendance pour vérifier que l'utilisateur est admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user

def require_user_or_admin(current_user = Depends(get_current_active_user)):
    """Dépendance pour vérifier que l'utilisateur est connecté (user ou admin)"""
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentification requise"
        )
    return current_user
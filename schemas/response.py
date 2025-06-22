from pydantic import BaseModel
from typing import Any, Optional, Dict, List

class StandardResponse(BaseModel):
    """Réponse API standardisée"""
    success: bool
    message: str
    data: Optional[List[Any]] = None
    count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

def success_response(data: Any = None, message: str = "Opération réussie", count: int = None, metadata: Dict = None):
    """Créer une réponse de succès"""
    if data is not None and not isinstance(data, list):
        data = [data]
    
    return StandardResponse(
        success=True,
        message=message,
        data=data,
        count=count or (len(data) if data else 0),
        metadata=metadata or {}
    ).model_dump()

def error_response(message: str, data: Any = None):
    """Créer une réponse d'erreur"""
    return StandardResponse(
        success=False,
        message=message,
        data=data,
        count=0
    ).model_dump()
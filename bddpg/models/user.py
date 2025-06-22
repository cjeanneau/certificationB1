from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255, unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    role: str = Field(default="user")  # "user" ou "admin"
    
class User(UserBase, table=True):
    """Modèle utilisateur pour la base de données"""
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)

    # definition de l'ffichage de l'objet User
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
class UserLogin(SQLModel):
    """Données de connexion"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=4, description="Mot de passe")

class UserCreate(SQLModel):
    """Création d'utilisateur"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=4, description="Mot de passe")
    role: str = Field("user", description="Rôle: user ou admin")


class UserResponse(SQLModel):
    """Réponse utilisateur (sans mot de passe)"""
    id: int
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(SQLModel):
    """Token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(SQLModel):
    """Données contenues dans le token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None

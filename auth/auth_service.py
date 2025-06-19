from sqlalchemy.orm import Session
from bddpg import User, UserCreate, UserLogin, UserResponse, Token
from schemas import success_response
#from exceptions import ValidationError, PassengerNotFound
from .jwt_handler import JWTHandler

class AuthService:
    """Service d'authentification simplifié"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate):
        """Créer un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            #raise ValidationError("Un utilisateur avec cet email existe déjà")
            raise ValueError("Un utilisateur avec cet email existe déjà")
        # Valider le rôle
        if user_data.role not in ["user", "admin"]:
            #raise ValidationError("Le rôle doit être 'user' ou 'admin'")
            raise ValueError("Le rôle doit être 'user' ou 'admin'")
        
        # Hacher le mot de passe
        password_hash = JWTHandler.hash_password(user_data.password)
        
        # Créer l'utilisateur
        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
            role=user_data.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return success_response(
            data=UserResponse.from_orm(db_user),
            message="Utilisateur créé avec succès"
        )
    
    @staticmethod
    def login(db: Session, login_data: UserLogin):
        """Connecter un utilisateur"""
        # Chercher l'utilisateur par email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            #raise ValidationError("Email ou mot de passe incorrect")
            raise ValueError("Email ou mot de passe incorrect")
        
        # Vérifier le mot de passe
        if not JWTHandler.verify_password(login_data.password, user.password_hash):
            #raise ValidationError("Email ou mot de passe incorrect")
            raise ValueError("Email ou mot de passe incorrect")
        
        # Vérifier que l'utilisateur est actif
        if not user.is_active:
            #raise ValidationError("Compte désactivé")
            raise ValueError("Compte désactivé")
        
        # Créer le token JWT
        access_token = JWTHandler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )
        
        # Retourner le token et les infos utilisateur
        token_response = Token(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
        
        return success_response(
            data=token_response,
            message="Connexion réussie"
        )
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Récupérer l'utilisateur actuel depuis le token"""
        # Décoder le token
        payload = JWTHandler.decode_token(token)
        if not payload:
            #raise ValidationError("Token invalide ou expiré")
            raise ValueError("Token invalide ou expiré")
            
        
        # Récupérer l'utilisateur
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            #raise ValidationError("Utilisateur non trouvé")
            raise ValueError("Utilisateur non trouvé")
        
        if not user.is_active:
            #raise ValidationError("Compte désactivé")
            raise ValueError("Compte désactivé")
        
        return user
    
    @staticmethod
    def get_all_users(db: Session):
        """Récupérer tous les utilisateurs (admin seulement)"""
        users = db.query(User).all()
        user_responses = [UserResponse.from_orm(user) for user in users]
        
        return success_response(
            data=user_responses,
            message=f"{len(users)} utilisateurs trouvés"
        )
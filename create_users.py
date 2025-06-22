import sys
import os

from bddpg import create_db_and_tables, get_session_sync, User
from auth import JWTHandler

def create_default_users():
    """Créer des utilisateurs par défaut pour les tests"""
    print("👥 Création des utilisateurs par défaut")
    print("=" * 40)
    
    # Créer les tables si nécessaire
    create_db_and_tables(drop=False)
    
    # Utilisateurs par défaut
    default_users = [
        {
            "email": "admin@immodb.com",
            "password": "admin",
            "role": "admin"
        },
        {
            "email": "cyril@immodb.com", 
            "password": "cyril",
            "role": "user"
        },
        {
            "email": "user@immodb.com",
            "password": "user",
            "role": "user"
        }
    ]
    
    db = get_session_sync()
    try:
        for user_data in default_users:
            # Vérifier si l'utilisateur existe déjà
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"Oopsy... {user_data['email']} existe déjà")
                continue
            
            # Créer l'utilisateur
            password_hash = JWTHandler.hash_password(user_data["password"])
            
            user = User(
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"]
            )
            
            db.add(user)
            print(f"Créé: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        print(f"\n Utilisateurs créés avec succès !")
        
        print("\n Comptes de test disponibles:")
        print(" Admin: admin@immodb.com / admin")
        print(" User:  user@immodb.com / user")
        print(" User:  jack@immodb.com / rose")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_default_users()
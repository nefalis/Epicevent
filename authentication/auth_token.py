import jwt
import os
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from model.user_model import User
from config import SECRET_KEY_TOKEN, ALGORITHM, TOKEN_FILE



def create_jwt_token(user_id: int, secret_key: str, algorithm: str, expires_delta: timedelta) -> str:
    """
    Crée un jeton JWT pour l'utilisateur.
    """
    expiration = datetime.now(tz=timezone.utc) + expires_delta
    to_encode = {"exp": expiration, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def save_token(token: str):
    with open(TOKEN_FILE, "w") as file:
        file.write(token)


def load_token() -> Optional[str]:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            token = file.read().strip()
            if isinstance(token, str):
                return token
            else:
                print("debug load token l60 Le jeton n'est pas une chaîne valide")
    return None


def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def verify_jwt_token(token: str, secret_key: str, algorithm: str):
    """
    Vérifie et décode un jeton JWT.
    """
    try:
        # Décoder le token
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload["sub"]
    
    except jwt.ExpiredSignatureError:
        raise PermissionError("Le jeton a expiré.")
    except jwt.InvalidTokenError:
        raise PermissionError("Erreur lors de la vérification du jeton.")
    

def get_user_from_token(token: str, db: Session):
    """
    Récupère l'utilisateur à partir du jeton JWT.
    """
    try:
        user_id = verify_jwt_token(token, SECRET_KEY_TOKEN, ALGORITHM)
        
        if not user_id:
            raise PermissionError("ID utilisateur non trouvé dans le jeton.")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise PermissionError("Utilisateur introuvable.")
        return user
    except PermissionError as e:
        raise e
    except Exception as e:
        raise PermissionError(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")


def check_token_expiry(token: str) -> bool:
    """
    Vérifie si le jeton est expiré.
    Retourne True si le jeton est encore valide, False s'il est expiré.
    """
    try:
        verify_jwt_token(token, SECRET_KEY_TOKEN, ALGORITHM)
        return True
    except PermissionError:
        return False

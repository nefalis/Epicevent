import os
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from authentication.auth import logout
from authentication.auth_controller import authenticate_user
from model.user_model import User
from authentication.auth_token import create_jwt_token, save_token
from config import SECRET_KEY_TOKEN, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def login_user(db: Session, employee_number: str, password: str) -> Optional[str]:
    """
    Service pour authentifier et connecter un utilisateur.
    """
    user = authenticate_user(db, employee_number, password)
    if user:
        token = create_jwt_token(user.id, SECRET_KEY_TOKEN, ALGORITHM, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        save_token(token)
        return token
    return None


def logout_user():
    """
    Service pour gérer la déconnexion. Supprime le jeton local.
    """
    logout()


def get_current_user_role(user_id: int, db: Session, token: str) -> str:
    """
    Obtient le rôle de l'utilisateur actuellement connecté en utilisant son ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if user and user.department:
        return user.department.name

    return None


def get_current_user_department(user_id: int, db: Session) -> str:
    """
    Obtient le département de l'utilisateur actuellement connecté en utilisant son ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    return user.department.name if user else None


def can_perform_action(user_department: str, action: str) -> bool:
    """
    Vérifie si le rôle de l'utilisateur autorise l'action demandée.
    """
    permissions = {
        "manager": {
            "get_all_clients": True,
            "create_client": True,
            "update_client": True,
            "delete_client": True,
            "get_all_contracts": True,
            "create_contract": True,
            "update_contract": True,
            "delete_contract": True,
            "get_all_users": True,
            "create_user": True,
            "update_user": True,
            "delete_user": True,
            "get_all_events": True,
            "create_event": True,
            "update_event": True,
            "delete_event": True,
        },
        "gestion": {
            "get_all_clients": True,
            "create_client": False,
            "update_client": False,
            "delete_client": False,
            "get_all_contracts": True,
            "create_contract": True,
            "update_contract": True,
            "delete_contract": True,
            "get_all_users": True,
            "create_user": True,
            "update_user": True,
            "delete_user": True,
            "get_all_events": True,
            "create_event": False,
            "update_event": True,
            "delete_event": True,
        },
        "commercial": {
            "get_all_clients": True,
            "create_client": True,
            "update_client": True,
            "delete_client": True,
            "get_all_contracts": True,
            "create_contract": False,
            "update_contract": True,
            "delete_contract": False,
            "get_all_users": True,
            "create_user": False,
            "update_user": False,
            "delete_user": False,
            "get_all_events": True,
            "create_event": True,
            "update_event": False,
            "delete_event": False,
        },
        "support": {
            "get_all_clients": True,
            "create_client": False,
            "update_client": False,
            "delete_client": False,
            "get_all_contracts": True,
            "create_contract": False,
            "update_contract": False,
            "delete_contract": False,
            "get_all_users": True,
            "create_user": False,
            "update_user": False,
            "delete_user": False,
            "get_all_events": True,
            "create_event": False,
            "update_event": True,
            "delete_event": False,
        },
        "default": {
            "get_all_clients": True,
            "get_all_contracts": True,
            "get_all_events": True,
            "get_all_users": False,
        }
    }

    result = permissions.get(user_department, permissions["default"]).get(action, False)
    return result


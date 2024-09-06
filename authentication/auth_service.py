from sqlalchemy.orm import Session
from auth import login, logout
from authentication.auth_controller import authenticate_user

def login_user(db: Session, employee_number: str, password: str):
    """
    Service pour authentifier et connecter un utilisateur.
    """
    user = authenticate_user(db, employee_number, password)
    if user:
        login(user)
    return user

def logout_user():
    """
    Service pour gérer la déconnexion.
    """
    logout()
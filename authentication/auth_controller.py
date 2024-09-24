from sqlalchemy.orm import Session
from model.user_model import User


def authenticate_user(db: Session, employee_number: str, password: str):
    """
    Authentifie un utilisateur en vérifiant
    le numéro d'employé et le mot de passe.
    """
    user = db.query(User).filter(
        User.employee_number == employee_number
        ).first()
    if user and user.check_password(password):
        return user
    return None

from sqlalchemy.orm import Session
import sentry_sdk
from rich.console import Console
from model.user_model import User, Department
from datetime import datetime
from authentication.auth_token import get_user_from_token
from authentication.auth_utils import handle_errors, requires_permission


console = Console()


@handle_errors
def get_all_users(db: Session, token: str):
    """
    Fonction pour récupérer et afficher tous les
    utilisateurs de la base de données
    """
    get_user_from_token(token, db)
    users = (
        db.query(User)
        .join(Department)
        .filter(Department.name != "manager")
        .all()
    )
    return users


@handle_errors
@requires_permission("create_user")
def create_user(
    db: Session, user_id: int, token: str, employee_number: str,
    complete_name: str, email: str, password: str, department_name: str
):
    """
    Fonction pour créer un nouvel utilisateur dans la base de données
    """
    department = (
        db.query(Department)
        .filter(Department.name == department_name)
        .first()
    )
    if not department:
        raise ValueError("Département non trouvé")

    new_user = User(
        employee_number=employee_number,
        complete_name=complete_name,
        email=email,
        password=password,
        department_id=department.id,
        creation_date=datetime.now()
    )
    new_user.set_password(password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    sentry_sdk.capture_message(f"Utilisateur créé: {new_user.complete_name}, ID: {new_user.id}")

    return new_user


@handle_errors
@requires_permission("update_user")
def update_user(db: Session, user_id: int, token: str, selected_user_id: int, **kwargs):
    """
    Fonction pour mettre à jour un utilisateur existant.
    """
    user_to_update = db.query(User).filter(User.id == selected_user_id).first()
    if not user_to_update:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(user_to_update, key, value)

    db.commit()
    db.refresh(user_to_update)

    sentry_sdk.capture_message(f"Utilisateur modifié: {user_to_update.complete_name}, ID: {user_to_update.id}")

    return user_to_update


@handle_errors
@requires_permission("delete_user")
def delete_user(db: Session, user_id: int, token: str, selected_user_id: int):
    """
    Fonction pour supprimer un utilisateur
    """
    user_to_delete = db.query(User).filter(User.id == selected_user_id).first()
    if not user_to_delete:
        return None

    db.delete(user_to_delete)
    db.commit()
    return user_to_delete


def get_users_by_role(db: Session, role: str):
    """
    Récupère tous les utilisateurs ayant un rôle spécifique.
    """
    return (
        db.query(User)
        .join(Department)
        .filter(Department.name == role)
        .all()
    )


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Récupère un événement spécifique par son ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_commercials(db: Session):
    """
    Fonction pour récupérer tous les utilisateurs ayant le rôle de commercial.
    """
    return (
        db.query(User)
        .join(Department)
        .filter(Department.name == "commercial")
        .all()
    )

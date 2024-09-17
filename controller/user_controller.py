from sqlalchemy.orm import Session
from model.user_model import User, Department
from datetime import datetime


def get_all_users(db: Session):
    """
    Fonction pour récupérer et afficher tous les utilisateurs de la base de données
    """
    users = db.query(User).join(Department).filter(Department.name != "admin").all()
    return users


def create_user(db: Session, employee_number: str, complete_name: str, email: str, password: str, department_name: str):
    """
    Fonction pour créer un nouvel utilisateur dans la base de données
    """
    department = db.query(Department).filter(Department.name == department_name).first()
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

    # Ajoute utilisateur à la session de la base de données
    db.add(new_user)
    # Commit les changements dans la base de données
    db.commit()
    # Actualise la session pour obtenir l'ID généré
    db.refresh(new_user)

    return new_user


def update_user(db: Session, user_id: int, complete_name: str = None, email: str = None, password: str = None, department_name: str = None):
    """
    Fonction pour mettre à jour un utilisateur existant
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    if complete_name:
        user.complete_name = complete_name
    if email:
        user.email = email
    if password:
        user.set_password(password)
    if department_name:
        department = db.query(Department).filter(Department.name == department_name).first()
        if not department:
            raise ValueError("Département non trouvé")
        user.department_id = department.id

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    """
    Fonction pour supprimer un utilisateur
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    db.delete(user)
    db.commit()
    return user


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
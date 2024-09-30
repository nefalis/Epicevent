from sqlalchemy.orm import Session
from config import SessionLocal, Base
from model.user_model import User, Department
from model.client_model import Client
from model.contract_model import Contract
from model.event_model import Event
import bcrypt
from datetime import datetime


def init_db(db: Session):
    """Initialiser la base de données avec des données de base."""

    departments = [
        (1, "commercial"),
        (2, "support"),
        (3, "gestion"),
        (4, "manager"),
    ]

    for department_id, department_name in departments:
        if not db.query(Department).filter_by(id=department_id).first():
            new_department = Department(id=department_id, name=department_name)
            db.add(new_department)
            print(f"Départment '{department_name}' créé avec succès.")

    db.commit()

    if not db.query(User).filter_by(email='gestion@epicmail.com').first():
        # Créer un utilisateur admin avec un mot de passe hashé
        hashed_password = bcrypt.hashpw("Mana4522pm".encode('utf-8'), bcrypt.gensalt())
        admin = User(
            complete_name="John Doe",
            email="gestion@epicmail.com",
            password=hashed_password.decode('utf-8'),
            employee_number="ma4444",
            department_id=4,
            creation_date=datetime.now()
        )
        db.add(admin)
        db.commit()
        print("Utilisateur admin créé avec succès.")
    else:
        print("L'utilisateur admin existe déjà.")

    print("Données initiales insérées avec succès.")


def main():
    """Fonction principale pour configurer la base de données."""

    db = SessionLocal()
    Base.metadata.create_all(bind=db.bind)

    init_db(db)

    db.close()


if __name__ == "__main__":
    main()

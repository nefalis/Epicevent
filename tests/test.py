from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from model.user_model import User
from model.client_model import Client
from model.contract_model import Contract
from model.event_model import Event
from config import SessionLocal
from config import Base, engine

# Créer toutes les tables dans la base de données
Base.metadata.create_all(bind=engine)

def populate_users():
    # creation nouvelle session
    db: Session = SessionLocal()

    try:
        user1 = User(employee_number='co2214', complete_name='Fred Epic', email='fred@epivmail.com', password='Fr84632d', role='commercial', creation_date='2024-08-24')
        user2 = User(employee_number='su4474', complete_name='Eric Event', email='eric@epivmail.com', password='Er7435hd', role='support', creation_date='2024-08-25')

        # ajout user a la session
        db.add_all([user1, user2])

        # commit pour persiter dans la base de donnée
        db.commit()
        print("user dans la base !")

    except Exception as e:
        # Annuler la transaction en cas d'erreur
        db.rollback()
        print(f"il y a une erreur: {e}")

    finally:
        # Fermer la session
        db.close()

if __name__ == "__main__":
    # Appel de la fonction pour remplir la table des utilisateurs
    populate_users()
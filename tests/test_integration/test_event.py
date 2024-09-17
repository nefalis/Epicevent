from sqlalchemy.orm import Session
from config import Base, engine, SessionLocal
from controller.contract_controller import create_contract
from model import *
from datetime import datetime

# Configuration de la base de données de test
Base.metadata.create_all(bind=engine)

def test_create_contract():
    # Configuration de la session de test
    db: Session = SessionLocal()
    user_id = 10

    # Données de test pour le contrat
    contract_data = {
        "client_id": 2,
        "commercial_contact_id": 1,
        "total_price": 5000,
        "remaining_price": 2000,
        "statut": "signé",
    }

    # Appel de la fonction à tester
    contract = create_contract(db, user_id, **contract_data)

    # Vérifications
    assert contract is not None
    assert contract.client_id == 2
    assert contract.total_price == 5000
    assert contract.statut == "signé"

    # Nettoyage
    db.close()
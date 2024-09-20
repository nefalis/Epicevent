import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.contract_model import Contract, Client
from model.user_model import User, Department
from controller.contract_controller import create_contract
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

# Utiliser une base en mémoire pour les tests
DATABASE_URL = "sqlite:///:memory:"

Base = declarative_base()

# Configuration de la base de données pour les tests
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Créer toutes les tables nécessaires
    Base.metadata.create_all(engine)

    # Ajouter des données de test
    yield session

    # Supprimer toutes les tables après les tests
    Base.metadata.drop_all(engine)
    session.close()

# Mock de la fonction d'authentification pour obtenir le rôle de l'utilisateur
@pytest.fixture
def mock_user_role(mocker):
    mocker.patch('authentication.auth_service.get_current_user_role', return_value="admin")
    mocker.patch('authentication.auth_service.can_perform_action', return_value=True)

# Test d'intégration pour créer un contrat
def test_create_contract(db_session, mock_user_role):
    client = Client(id=1, full_name="Client Test")
    db_session.add(client)
    db_session.commit()

    user_id = 1
    new_contract = create_contract(
        db_session, user_id=user_id, client_id=client.id, commercial_contact_id=1,
        total_price=1000.0, remaining_price=500.0, statut="En cours"
    )

    # Vérifier que le contrat a été créé
    assert new_contract.id is not None
    assert new_contract.client_id == 1
    assert new_contract.total_price == 1000.0
    assert new_contract.statut == "En cours"

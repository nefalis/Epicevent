import pytest
from unittest import mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.contract_model import Base
from controller.contract_controller import (
    create_contract,
    update_contract,
    delete_contract,
    get_contract_by_id
    )


@pytest.fixture(scope="module")
def test_db():
    """
    Fonction qui crée une base de données SQLite en mémoire pour les tests.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def mock_requires_permission():
    """
    Cette fonction simule la vérification des permissions sans appliquer réellement les vérifications.
    """
    with mock.patch(
        "controller.contract_controller.requires_permission",
        side_effect=lambda x: lambda f: f
    ):
        yield


@mock.patch(
        "authentication.auth_utils.requires_permission",
        side_effect=lambda x: lambda f: f)
@mock.patch(
    "authentication.auth_utils.get_current_user_role",
    return_value='manager'
    )
def test_create_contract(
    mock_get_current_user_role, mock_requires_permission, test_db
):
    """Test pour la création d'un contrat."""
    new_contract = create_contract(
        db=test_db,
        user_id=1,
        token="fake_token",
        client_id=123,
        commercial_contact_id=456,
        total_price=10000,
        remaining_price=5000,
        statut="en attente"
    )

    assert new_contract.client_id == 123
    assert new_contract.commercial_contact_id == 456
    assert new_contract.total_price == 10000
    assert new_contract.remaining_price == 5000
    assert new_contract.statut == "en attente"


@mock.patch(
        "authentication.auth_utils.requires_permission",
        side_effect=lambda x: lambda f: f
        )
@mock.patch(
    "authentication.auth_utils.get_current_user_role",
    return_value='manager'
    )
def test_update_contract(
    mock_get_current_user_role, mock_requires_permission, test_db
):
    """Test pour la mise à jour d'un contrat."""
    new_contract = create_contract(
        db=test_db,
        user_id=1,
        token="fake_token",
        client_id=123,
        commercial_contact_id=456,
        total_price=10000,
        remaining_price=5000,
        statut="en attente"
    )

    updated_contract = update_contract(
        db=test_db,
        user_id=1,
        token="fake_token",
        contract_id=new_contract.id,
        total_price=12000,
        statut="signé"
    )

    assert updated_contract.total_price == 12000
    assert updated_contract.statut == "signé"


@mock.patch(
        "authentication.auth_utils.requires_permission",
        side_effect=lambda x: lambda f: f
        )
@mock.patch(
    "authentication.auth_utils.get_current_user_role",
    return_value='manager'
    )
def test_delete_contract(
    mock_get_current_user_role, mock_requires_permission, test_db
):
    """Test pour la suppression d'un contrat."""
    new_contract = create_contract(
        db=test_db,
        user_id=1,
        token="fake_token",
        client_id=123,
        commercial_contact_id=456,
        total_price=10000,
        remaining_price=5000,
        statut="signé"
    )

    deleted_contract = delete_contract(
        db=test_db,
        user_id=1,
        token="fake_token",
        contract_id=new_contract.id
    )

    assert deleted_contract is not None
    assert get_contract_by_id(test_db, new_contract.id) is None

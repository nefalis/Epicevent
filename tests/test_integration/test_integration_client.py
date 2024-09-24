import pytest
from unittest import mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.client_model import Base
from controller.client_controller import (
    create_client,
    update_client,
    delete_client
)


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def mock_requires_permission():
    with mock.patch(
        "authentication.auth_utils.requires_permission",
        side_effect=lambda x: lambda f: f
    ):
        yield


@mock.patch(
        "authentication.auth_utils.requires_permission",
        side_effect=lambda x: lambda f: f
        )
@mock.patch(
    "authentication.auth_utils.get_current_user_role",
    return_value='manager'
    )
def test_create_client(
    mock_get_current_user_role, mock_requires_permission, test_db
):
    new_client = create_client(
        db=test_db,
        user_id=1,
        token="fake_token",
        full_name="Laura Tatouille",
        email="tatouille@exemple.com",
        phone_number="0600102030",
        company_name="Tatouille entreprise",
        commercial_contact_id=None
    )

    assert new_client.full_name == "Laura Tatouille"
    assert new_client.email == "tatouille@exemple.com"
    assert new_client.phone_number == "0600102030"
    assert new_client.company_name == "Tatouille entreprise"


@mock.patch(
        "authentication.auth_utils.requires_permission",
        side_effect=lambda x: lambda f: f
        )
@mock.patch(
    "authentication.auth_utils.get_current_user_role",
    return_value='manager'
    )
def test_update_client(
    mock_get_current_user_role, mock_requires_permission, test_db
    ):
    # Création d'un client pour la mise à jour
    new_client = create_client(
        db=test_db,
        user_id=1,
        token="fake_token",
        full_name="Laura Tatouille",
        email="fake@exemple.com",
        phone_number="0600102030",
        company_name="Tatouille entreprise",
        commercial_contact_id=None
    )

    updated_client = update_client(
        db=test_db,
        user_id=1,
        token="fake_token",
        client_id=new_client.id,
        full_name="Old Tatouille",
        email="update@exemple.com",
        phone_number="0600102030",
        company_name="Tatouille entreprise",
        commercial_contact_id=None
    )

    assert updated_client.full_name == "Old Tatouille"
    assert updated_client.email == "update@exemple.com"


@mock.patch(
        "authentication.auth_utils.get_current_user_role",
        return_value='manager'
        )
def test_delete_client(mock_get_current_user_role, test_db):
    new_client = create_client(
        db=test_db,
        user_id=1,
        token="fake_token",
        full_name="Laura Tatouille",
        email="fake@exemple.com",
        phone_number="0600102030",
        company_name="Tatouille entreprise",
        commercial_contact_id=None
    )

    deleted_client = delete_client(
        db=test_db,
        user_id=1,
        client_id=new_client.id,
        token="fake_token"
    )

    assert deleted_client is not None
    assert deleted_client.full_name == "Laura Tatouille"

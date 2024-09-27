from sqlalchemy.orm import Session
from model.client_model import Client
from model.user_model import User
from datetime import datetime
from authentication.auth_utils import handle_errors, requires_permission
from authentication.auth_token import get_user_from_token


@handle_errors
def get_all_clients(db: Session, token: str):
    """
    Fonction pour récupérer tous les clients de la base de données.
    """
    get_user_from_token(token, db)
    clients = db.query(Client).all()
    return clients


@handle_errors
@requires_permission("create_client")
def create_client(
    db: Session, user_id: int, token: str, full_name: str, email: str,
    phone_number: str = None, company_name: str = None,
    commercial_contact_id: int = None
):
    """
    Fonction pour créer un nouveau client.
    """
    commercial_contact = db.query(User).filter(
        User.id == commercial_contact_id
        ).first() if commercial_contact_id else None

    if commercial_contact_id and not commercial_contact:
        raise ValueError(
            f"Aucun commercial trouvé avec l'ID {commercial_contact_id}."
            )

    new_client = Client(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        company_name=company_name,
        creation_date=datetime.now(),
        last_update=datetime.now(),
        commercial_contact_id=commercial_contact_id
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


@handle_errors
@requires_permission("update_client")
def update_client(
    db: Session, user_id: int, token: str, client_id: int, **kwargs
):
    """
    Fonction pour mettre à jour un client existant.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None

    for key, value in kwargs.items():
        setattr(client, key, value)

    db.commit()
    db.refresh(client)
    return client


@handle_errors
@requires_permission("delete_client")
def delete_client(db: Session, user_id: int, token: str, client_id: int, ):
    """
    Fonction pour supprimer un client.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None

    db.delete(client)
    db.commit()
    return client


def get_client_by_id(db: Session, client_id: int):
    """
    Récupère un client spécifique par son ID.
    """
    return db.query(Client).filter(Client.id == client_id).first()

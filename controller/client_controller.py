from sqlalchemy.orm import Session
from model.client_model import Client
from model.user_model import User
from datetime import datetime
from authentication.auth_service import get_current_user_role, can_perform_action



def get_all_clients(db: Session):
    """
    Fonction pour récupérer tous les clients de la base de données.
    """
    clients = db.query(Client).all()
    return  clients


def create_client(db: Session, user_id: int, full_name: str, email: str, phone_number: str = None, company_name: str = None, commercial_contact_id: int = None):
    """
    Fonction pour créer un nouveau client.
    """
    user_role = get_current_user_role(user_id, db)
    print(f"Rôle de l'utilisateur debug : {user_role}")
    
    if not can_perform_action(user_role, "create_client"):
        raise PermissionError("Vous n'avez pas les droits nécessaires pour créer un client.")
    
    # Vérifie si le commercial existe dans la base de données
    commercial_contact = db.query(User).filter(User.id == commercial_contact_id).first() if commercial_contact_id else None
    if commercial_contact_id and not commercial_contact:
        raise ValueError(f"Aucun commercial trouvé avec l'ID {commercial_contact_id}.")

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


def update_client(db: Session, user_id: int, client_id: int, full_name: str = None, email: str = None, phone_number: str = None, company_name: str = None, commercial_contact_id: int = None):
    """
    Fonction pour mettre à jour un client existant.
    """
    user_role = get_current_user_role(user_id, db)
    
    if not can_perform_action(user_role, "update_client"):
        raise PermissionError("Vous n'avez pas les droits nécessaires pour modifier un client.")

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None

    # Vérifie si le commercial existe dans la base de données
    if commercial_contact_id:
        commercial_contact = db.query(User).filter(User.id == commercial_contact_id).first()
        if not commercial_contact:
            raise ValueError(f"Aucun commercial trouvé avec l'ID {commercial_contact_id}.")

    if full_name is not None:
        client.full_name = full_name
    if email is not None:
        client.email = email
    if phone_number is not None:
        client.phone_number = phone_number
    if company_name is not None:
        client.company_name = company_name
    if commercial_contact_id is not None:
        client.commercial_contact_id = commercial_contact_id

    try:
        client.last_update = datetime.now()
        db.commit()
        db.refresh(client)
        return client
    except Exception as e:
        db.rollback()
        return None


def delete_client(db: Session, user_id: int, client_id: int):
    """
    Fonction pour supprimer un client.
    """
    user_role = get_current_user_role(user_id, db)
    
    if not can_perform_action(user_role, "delete_client"):
        print(f"Debug: Permissions pour suppression : {can_perform_action(user_role, 'delete_client')}")
        raise PermissionError("Vous n'avez pas les droits nécessaires pour supprimer un client.")
    
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None

    db.delete(client)
    db.commit()
    return client



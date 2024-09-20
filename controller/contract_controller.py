from sqlalchemy.orm import Session
from model.contract_model import Contract
from datetime import datetime
from authentication.auth_service import get_current_user_role, can_perform_action
from authentication.auth_utils import handle_errors, requires_permission

@handle_errors
def get_all_contracts(db: Session):
    """
    Fonction pour récupéré et afficher tous les contrats de la base de données
    """
    contracts = db.query(Contract).all()
    return contracts


@handle_errors
@requires_permission("create_contract")
def create_contract(db: Session, user_id: int, token: str, client_id: int, commercial_contact_id: int, total_price: float, remaining_price: float, statut: str):
    """
    Fonction pour créer un nouveau contrat dans la base de données
    """
    new_contract = Contract(
    client_id=client_id,
    commercial_contact_id=commercial_contact_id,
    total_price=total_price,
    remaining_price=remaining_price,
    creation_date=datetime.now(),
    statut=statut
    )

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return new_contract


@handle_errors
@requires_permission("update_contract")
def update_contract(db: Session,user_id: int, token: str, contract_id: int, **kwargs):
    """
    Met à jour un contrat existant avec les informations fournies.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        return None

    for key, value in kwargs.items():
        setattr(contract, key, value)

    contract.last_update = datetime.now()
    db.commit()
    db.refresh(contract)
    return contract


@handle_errors
@requires_permission("delete_contract")
def delete_contract(db: Session, user_id: int, token: str,contract_id: int):
    """
    Supprime un contrat de la base de données.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        return None

    db.delete(contract)
    db.commit()
    return contract


def get_contract_by_id(db: Session, contract_id: int):
    """
    Récupère un contrat spécifique par son ID.
    """
    return db.query(Contract).filter(Contract.id == contract_id).first()


def get_contracts_by_client_id(db: Session, client_id: int):
    """
    Récupère tous les contrats associés à un client spécifique.
    """
    return db.query(Contract).filter(Contract.client_id == client_id).all()

from sqlalchemy.orm import Session
from model.event_model import Event
from datetime import datetime
from authentication.auth_utils import handle_errors, requires_permission


@handle_errors
def get_all_events(db: Session, token: str):
    """
    Récupère tous les événements de la base de données.
    """
    return db.query(Event).all()


@handle_errors
@requires_permission("create_event")
def create_event(
    db: Session, user_id: int, token: str, event_name: str,
    contract_id: int, client_id: int, client_name: str, client_contact: str,
    date_start: datetime, date_end: datetime, support_contact_id: int,
    location: str, attendees: int, notes: str
):
    """
    Crée un nouvel événement dans la base de données.
    """
    new_event = Event(
        event_name=event_name,
        contract_id=contract_id,
        client_id=client_id,
        client_name=client_name,
        client_contact=client_contact,
        date_start=date_start,
        date_end=date_end,
        support_contact_id=support_contact_id,
        location=location,
        attendees=attendees,
        notes=notes
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@handle_errors
@requires_permission("update_event")
def update_event(
    db: Session, user_id: int, token: str, event_id: int, **kwargs
):
    """
    Met à jour un événement existant avec les informations fournies.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    for key, value in kwargs.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


@handle_errors
@requires_permission("delete_event")
def delete_event(db: Session, event_id: int, user_id: int, token: str):
    """
    Supprime un événement de la base de données.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    db.delete(event)
    db.commit()
    return event


def get_event_by_id(db: Session, event_id: int):
    """
    Récupère un événement spécifique par son ID.
    """
    return db.query(Event).filter(Event.id == event_id).first()

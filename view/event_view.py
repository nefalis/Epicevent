from sqlalchemy.orm import Session
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from config import SessionLocal
from datetime import datetime
from controller.event_controller import (
    get_all_events,
    create_event,
    update_event,
    delete_event,
    get_event_by_id,
)
from controller.client_controller import get_all_clients
from controller.contract_controller import get_contracts_by_client_id
from controller.user_controller import get_users_by_role


console = Console()

def display_events(db: Session):
    """
    Affiche tous les événements.
    """
    events = get_all_events(db)
    if not events:
        console.print("\n[blue]Aucun événement trouvé.[/blue]\n")
        return

    table = Table(title="\nListe des Événements\n")
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Nom de l'événement", justify="center", style="blue")
    table.add_column("Client", justify="center", style="blue")
    table.add_column("Date de début", justify="center", style="blue")
    table.add_column("Date de fin", justify="center", style="blue")
    table.add_column("Lieu", justify="center", style="blue")

    for event in events:
        table.add_row(
            str(event.id),
            event.event_name,
            event.client_name,
            event.date_start.strftime("%Y-%m-%d %H:%M"),
            event.date_end.strftime("%Y-%m-%d %H:%M"),
            event.location
        )

    console.print("\n")
    console.print(table)
    console.print("\n")


def prompt_create_event(db: Session):
    """
    Demande à l'utilisateur de saisir les informations pour créer un nouvel événement.
    """
    clients = get_all_clients(db)
    supports = get_users_by_role(db, role='support')

    if not clients:
        console.print("[blue]Aucun client disponible pour créer un événement.[/blue]")
        return
    if not supports:
        console.print("[blue]Aucun contact support disponible pour créer un événement.[/blue]")
        return

    # Sélection du client
    client_choices = [(f"{client.id} - {client.full_name}", client.id) for client in clients]
    client_choices.insert(0, ("Retour en arrière", None))

    selected_client_text = inquirer.select(
        message="Sélectionnez un client :",
        choices=[choice for choice, _ in client_choices]
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return
    
    selected_client_id = next((id for text, id in client_choices if text == selected_client_text), None)
    selected_client = next(client for client in clients if client.id == selected_client_id)
    
    # Sélection du contrat lié au client
    contracts = get_contracts_by_client_id(db, selected_client_id)
    if not contracts:
        console.print("[blue]Aucun contrat disponible pour ce client.[/blue]")
        return
    
    contract_choices = [(f"{contract.id} - {contract.client.full_name}", contract.id) for contract in contracts]
    selected_contract_text = inquirer.select(
        message=f"Sélectionnez un contrat pour {selected_client.full_name} :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()
    selected_contract_id = next((id for text, id in contract_choices if text == selected_contract_text), None)

    # Sélection du contact support
    support_choices = [(f"{support.id} - {support.complete_name}", support.id) for support in supports]
    support_contact_text = inquirer.select(
        message="Sélectionnez un contact support :",
        choices=[choice for choice, _ in support_choices]
    ).execute()
    support_contact_id = next((id for text, id in support_choices if text == support_contact_text), None)

    # Saisie des autres informations
    event_name = inquirer.text(
        message="Entrez le nom de l'événement :"
    ).execute()

    client_contact = inquirer.text(
        message="Entrez le contact du client :"
    ).execute()

    date_start = inquirer.text(
        message="Entrez la date de début (YYYY-MM-DD HH:MM) :",
        validate=lambda result: datetime.strptime(result, "%Y-%m-%d %H:%M")
    ).execute()

    date_end = inquirer.text(
        message="Entrez la date de fin (YYYY-MM-DD HH:MM) :",
        validate=lambda result: datetime.strptime(result, "%Y-%m-%d %H:%M")
    ).execute()

    location = inquirer.text(
        message="Entrez le lieu :"
    ).execute()

    attendees = inquirer.text(
        message="Entrez le nombre de participants :",
        validate=lambda result: result.isdigit() and int(result) >= 0,
        filter=lambda result: int(result)
    ).execute()

    notes = inquirer.text(
        message="Entrez les notes :"
    ).execute()

    # Création de l'événement
    create_event(
        db,
        event_name=event_name,
        contract_id=selected_contract_id,
        client_id=selected_client_id,
        client_name=selected_client.full_name,
        client_contact=client_contact,
        date_start=datetime.strptime(date_start, "%Y-%m-%d %H:%M"),
        date_end=datetime.strptime(date_end, "%Y-%m-%d %H:%M"),
        support_contact_id=support_contact_id,
        location=location,
        attendees=attendees,
        notes=notes
    )
    console.print(f"\n [blue]Événement créé avec succès ![/blue] \n")


def prompt_update_event(db: Session):
    """
    Demande à l'utilisateur de sélectionner un événement à mettre à jour et les modifications à apporter.
    """
    events = get_all_events(db)
    if not events:
        console.print("\n[blue]Aucun événement disponible pour mise à jour.[/blue]\n")
        return

    event_choices = [(f"{event.id} - {event.event_name}", event.id) for event in events]
    event_choices.insert(0, ("Retour en arrière", None))

    event_id = inquirer.select(
        message="Sélectionnez un événement à modifier :",
        choices=[choice for choice, _ in event_choices]
    ).execute()

    if event_id == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    event_id = next((id for text, id in event_choices if text == event_id), None)

    event = get_event_by_id(db, event_id)
    if not event:
        console.print("[blue]Événement non trouvé.[/blue]")
        return

    event_name = inquirer.text(
        message=f"Nom de l'événement actuel : {event.event_name}. Entrez le nouveau nom (laisser vide pour conserver) :",
        filter=lambda result: result if result else event.event_name
    ).execute()

    date_start = inquirer.text(
        message=f"Date de début actuelle : {event.date_start.strftime('%Y-%m-%d %H:%M')}. Entrez la nouvelle date de début (YYYY-MM-DD HH:MM) (laisser vide pour conserver) :",
        validate=lambda result: result == "" or datetime.strptime(result, "%Y-%m-%d %H:%M"),
        filter=lambda result: datetime.strptime(result, "%Y-%m-%d %H:%M") if result else event.date_start
    ).execute()

    date_end = inquirer.text(
        message=f"Date de fin actuelle : {event.date_end.strftime('%Y-%m-%d %H:%M')}. Entrez la nouvelle date de fin (YYYY-MM-DD HH:MM) (laisser vide pour conserver) :",
        validate=lambda result: result == "" or datetime.strptime(result, "%Y-%m-%d %H:%M"),
        filter=lambda result: datetime.strptime(result, "%Y-%m-%d %H:%M") if result else event.date_end
    ).execute()

    location = inquirer.text(
        message=f"Lieu actuel : {event.location}. Entrez le nouveau lieu (laisser vide pour conserver) :",
        filter=lambda result: result if result else event.location
    ).execute()

    notes = inquirer.text(
        message=f"Notes actuelles : {event.notes}. Entrez les nouvelles notes (laisser vide pour conserver) :",
        filter=lambda result: result if result else event.notes
    ).execute()

    update_event(
        db,
        event_id=event_id,
        event_name=event_name,
        location=location,
        notes=notes,
        date_start=date_start,
        date_end=date_end
    )
    console.print(f"\n [blue]Événement mis à jour avec succès ![/blue] \n")


def prompt_delete_event(db: Session):
    """
    Demande à l'utilisateur de sélectionner un événement à supprimer.
    """
    events = get_all_events(db)
    if not events:
        console.print("\n[blue]Aucun événement disponible pour suppression.[/blue]\n")
        return

    event_choices = [(f"{event.id} - {event.event_name}", event.id) for event in events]
    event_choices.insert(0, ("Retour en arrière", None))

    event_id = inquirer.select(
        message="Sélectionnez un événement à supprimer :",
        choices=[choice for choice, _ in event_choices]
    ).execute()

    if event_id == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    event_id = next((id for text, id in event_choices if text == event_id), None)

    delete_event(db, event_id)
    console.print(f"\n [blue]Événement supprimé avec succès ![/blue] \n")


def event_menu(db: Session):
    """
    Menu principal pour la gestion des événements.
    """
    db: Session = SessionLocal()

    try:
        while True:
            choice = inquirer.select(
                message="Gestion des Événements - Sélectionnez une action :",
                choices=[
                    "Lister les événements",
                    "Ajouter un événement",
                    "Modifier un événement",
                    "Supprimer un événement",
                    "Retour au menu principal"
                ]
            ).execute()

            if choice == "Lister les événements":
                display_events(db)
            elif choice == "Ajouter un événement":
                prompt_create_event(db)
            elif choice == "Modifier un événement":
                prompt_update_event(db)
            elif choice == "Supprimer un événement":
                prompt_delete_event(db)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()

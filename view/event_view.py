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
from authentication.auth_service import can_perform_action
from authentication.auth_token import get_user_from_token, load_token
from view.validation import validate_digits, validate_text


console = Console()


def display_events(db: Session, token: str):
    """
    Affiche tous les événements.
    """
    events = get_all_events(db, token)
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
    table.add_column("Contact Support", justify="center", style="blue")
    table.add_column("Participants", justify="center", style="blue")
    table.add_column("Notes", justify="center", style="blue")

    for event in events:
        support_contact = event.support_contact.complete_name if event.support_contact else "N/A"
        attendees = str(event.attendees) if event.attendees is not None else "0"
        notes = str(event.notes) if event.notes else "Pas de notes"

        table.add_row(
            str(event.id),
            event.event_name,
            event.client_name,
            event.date_start.strftime("%Y-%m-%d %H:%M"),
            event.date_end.strftime("%Y-%m-%d %H:%M"),
            event.location,
            support_contact,
            attendees,
            notes
        )

    console.print("\n")
    console.print(table)
    console.print("\n")


def prompt_create_event(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de saisir les
    informations pour créer un nouvel événement.
    """
    clients = get_all_clients(db, token)
    supports = get_users_by_role(db, role='support')

    if not clients:
        console.print(
            "\n[blue]Aucun client disponible pour créer un événement.[/blue]\n"
            )
        return
    if not supports:
        console.print(
            "\n[blue]Aucun contact support disponible pour créer un événement.[/blue]\n"
            )
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

    selected_client_id = next(
        (id for text, id in client_choices if text == selected_client_text), None
        )
    selected_client = next(
        client for client in clients if client.id == selected_client_id
        )

    contracts = get_contracts_by_client_id(db, selected_client_id)
    if not contracts:
        console.print(
            "\n[blue]Aucun contrat disponible pour ce client.[/blue]\n"
            )
        return

    contract_choices = [
        (f"{contract.id} - {contract.client.full_name}", contract.id)
        for contract in contracts
        ]
    selected_contract_text = inquirer.select(
        message=f"Sélectionnez un contrat pour {selected_client.full_name} :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()
    selected_contract_id = next(
        (id for text, id in contract_choices if text == selected_contract_text), None
        )

    # Sélection du contact support
    support_choices = [
        (f"{support.id} - {support.complete_name}", support.id)
        for support in supports
        ]
    support_contact_text = inquirer.select(
        message="Sélectionnez un contact support :",
        choices=[choice for choice, _ in support_choices]
    ).execute()
    support_contact_id = next(
        (id for text, id in support_choices if text == support_contact_text), None
        )

    event_name = inquirer.text(
        message="Entrez le nom de l'événement :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir"
    ).execute()

    client_contact = inquirer.text(
        message="Entrez le contact du client :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

# Saisie et validation des dates
    while True:
        try:
            date_start = inquirer.text(
                message="Entrez la date de début (YYYY-MM-DD HH:MM) :"
            ).execute()
            start_dt = datetime.strptime(date_start, "%Y-%m-%d %H:%M")
            break
        except ValueError:
            console.print(
                "[red]Erreur : Le format de la date de début"
                "est incorrect. Veuillez réessayer.[/red]"
            )

    while True:
        try:
            date_end = inquirer.text(
                message="Entrez la date de fin (YYYY-MM-DD HH:MM) :"
            ).execute()
            end_dt = datetime.strptime(date_end, "%Y-%m-%d %H:%M")
            # Validation que la date de fin est après la date de début
            if end_dt <= start_dt:
                console.print(
                    "[red]Erreur : La date de fin doit être après la date de début."
                    "Veuillez réessayer.[/red]"
                    )
                continue
            break
        except ValueError:
            console.print(
                "[red]Erreur : Le format de la date de fin est incorrect."
                "Veuillez réessayer.[/red]"
                )

    location = inquirer.text(
        message="Entrez le lieu :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    attendees = inquirer.text(
        message="Entrez le nombre de participants :",
        validate=lambda result: validate_digits(result),
        invalid_message="Veuillez entrer uniquement des chiffres."
    ).execute()

    notes = inquirer.text(
        message="Entrez les notes :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    # Création de l'événement
    create_event(
        db,
        user_id=user_id,
        token=token,
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
    console.print("\n [blue]Événement créé avec succès ![/blue] \n")


def prompt_update_event(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un événement
    à mettre à jour et les modifications à apporter.
    """
    events = get_all_events(db, token)
    if not events:
        console.print("\n[blue]Aucun événement disponible pour mise à jour.[/blue]\n")
        return

    event_choices = [
        (f"{event.id} - {event.event_name}", event.id)for event in events
    ]
    event_choices.insert(0, ("Retour en arrière", None))

    event_id = inquirer.select(
        message="Sélectionnez un événement à modifier :",
        choices=[choice for choice, _ in event_choices]
    ).execute()

    if event_id == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    event_id = next(
        (id for text, id in event_choices if text == event_id), None
        )

    event = get_event_by_id(db, event_id)
    if not event:
        console.print("\n[blue]Événement non trouvé.[/blue]\n")
        return

    event_name = inquirer.text(
        message=f"Nom de l'événement actuel : {event.event_name}. "
                "Entrez le nouveau nom (laisser vide pour conserver) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    date_start_str = inquirer.text(
        message=f"Date de début actuelle : {event.date_start.strftime('%Y-%m-%d %H:%M')}."
        f"Entrez la nouvelle date de début (YYYY-MM-DD HH:MM) (laisser vide pour conserver) :",
        validate=lambda result: result == "" or datetime.strptime(result, "%Y-%m-%d %H:%M"),
        filter=lambda result: datetime.strptime(result, "%Y-%m-%d %H:%M") if result else event.date_start
    ).execute()

    date_end_str = inquirer.text(
        message=(
            f"Date de fin actuelle : {event.date_end.strftime('%Y-%m-%d %H:%M')}. "
            "Entrez la nouvelle date de fin (YYYY-MM-DD HH:MM) (laisser vide pour conserver) :"
        ),
        validate=lambda result: result == "" or datetime.strptime(result, "%Y-%m-%d %H:%M"),
        filter=lambda result: datetime.strptime(result, "%Y-%m-%d %H:%M") if result else event.date_end
    ).execute()

    # Convertir les dates pour comparaison et vérifier si date_end est après date_start
    date_start = date_start_str if isinstance(date_start_str, datetime) else event.date_start
    date_end = date_end_str if isinstance(date_end_str, datetime) else event.date_end

    # Vérification si la date de fin est après la date de début
    if date_end <= date_start:
        console.print(
            "[red]Erreur : La date de fin doit être après la date de début.[/red]"
            )
        return

    attendees_input = inquirer.text(
        message=f"Nombre de participant actuel : {event.attendees}. "
                "Entrez le nouveau nombre de participant (laisser vide pour conserver) :",
        validate=lambda result: validate_digits(result) if result else True,
        invalid_message="Veuillez entrer uniquement des chiffres."
    ).execute()

    attendees = int(attendees_input) if attendees_input else event.attendees

    location = inquirer.text(
        message=f"Lieu actuel : {event.location}. "
                "Entrez le nouveau lieu (laisser vide pour conserver) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    notes = inquirer.text(
        message=f"Notes actuelles : {event.notes}. "
                "Entrez les nouvelles notes (laisser vide pour conserver) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    update_event(
        db,
        user_id,
        token=token,
        event_id=event_id,
        event_name=event_name,
        location=location,
        notes=notes,
        date_start=date_start,
        date_end=date_end,
        attendees=attendees
    )
    console.print("\n [blue]Événement mis à jour avec succès ![/blue] \n")


def prompt_delete_event(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un événement à supprimer.
    """
    events = get_all_events(db, token)
    if not events:
        console.print(
            "\n[blue]Aucun événement disponible pour suppression.[/blue]\n"
            )
        return
    
    event_choices = [
        (f"{event.id} - {event.event_name}", event.id) for event in events
        ]
    event_choices.insert(0, ("Retour en arrière", None))

    event_id_text = inquirer.select(
        message="Sélectionnez un événement à supprimer :",
        choices=[choice for choice, _ in event_choices]
    ).execute()

    if event_id_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    event_id = next((
        id for text, id in event_choices
        if text == event_id_text), None
        )

    confirmation = inquirer.confirm(
        message=f"Êtes-vous sûr de vouloir supprimer l'événement' {event_id} ?",
        default=False
    ).execute()

    if not confirmation:
        console.print("\n[blue]Suppression annulée, événement non supprimé.[/blue]\n")
        return

    delete_event(db, user_id, token, event_id)
    console.print("\n [blue]Événement supprimé avec succès ![/blue] \n")


def event_menu(current_user_role, user_id, token):
    """
    Menu principal pour la gestion des événements.
    """
    db: Session = SessionLocal()

    try:
        token = load_token()
        user = get_user_from_token(token, db)
        if not user:
            console.print(
                "\n[red]Token invalide ou expiré. Veuillez vous reconnecter.[/red]\n"
                )
            return
        while True:
            # Obtenir les options de menu en fonction des permissions
            menu_options = []
            if can_perform_action(current_user_role, "get_all_events"):
                menu_options.append("Lister les événements")
            if can_perform_action(current_user_role, "create_event"):
                menu_options.append("Ajouter un événement")
            if can_perform_action(current_user_role, "update_event"):
                menu_options.append("Modifier un événement")
            if can_perform_action(current_user_role, "delete_event"):
                menu_options.append("Supprimer un événement")

            menu_options.append("Retour au menu principal")

            choice = inquirer.select(
                message="Gestion des Événements - Sélectionnez une action :",
                choices=menu_options
            ).execute()

            if choice == "Lister les événements":
                display_events(db, token)
            elif choice == "Ajouter un événement":
                prompt_create_event(db, user_id, token)
            elif choice == "Modifier un événement":
                prompt_update_event(db, user_id, token)
            elif choice == "Supprimer un événement":
                prompt_delete_event(db, user_id, token)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()

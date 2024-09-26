from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
from sqlalchemy.orm import Session
from controller.client_controller import (
    get_all_clients,
    create_client,
    update_client,
    delete_client,
    get_client_by_id
    )
from config import SessionLocal
from authentication.auth_service import (
    can_perform_action,
    get_current_user_role
    )
from authentication.auth_token import get_user_from_token, load_token
from controller.user_controller import get_commercials
from view.validation import (
    validate_email,
    validate_phone_number,
    validate_text)


console = Console()


def display_clients(db: Session, token: str):
    """
    Affiche la liste des clients.
    """

    clients = get_all_clients(db, token)
    if not clients:
        console.print("\n[blue]Aucun client trouvé.[/blue]\n")
        return

    table = Table(title="Liste des Clients")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Nom Complet", style="blue")
    table.add_column("Email", style="blue")
    table.add_column("Téléphone", style="blue")
    table.add_column("Entreprise", style="blue")
    table.add_column("Date de Création", style="blue")
    table.add_column("Dernière Mise à Jour", style="blue")
    table.add_column("Commercial", style="blue")

    for client in clients:
        commercial_name = (
            client.commercial_contact.complete_name
            if client.commercial_contact else "N/A"
        )
        table.add_row(
            str(client.id),
            client.full_name,
            client.email,
            client.phone_number or "N/A",
            client.company_name or "N/A",
            str(client.creation_date),
            str(client.last_update),
            commercial_name,
        )

    console.print("\n")
    console.print(table)
    console.print("\n")


def select_commercial(db: Session, token: str):
    """
    Fonction pour sélectionner un commercial
    dans une liste des commerciaux disponibles.
    """
    commercials = get_commercials(db)
    if not commercials:
        console.print
        ("\n[[blue]Aucun commercial disponible.[/blue]\n[")
        return None

    choices = [(f"{commercial.id} - {commercial.complete_name}",
                commercial.id) for commercial in commercials]
    choices.insert(0, ("Retour en arrière", None))

    choice = inquirer.select(
        message="Sélectionnez un commercial :",
        choices=[choice for choice, _ in choices],
    ).execute()

    if choice == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return None

    commercial_id = next((id for text, id in choices if text == choice), None)
    return commercial_id


def prompt_create_client(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de saisir les
    informations pour créer un nouveau client.
    """

    user_role = get_current_user_role(user_id, db, token)

    if not can_perform_action(user_role, "create_client"):
        console.print(
            "\n[red]Vous n'avez pas les droits"
            "nécessaires pour créer un client view.[/red]\n"
            )
        return

    start_creation = inquirer.select(
        message="Souhaitez-vous créer un nouveau client ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_creation == "Retour en arrière":
        console.print("\n[blue]Création annulée, retour en arrière.[/blue]\n")
        return

    full_name = inquirer.text(
        message="Entrez le nom complet du client :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir uniquement"
        "des lettres, espaces ou tiret."
    ).execute()

    email = inquirer.text(
        message="Entrez l'email du client :",
        validate=lambda result: validate_email(result),
        invalid_message="Veuillez entrer un email valide"
        "(exemple: utilisateur@domaine.com)."
    ).execute()

    phone_number = inquirer.text(
        message="Entrez le numéro de téléphone :",
        validate=lambda result: validate_phone_number(result),
        invalid_message="Veuillez entrer un numéro de téléphone"
        "valide (exemple 03 00 00 00 00 )."
    ).execute()

    company_name = inquirer.text(
        message="Entrez le nom de l'entreprise :",
        validate=lambda result: validate_text(result) or result == "",
        invalid_message="Le nom doit contenir uniquement"
        "des lettres, espaces ou tiret."
    ).execute()

    commercial_contact_id = select_commercial(db, token)

    try:
        new_client = create_client(
            db,
            user_id=user_id,
            token=token,
            full_name=full_name,
            email=email,
            phone_number=phone_number if phone_number else None,
            company_name=company_name if company_name else None,
            commercial_contact_id=commercial_contact_id
        )
        console.print(
            f"\n[blue]Nouveau client créé :[/blue]\n"
            f"ID: {new_client.id},\n"
            f"Nom: {new_client.full_name},\n"
            f"Email: {new_client.email}\n"
            )
    except ValueError as e:
        console.print(f"\n[red]{str(e)}[/red]\n")


def prompt_update_client(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un
    client et de mettre à jour ses informations.
    """
    clients = get_all_clients(db, token)
    if not clients:
        console.print("\n[blue]Aucun client disponible.[/blue]\n")
        return

    client_choices = [
        (f"{client.id} - {client.full_name}", client.id) for client in clients
        ]
    client_choices.insert(0, ("Retour en arrière", None))

    selected_client_text = inquirer.select(
        message="Sélectionnez un client à modifier :",
        choices=[choice for choice, _ in client_choices],
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    client_id = next(
        (id for text, id in client_choices if text == selected_client_text), None
        )

    client = get_client_by_id(db, client_id)
    if not client:
        console.print("\n[red]Client non trouvé.[/red]\n")
        return

    full_name = inquirer.text(
        message=f"Nom complet actuel : {client.full_name}\n"
                "Entrez le nouveau nom complet (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute() or client.full_name

    email = inquirer.text(
        message=f"Email actuel : {client.email}\n"
                "Entrez le nouvel email (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_email(result) if result else True,
        invalid_message="Veuillez entrer un email valide (exemple: utilisateur@domaine.com)."
    ).execute() or client.email

    phone_number = inquirer.text(
        message=f"Numéro de téléphone actuel : {client.phone_number}\n"
                "Entrez le nouveau numéro de téléphone (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_phone_number(result) if result else True,
        invalid_message="Veuillez entrer un numéro de téléphone valide (uniquement des chiffres, avec ou sans +)."
    ).execute() or client.phone_number

    company_name = inquirer.text(
        message=f"Nom de l'entreprise actuel : {client.company_name}\n"
                "Entrez le nouveau nom de l'entreprise (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute() or client.company_name

    change_commercial = inquirer.confirm(
        message="Voulez-vous changer de commercial ?", default=False
    ).execute()
    commercial_contact_id = select_commercial(db, token) if change_commercial else client.commercial_contact_id

    # Mettre à jour le client
    updated_client = update_client(
        db,
        user_id,
        token=token,
        client_id=client_id,
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        company_name=company_name,
        commercial_contact_id=commercial_contact_id,
    )

    if updated_client:
        console.print(
            f"\n[blue]Client mis à jour : {updated_client.id} - "
            f"Nom : {updated_client.full_name}, Email : {updated_client.email}\n"
        )
    else:
        console.print("\n[red]Problème lors de la mise à jour du client.[/red]\n")


def prompt_delete_client(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un client à supprimer.
    """

    clients = get_all_clients(db, token)
    if not clients:
        console.print(
            "\n[red]Aucun client disponible pour suppression.[/red]\n"
            )
        return

    client_choices = [(f"Client ID {client.id} - {client.full_name}", client.id) for client in clients]
    client_choices.insert(0, ("Retour en arrière", None))

    selected_client_text = inquirer.select(
        message="Sélectionnez un client à supprimer :",
        choices=[choice for choice, _ in client_choices],
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    client_id = next(
        (id for text, id in client_choices
            if text == selected_client_text), None
    )

    confirmation = inquirer.confirm(
        message=f"Êtes-vous sûr de vouloir supprimer le client {client_id} ?",
        default=False
    ).execute()

    if not confirmation:
        console.print("\n[blue]Suppression annulée, client non supprimé.[/blue]\n")
        return

    client = delete_client(db, user_id, token, client_id)
    console.print(
        f"\n[blue]Client supprimé :[/blue] {client.id}, "
        f"Nom: {client.full_name}\n"
    )


def client_menu(current_user_role, user_id, token):
    db: Session = SessionLocal()

    try:
        # Vérifier que le token est valide et obtenir l'utilisateur
        token = load_token()
        user = get_user_from_token(token, db)
        if not user:
            console.print(
                "\n[red]Token invalide ou expiré."
                "Veuillez vous reconnecter.[/red]\n"
                )
            return

        while True:
            menu_options = []
            if can_perform_action(current_user_role, "get_all_clients"):
                menu_options.append("Afficher tous les clients")
            if can_perform_action(current_user_role, "create_client"):
                menu_options.append("Créer un nouveau client")
            if can_perform_action(current_user_role, "update_client"):
                menu_options.append("Modifier un client")
            if can_perform_action(current_user_role, "delete_client"):
                menu_options.append("Supprimer un client")

            menu_options.append("Retour au menu principal")

            choice = inquirer.select(
                message="Gestion des Clients - Sélectionnez une action :",
                choices=menu_options
            ).execute()

            if choice == "Afficher tous les clients":
                display_clients(db, token)
            elif choice == "Créer un nouveau client":
                prompt_create_client(db, user.id, token)
            elif choice == "Modifier un client":
                prompt_update_client(db, user.id, token)
            elif choice == "Supprimer un client":
                prompt_delete_client(db, user.id, token)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()

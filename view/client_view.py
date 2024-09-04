from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
from sqlalchemy.orm import Session
from controller.client_controller import get_all_clients, create_client, update_client, delete_client, get_commercials
from config import SessionLocal

console = Console()

def display_clients(db: Session):
    """
    Affiche la liste des clients.
    """

    clients = get_all_clients(db)
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
            client.commercial_contact.complete_name if client.commercial_contact else "N/A"
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


def select_commercial(db: Session):
    """
    Fonction pour sélectionner un commercial dans une liste des commerciaux disponibles.
    """
    commercials = get_commercials(db)
    if not commercials:
        console.print("[blue]Aucun commercial disponible.[/blue]")
        return None

    choices = [(f"{commercial.id} - {commercial.complete_name}", commercial.id) for commercial in commercials]
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

def prompt_create_client(db: Session):
    """
    Demande à l'utilisateur de saisir les informations pour créer un nouveau client.
    """

    start_creation = inquirer.select(
        message="Souhaitez-vous créer un nouveau client ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_creation == "Retour en arrière":
        console.print("\n[blue]Création annulée, retour en arrière.[/blue]\n")
        return

    full_name = inquirer.text(message="Entrez le nom complet du client:").execute()
    email = inquirer.text(message="Entrez l'email du client:").execute()
    phone_number = inquirer.text(message="Entrez le numéro de téléphone:").execute()
    company_name = inquirer.text(message="Entrez le nom de l'entreprise:").execute()
    commercial_contact_id = select_commercial(db)

    try:
        new_client = create_client(
            db,
            full_name=full_name,
            email=email,
            phone_number=phone_number if phone_number else None,
            company_name=company_name if company_name else None,
            commercial_contact_id=commercial_contact_id
        )
        console.print(f"[blue]Nouveau client créé :[/blue] {new_client.id}, Nom: {new_client.full_name}, Email: {new_client.email}")
    except ValueError as e:
        console.print(f"[red]{str(e)}[/red]")

def prompt_update_client(db: Session):
    """
    Demande à l'utilisateur de sélectionner un client et de mettre à jour ses informations.
    """
    clients = get_all_clients(db)
    if not clients:
        console.print("\n[blue]Aucun client disponible pour mise à jour.[/blue]\n")
        return

    client_choices = [(f"{client.id} - {client.full_name}", client.id) for client in clients]
    client_choices.insert(0, ("Retour en arrière", None))

    selected_client_text = inquirer.select(
        message="Sélectionnez un client à modifier :",
        choices=[choice for choice, _ in client_choices],
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    client_id = next((id for text, id in client_choices if text == selected_client_text), None)

    full_name = inquirer.text(message="Entrez le nouveau nom complet (laissez vide pour ne pas changer):").execute()
    email = inquirer.text(message="Entrez le nouvel email (laissez vide pour ne pas changer):").execute()
    phone_number = inquirer.text(
        message="Entrez le nouveau numéro de téléphone (laissez vide pour ne pas changer):"
    ).execute()

    company_name = inquirer.text(message="Entrez le nouveau nom de l'entreprise (laissez vide pour ne pas changer):").execute()
    change_commercial = inquirer.confirm(message="Voulez-vous changer de commercial ?", default=False).execute()

    commercial_contact_id = select_commercial(db) if change_commercial else None

    updated_client = update_client(
        db,
        client_id,
        full_name or None,
        email or None,
        phone_number or None,
        company_name or None,
        commercial_contact_id,
    )
    if updated_client:
        console.print(
            f"[blue]Client mis à jour :[/blue] {updated_client.id}, Nom: {updated_client.full_name}, Email: {updated_client.email}"
        )
    else:
        console.print("[blue]Client non trouvé.[/blue]")



def prompt_delete_client(db: Session):
    """
    Demande à l'utilisateur de sélectionner un client à supprimer.
    """

    clients = get_all_clients(db)
    if not clients:
        console.print("\n[red]Aucun client disponible pour suppression.[/red]\n")
        return

    client_choices = [(f"{client.id} - {client.full_name}", client.id) for client in clients]
    client_choices.insert(0, ("Retour en arrière", None))

    selected_client_text = inquirer.select(
        message="Sélectionnez un client à supprimer :",
        choices=[choice for choice, _ in client_choices],
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    client_id = next((id for text, id in client_choices if text == selected_client_text), None)

    client = delete_client(db, client_id)
    if client:
        console.print(f"[blue]Client supprimé :[/blue] {client.id}, Nom: {client.full_name}")
    else:
        console.print("[blue]Client non trouvé.[/blue]")

def client_menu():
    db: Session = SessionLocal()

    try:
        while True:
            choice = inquirer.select(
                message="Choisissez une option:",
                choices=[
                    "Afficher tous les clients",
                    "Créer un nouveau client",
                    "Modifier un client",
                    "Supprimer un client",
                    "Retour au menu principal"
                ]
            ).execute()

            if choice == "Afficher tous les clients":
                display_clients(db)
            elif choice == "Créer un nouveau client":
                prompt_create_client(db)
            elif choice == "Modifier un client":
                prompt_update_client(db)
            elif choice == "Supprimer un client":
                prompt_delete_client(db)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()
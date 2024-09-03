from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
from sqlalchemy.orm import Session
from controller.client_controller import get_all_clients, create_client, update_client, delete_client, get_commercials
from config import SessionLocal

console = Console()

def display_clients(db: Session):
    clients = get_all_clients(db)
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
        commercial_name = client.commercial_contact.complete_name if client.commercial_contact else "N/A"
        table.add_row(
            str(client.id),
            client.full_name,
            client.email,
            client.phone_number or "N/A",
            client.company_name or "N/A",
            str(client.creation_date),
            str(client.last_update),
            commercial_name
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
    choice = inquirer.select(
        message="Sélectionnez un commercial :",
        choices=[choice for choice, _ in choices],
    ).execute()

    commercial_id = next((id for text, id in choices if text == choice), None)
    return commercial_id

def prompt_create_client(db: Session):
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
    client_id = int(inquirer.text(message="Entrez l'ID du client à modifier:").execute())
    full_name = inquirer.text(message="Entrez le nouveau nom complet (laissez vide pour ne pas changer):").execute()
    email = inquirer.text(message="Entrez le nouvel email (laissez vide pour ne pas changer):").execute()
    phone_number = inquirer.text(message="Entrez le nouveau numéro de téléphone (laissez vide pour ne pas changer):").execute()
    company_name = inquirer.text(message="Entrez le nouveau nom de l'entreprise (laissez vide pour ne pas changer):").execute()
    change_commercial = inquirer.confirm(message="Voulez-vous changer de commercial ?", default=False).execute()
    commercial_contact_id = select_commercial(db) if change_commercial else None

    updated_client = update_client(db, client_id, full_name or None, email or None, phone_number or None, company_name or None, commercial_contact_id)
    if updated_client:
        console.print(f"[blue]Client mis à jour :[/blue] {updated_client.id}, Nom: {updated_client.full_name}, Email: {updated_client.email}")
    else:
        console.print("[blue]Client non trouvé.[/blue]")

def prompt_delete_client(db: Session):
    client_id = int(inquirer.text(message="Entrez l'ID du client à supprimer:").execute())
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
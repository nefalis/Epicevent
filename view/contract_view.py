from sqlalchemy.orm import Session
from controller.contract_controller import (
    get_all_contracts,
    create_contract,
    update_contract,
    delete_contract,
    get_contract_by_id,
    get_commercials,
)
from controller.client_controller import get_all_clients
from controller.user_controller import get_all_users
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from config import SessionLocal


console = Console()


def display_contracts(db: Session):
    """
    Fonction pour afficher tous les contrats
    """
    contracts = get_all_contracts(db)
    if not contracts:
        console.print("\n[blue]Aucun contrat trouvé.[/blue]\n")
        return

    table = Table(title="\nListe des Contrats\n")
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Client", justify="center", style="blue")
    table.add_column("Commercial", justify="center", style="blue")
    table.add_column("Prix Total", justify="center", style="blue")
    table.add_column("Prix Restant", justify="center", style="blue")
    table.add_column("Statut", justify="center", style="blue")

    for contract in contracts:
        table.add_row(
            str(contract.id),
            contract.client.full_name,
            contract.commercial_contact.complete_name,
            f"{contract.total_price:.2f} €",
            f"{contract.remaining_price:.2f} €",
            contract.statut
        )

    console.print("\n")
    console.print(table)
    console.print("\n")


def prompt_create_contract(db: Session):
    """
    Demande à l'utilisateur de saisir les informations pour créer un nouveau contrat.
    """
    clients = get_all_clients(db)
    commercials = get_commercials(db)

    if not clients:
        console.print("[blue]Aucun client disponible pour créer un contrat.[/blue]")
        return
    if not commercials:
        console.print("[blue]Aucun commercial disponible pour créer un contrat.[/blue]")
        return

    client_choices = [(f"{client.id} - {client.full_name}", client.id) for client in clients]
    commercial_choices = [(f"{commercial.id} - {commercial.complete_name}", commercial.id) for commercial in commercials]

    client_id = inquirer.select(
        message="Sélectionnez un client :",
        choices=[choice for choice, _ in client_choices]
    ).execute()

    client_id = next((id for text, id in client_choices if text == client_id), None)

    commercial_contact_id = inquirer.select(
        message="Sélectionnez un commercial :",
        choices=[choice for choice, _ in commercial_choices]
    ).execute()

    commercial_contact_id = next((id for text, id in commercial_choices if text == commercial_contact_id), None)

    total_price = inquirer.text(
        message="Entrez le prix total :",
        validate=lambda result: result.replace('.', '', 1).isdigit() and float(result) > 0,
        filter=lambda result: float(result)
    ).execute()

    remaining_price = inquirer.text(
        message="Entrez le prix restant :",
        validate=lambda result: result.replace('.', '', 1).isdigit() and float(result) >= 0,
        filter=lambda result: float(result)
    ).execute()

    statut = inquirer.text(
        message="Entrez le statut du contrat :"
    ).execute()

    create_contract(
        db,
        client_id=client_id,
        commercial_contact_id=commercial_contact_id,
        total_price=total_price,
        remaining_price=remaining_price,
        statut=statut
    )
    console.print("[blue]Contrat créé avec succès ![/blue]")


def prompt_update_contract(db: Session):
    """
    Demande à l'utilisateur de sélectionner un contrat à mettre à jour et les modifications à apporter.
    """
    contracts = get_all_contracts(db)
    if not contracts:
        console.print("\n[blue]Aucun contrat disponible pour mise à jour.[/blue]\n")
        return

    contract_choices = [(f"{contract.id} - {contract.client.full_name}", contract.id) for contract in contracts]

    contract_id = inquirer.select(
        message="Sélectionnez un contrat à modifier :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()

    contract_id = next((id for text, id in contract_choices if text == contract_id), None)

    contract = get_contract_by_id(db, contract_id)
    if not contract:
        console.print("[blue]Contrat non trouvé.[/blue]")
        return

    # Collecte des nouvelles valeurs
    total_price = inquirer.text(
        message=f"Prix total actuel : {contract.total_price}. Entrez le nouveau prix (laisser vide pour conserver) :",
        filter=lambda result: float(result) if result else contract.total_price
    ).execute()

    remaining_price = inquirer.text(
        message=f"Prix restant actuel : {contract.remaining_price}. Entrez le nouveau prix restant (laisser vide pour conserver) :",
        filter=lambda result: float(result) if result else contract.remaining_price
    ).execute()

    statut = inquirer.text(
        message=f"Statut actuel : {contract.statut}. Entrez le nouveau statut (laisser vide pour conserver) :",
        filter=lambda result: result if result else contract.statut
    ).execute()

    update_contract(
        db,
        contract_id=contract_id,
        total_price=total_price,
        remaining_price=remaining_price,
        statut=statut
    )
    console.print("[blue]Contrat mis à jour avec succès ![/blue]")


def prompt_delete_contract(db: Session):
    """
    Demande à l'utilisateur de sélectionner un contrat à supprimer.
    """
    contracts = get_all_contracts(db)
    if not contracts:
        console.print("\n[red]Aucun contrat disponible pour suppression.[/red]\n")
        return

    contract_choices = [(f"{contract.id} - {contract.client.full_name}", contract.id) for contract in contracts]

    contract_id = inquirer.select(
        message="Sélectionnez un contrat à supprimer :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()

    contract_id = next((id for text, id in contract_choices if text == contract_id), None)

    delete_contract(db, contract_id)
    console.print("[green]Contrat supprimé avec succès ![/green]")


def contract_menu(db: Session):
    """
    Menu principal pour la gestion des contrats.
    """
    db: Session = SessionLocal()

    try:
        while True:
            choice = inquirer.select(
                message="Gestion des Contrats - Sélectionnez une action :",
                choices=[
                    "Lister les contrats",
                    "Ajouter un contrat",
                    "Modifier un contrat",
                    "Supprimer un contrat",
                    "Retour au menu principal"
                ]
            ).execute()

            if choice == "Lister les contrats":
                display_contracts(db)
            elif choice == "Ajouter un contrat":
                prompt_create_contract(db)
            elif choice == "Modifier un contrat":
                prompt_update_contract(db)
            elif choice == "Supprimer un contrat":
                prompt_delete_contract(db)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()
from sqlalchemy.orm import Session
from controller.contract_controller import (
    get_all_contracts,
    create_contract,
    update_contract,
    delete_contract,
    get_contract_by_id,
)
from controller.client_controller import get_all_clients
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from config import SessionLocal
from authentication.auth_service import can_perform_action
from controller.user_controller import get_commercials
from view.validation import validate_text


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


def prompt_create_contract(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de saisir les informations pour créer un nouveau contrat.
    """
    clients = get_all_clients(db)
    commercials = get_commercials(db)

    if not clients:
        console.print("\n[[blue]Aucun client disponible pour créer un contrat.[/blue]\n[")
        return
    
    
    if not commercials:
        console.print("\n[[blue]Aucun commercial disponible pour créer un contrat.[/blue]\n[")
        return

    client_choices = [(f"{client.id} - {client.full_name}", client.id) for client in clients]
    client_choices.insert(0, ("Retour en arrière", None))
    
    commercial_choices = [(f"{commercial.id} - {commercial.complete_name}", commercial.id) for commercial in commercials]

    selected_client_text = inquirer.select(
        message="Sélectionnez un client :",
        choices=[choice for choice, _ in client_choices]
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    client_id = next((id for text, id in client_choices if text == selected_client_text), None)

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
        validate=lambda result: (
            result.replace('.', '', 1).isdigit() and
            float(result) >= 0 and
            float(result) <= float(total_price)
        ),
        filter=lambda result: float(result)
    ).execute()

    statut = inquirer.text(
        message="Entrez le statut du contrat :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    create_contract(
        db,
        user_id=user_id,
        token=token,
        client_id=client_id,
        commercial_contact_id=commercial_contact_id,
        total_price=total_price,
        remaining_price=remaining_price,
        statut=statut
    )
    console.print("\n[blue]Contrat créé avec succès ![/blue]\n")


def prompt_update_contract(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un contrat à mettre à jour et les modifications à apporter.
    """
    contracts = get_all_contracts(db)
    if not contracts:
        console.print("\n[blue]Aucun contrat disponible pour mise à jour.[/blue]\n")
        return

    contract_choices = [(f"{contract.id} - {contract.client.full_name}", contract.id) for contract in contracts]
    contract_choices.insert(0, ("Retour en arrière", None))

    selected_contract_text = inquirer.select(
        message="Sélectionnez un contrat à modifier :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()

    if selected_contract_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return
    
    contract_id = next((id for text, id in contract_choices if text == selected_contract_text), None)

    contract = get_contract_by_id(db, contract_id)
    if not contract:
        console.print("\n[blue]Contrat non trouvé.[/blue]\n")
        return

    total_price = inquirer.text(
        message=f"Prix total actuel : {contract.total_price}. Entrez le nouveau prix (laisser vide pour conserver) :",
    validate=lambda result: result.replace('.', '', 1).isdigit() and float(result) > 0 if result else True,
    filter=lambda result: float(result) if result else contract.total_price
    ).execute()

    remaining_price = inquirer.text(
        message=f"Prix restant actuel : {contract.remaining_price}. Entrez le nouveau prix restant (laisser vide pour conserver) :",
        validate=lambda result: (
            result.replace('.', '', 1).isdigit() and
            (float(result) <= float(total_price) if result else True)
        ),
        filter=lambda result: float(result) if result else contract.remaining_price
    ).execute()

    statut = inquirer.text(
        message=f"Statut actuel : {contract.statut}. Entrez le nouveau statut (laisser vide pour conserver) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    update_contract(
        db,
        user_id=user_id,
        token=token,
        contract_id=contract_id,
        total_price=total_price,
        remaining_price=remaining_price,
        statut=statut
    )
    console.print("\n[blue]Contrat mis à jour avec succès ![/blue]\n")


def prompt_delete_contract(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un contrat à supprimer.
    """
    contracts = get_all_contracts(db)
    if not contracts:
        console.print("\n[red]Aucun contrat disponible pour suppression.[/red]\n")
        return

    contract_choices = [(f"{contract.id} - {contract.client.full_name}", contract.id) for contract in contracts]
    contract_choices.insert(0, ("Retour en arrière", None))

    selected_contract_text = inquirer.select(
        message="Sélectionnez un contrat à supprimer :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()

    
    if selected_contract_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    contract_id = next((id for text, id in contract_choices if text == selected_contract_text), None)

    delete_contract(db, user_id, token, contract_id)
    console.print("\n[green]Contrat supprimé avec succès ![/green]\n")


def contract_menu(current_user_role, user_id, token):
    """
    Menu principal pour la gestion des contrats.
    """
    db: Session = SessionLocal()

    try:
        while True:
            # Obtenir les options de menu en fonction des permissions
            menu_options = []
            if can_perform_action(current_user_role, "get_all_contracts"):
                menu_options.append("Lister les contrats")
            if can_perform_action(current_user_role, "create_contract"):
                menu_options.append("Ajouter un contrat")
            if can_perform_action(current_user_role, "update_contract"):
                menu_options.append("Modifier un contrat")
            if can_perform_action(current_user_role, "delete_contract"):
                menu_options.append("Supprimer un contrat")

            menu_options.append("Retour au menu principal")

            choice = inquirer.select(
                message="Gestion des Contrats - Sélectionnez une action :",
                choices=menu_options
            ).execute()

            if choice == "Lister les contrats":
                display_contracts(db)
            elif choice == "Ajouter un contrat":
                prompt_create_contract(db, user_id, token)
            elif choice == "Modifier un contrat":
                prompt_update_contract(db, user_id, token)
            elif choice == "Supprimer un contrat":
                prompt_delete_contract(db, user_id, token)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()
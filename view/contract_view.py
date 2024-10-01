from sqlalchemy.orm import Session
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from config import SessionLocal
from controller.contract_controller import (
    get_all_contracts,
    create_contract,
    update_contract,
    delete_contract,
    get_contract_by_id,
)
from controller.client_controller import get_all_clients
from authentication.auth_service import can_perform_action
from controller.user_controller import get_commercials


console = Console()


STATUTS_CONTRAT = [
    "En négociation",
    "Signé",
    "En cours",
    "Terminé",
    "Annulé"
]


def display_contracts(db: Session, token: str, current_user_role: str):
    """
    Fonction pour afficher tous les contrats
    """
    contracts = get_all_contracts(db, token)
    if not contracts:
        console.print("\n[blue]Aucun contrat trouvé.[/blue]\n")
        return
    
    filter_choice = "Tous les contrats"

    if current_user_role == "commercial":
        filter_choice = inquirer.select(
            message="Souhaitez-vous appliquer un filtre ?",
            choices=["Tous les contrats", "Contrats signés", "Contrats payés intégralement"]
        ).execute()

        if filter_choice == "Contrats signés":
            contracts = [contract for contract in contracts if contract.statut == "Signé"]
        elif filter_choice == "Contrats payés intégralement":
            contracts = [contract for contract in contracts if contract.remaining_price == 0]

    if not contracts:
        console.print(f"\n[blue]Aucun contrat trouvé pour le filtre : {filter_choice}.[/blue]\n")
        return

    table = Table(title=f"\nListe des Contrats ({filter_choice})\n")
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Client", justify="center", style="blue")
    table.add_column("Commercial", justify="center", style="blue")
    table.add_column("Prix Total", justify="center", style="blue")
    table.add_column("Prix Restant", justify="center", style="blue")
    table.add_column("Statut", justify="center", style="blue")

    for contract in contracts:
        commercial_name = contract.commercial_contact.complete_name if contract.commercial_contact else "N/A"
        client_name = contract.client.full_name if contract.client else "N/A"

        table.add_row(
            str(contract.id),
            client_name,
            commercial_name,
            f"{contract.total_price:.2f} €",
            f"{contract.remaining_price:.2f} €",
            contract.statut
        )

    console.print("\n")
    console.print(table)
    console.print("\n")


def prompt_create_contract(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de saisir les
    informations pour créer un nouveau contrat.
    """
    clients = get_all_clients(db, token)
    commercials = get_commercials(db)

    if not clients:
        console.print(
            "\n[blue]Aucun client disponible pour créer un contrat.[/blue]\n"
            )
        return

    if not commercials:
        console.print(
            "\n[blue]Aucun commercial disponible pour créer un contrat.[/blue]\n"
            )
        return

    client_choices = [
        (f"{client.id} - {client.full_name}", client.id) for client in clients
        ]
    client_choices.insert(0, ("Retour en arrière", None))

    commercial_choices = [
        (f"{commercial.id} - {commercial.complete_name}", commercial.id)
        for commercial in commercials
        ]

    selected_client_text = inquirer.select(
        message="Sélectionnez un client :",
        choices=[choice for choice, _ in client_choices]
    ).execute()

    if selected_client_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    client_id = next(
        (id for text, id in client_choices
            if text == selected_client_text), None
        )

    commercial_contact_id = inquirer.select(
        message="Sélectionnez un commercial :",
        choices=[choice for choice, _ in commercial_choices]
    ).execute()

    commercial_contact_id = next(
        (id for text, id in commercial_choices
            if text == commercial_contact_id), None
        )

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

    statut = inquirer.select(
        message="Sélectionnez le statut du contrat :",
        choices=STATUTS_CONTRAT
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
    Demande à l'utilisateur de sélectionner un contrat
    à mettre à jour et les modifications à apporter.
    """
    contracts = get_all_contracts(db, token)
    if not contracts:
        console.print(
            "\n[blue]Aucun contrat disponible pour mise à jour.[/blue]\n"
            )
        return

    contract_choices = [
        (f"Contrat ID {contract.id} - {contract.client.full_name if contract.client else 'N/A'}", contract.id)
        for contract in contracts
        ]
    contract_choices.insert(0, ("Retour en arrière", None))

    selected_contract_text = inquirer.select(
        message="Sélectionnez un contrat à modifier :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()

    if selected_contract_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    contract_id = next(
        (id for text, id in contract_choices
            if text == selected_contract_text), None
        )

    contract = get_contract_by_id(db, contract_id)
    if not contract:
        console.print("\n[blue]Contrat non trouvé.[/blue]\n")
        return

    commercials = get_commercials(db)
    commercial_choices = [
        (f"{commercial.id} - {commercial.complete_name}", commercial.id)
        for commercial in commercials
    ]

    selected_commercial_text = inquirer.select(
        message="Sélectionnez un nouveau commercial (laisser vide pour conserver) :",
        choices=[
            f"Conserver le commercial actuel : "
            f"{contract.commercial_contact.complete_name if contract.commercial_contact else 'N/A'}"
        ] + [choice for choice, _ in commercial_choices]
    ).execute()

    if selected_commercial_text.startswith("Conserver"):
        commercial_contact_id = contract.commercial_contact.id if contract.commercial_contact else None
    else:
        commercial_contact_id = next(
            (id for text, id in commercial_choices if text == selected_commercial_text),
            None
        )

    total_price = inquirer.text(
        message=f"Prix total actuel : {contract.total_price}. "
                "Entrez le nouveau prix (laisser vide pour conserver) :",
        validate=lambda result: result.replace('.', '', 1).isdigit() and float(result) > 0
        if result else True,
        filter=lambda result: float(result) if result else contract.total_price
    ).execute()

    remaining_price = inquirer.text(
        message=f"Prix restant actuel : {contract.remaining_price}."
                f" Entrez le nouveau prix restant (laisser vide pour conserver) :",
        validate=lambda result: (
            result == "" or
            (result.replace('.', '', 1).isdigit() and
                float(result) <= float(total_price))
        ),
        filter=lambda result: float(result) if result else contract.remaining_price
    ).execute()

    statut = inquirer.select(
        message=f"Statut actuel : {contract.statut}. Sélectionnez le nouveau statut (laisser vide pour conserver) :",
        choices=STATUTS_CONTRAT
    ).execute()

    update_contract(
        db,
        user_id=user_id,
        token=token,
        contract_id=contract_id,
        total_price=total_price,
        remaining_price=remaining_price,
        statut=statut,
        commercial_contact_id=commercial_contact_id
    )
    console.print("\n[blue]Contrat mis à jour avec succès ![/blue]\n")


def prompt_delete_contract(db: Session, user_id: int, token: str):
    """
    Demande à l'utilisateur de sélectionner un contrat à supprimer.
    """
    contracts = get_all_contracts(db, token)
    if not contracts:
        console.print(
            "\n[red]Aucun contrat disponible pour suppression.[/red]\n"
            )
        return

    contract_choices = [
        (
            f"Contrat ID {contract.id} - {contract.client.full_name if contract.client else 'Client non spécifié'}",
            contract.id
        )
        for contract in contracts
    ]
    contract_choices.insert(0, ("Retour en arrière", None))

    selected_contract_text = inquirer.select(
        message="Sélectionnez un contrat à supprimer :",
        choices=[choice for choice, _ in contract_choices]
    ).execute()

    if selected_contract_text == "Retour en arrière":
        console.print("\n[blue]Retour en arrière.[/blue]\n")
        return

    contract_id = next(
        (id for text, id in contract_choices
            if text == selected_contract_text), None
        )

    confirmation = inquirer.confirm(
        message=f"Êtes-vous sûr de vouloir supprimer le contrat {contract_id} ?",
        default=False
    ).execute()

    if not confirmation:
        console.print("\n[blue]Suppression annulée, contrat non supprimé.[/blue]\n")
        return

    delete_contract(db, user_id, token, contract_id)
    console.print("\n[green]Contrat supprimé avec succès ![/green]\n")


def contract_menu(current_user_role, user_id, token):
    """
    Menu principal pour la gestion des contrats.
    """
    db: Session = SessionLocal()

    try:
        while True:
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
                display_contracts(db, token, current_user_role)
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

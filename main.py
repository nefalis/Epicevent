from sqlalchemy.orm import Session
from config import SessionLocal
from InquirerPy import inquirer
from rich.console import Console
from view.user_view import user_menu
from view.client_view import client_menu
from view.contract_view import contract_menu
from view.event_view import event_menu
from authentication.auth_service import (
    can_perform_action,
    get_current_user_department,
    login_user
    )
from authentication.auth_controller import authenticate_user
from authentication.auth_token import (
    load_token,
    delete_token,
    check_token_expiry
    )
from authentication.auth import login, logout
import sentry_sdk

sentry_sdk.init(
    dsn=(
        "https://7ca766726f13e2fedaf654f7d4401130@o4507843819405312.ingest"
        ".de.sentry.io/4507843832053840"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

console = Console()
current_user_department = None
current_user_id = None


def main_menu():
    """
    Menu principal pour choisir entre les différentes entités à gérer.
    """
    global current_user_department
    global current_user_id
    db: Session = SessionLocal()

    try:
        while True:
            console.print("\n")

            if current_user_department is None:
                choice = inquirer.select(
                    message="Choisissez une option:",
                    choices=[
                        "Connexion",
                        "Quitter"
                    ]
                ).execute()

                if choice == "Connexion":
                    employee_number = inquirer.text(
                        message="Numéro d'employé:"
                        ).execute()
                    password = inquirer.secret(
                        message="Mot de passe:"
                        ).execute()

                    user = authenticate_user(db, employee_number, password)

                    if user:
                        token = login_user(db, employee_number, password)

                        if token:
                            login(user)
                            token = load_token()
                            current_user_department = get_current_user_department(
                                user.id, db
                                )
                            global current_user_id
                            current_user_id = user.id

                            console.print(
                                f"\n [blue]Connexion réussie!"
                                f"Bienvenue {user.complete_name}.[/blue]"
                                )
                        else:
                            console.print(
                                "[red]Erreur lors de la création du jeton.[/red]"
                                )
                    else:
                        console.print(
                            "[red]Numéro d'employé ou mot de passe incorrect.[/red]"
                            )

                elif choice == "Quitter":
                    console.print("[red]Fermeture du programme...[/red]")
                    break

            else:
                # Vérifier si le jeton est expiré
                if token is None:
                    console.print(
                        "[red]Aucun jeton trouvé."
                        "Vous allez être déconnecté.[/red]"
                        )
                    delete_token()
                    logout()
                    current_user_department = None
                    current_user_id = None
                    continue

                if not check_token_expiry(token):
                    console.print(
                        "[red]Votre session a expiré."
                        "Vous allez être déconnecté.[/red]"
                        )
                    delete_token()
                    logout()
                    current_user_department = None
                    current_user_id = None
                    token = None
                    continue

                menu_options = []
                if can_perform_action(
                    current_user_department, "get_all_users"
                ):
                    menu_options.append("Utilisateur")

                if can_perform_action(
                    current_user_department, "get_all_contracts"
                ):
                    menu_options.append("Contrat")

                if can_perform_action(
                    current_user_department, "get_all_events"
                ):
                    menu_options.append("Événement")

                if can_perform_action(
                    current_user_department, "get_all_clients"
                ):
                    menu_options.append("Client")

                menu_options.append("Déconnexion")
                menu_options.append("Quitter")

                choice = inquirer.select(
                    message="Choisissez une option:",
                    choices=menu_options
                ).execute()

                try:
                    if choice == "Utilisateur" and can_perform_action(
                        current_user_department, "get_all_users"
                    ):
                        user_menu(current_user_department, current_user_id, token)

                    elif choice == "Contrat" and can_perform_action(
                        current_user_department, "get_all_contracts"
                    ):
                        contract_menu(current_user_department, current_user_id, token)

                    elif choice == "Événement" and can_perform_action(
                        current_user_department, "get_all_events"
                    ):
                        event_menu(current_user_department, current_user_id, token)

                    elif choice == "Client" and can_perform_action(
                        current_user_department, "get_all_clients"
                    ):
                        client_menu(current_user_department, current_user_id, token)

                    elif choice == "Déconnexion":
                        delete_token()
                        logout()
                        current_user_department = None
                        current_user_id = None
                        token = None
                        console.print("[yellow]Vous êtes déconnecté.[/yellow]")

                    elif choice == "Quitter":
                        console.print("[red]Fermeture du programme...[/red]")
                        break

                except PermissionError as e:
                    console.print(f"[red]{str(e)}[/red]")

    finally:
        db.close()


if __name__ == "__main__":
    main_menu()

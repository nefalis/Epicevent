from sqlalchemy.orm import Session
from config import SessionLocal
from InquirerPy import inquirer
from rich.console import Console
from view.user_view import user_menu
from view.client_view import client_menu
from view.contract_view import contract_menu
from view.event_view import event_menu
from authentication.auth_controller import authenticate_user
from authentication.auth import login, logout
from authentication.auth_service import can_perform_action,get_current_user_department
import sentry_sdk


sentry_sdk.init(
    dsn="https://7ca766726f13e2fedaf654f7d4401130@o4507843819405312.ingest.de.sentry.io/4507843832053840",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

console = Console()
current_user_department = None

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
                    employee_number = inquirer.text(message="Numéro d'employé:").execute()
                    password = inquirer.secret(message="Mot de passe:").execute()
                    user = authenticate_user(db, employee_number, password)
                    if user:
                        login(user)
                        current_user_department = get_current_user_department(user.id, db)
                        global current_user_id
                        current_user_id = user.id
                        console.print(f"\n [blue]Connexion réussie! Bienvenue {user.complete_name}.[/blue]")
                        console.print(f"debug main Rôle utilisateur : {current_user_department}")
                    else:
                        console.print("[red]Numéro d'employé ou mot de passe incorrect.[/red]")
                elif choice == "Quitter":
                    console.print("[red]Fermeture du programme...[/red]")
                    break
            else:
                # Obtenir les options de menu en fonction des permissions
                menu_options = []
                if can_perform_action(current_user_department, "get_all_users"):
                    menu_options.append("Utilisateur")
                if can_perform_action(current_user_department, "get_all_contracts"):
                    menu_options.append("Contrat")
                if can_perform_action(current_user_department, "get_all_events"):
                    menu_options.append("Événement")
                if can_perform_action(current_user_department, "get_all_clients"):
                    menu_options.append("Client")

                menu_options.append("Déconnexion")
                menu_options.append("Quitter")

                choice = inquirer.select(
                    message="Choisissez une option:",
                    choices=menu_options
                ).execute()

                if choice == "Utilisateur" and can_perform_action(current_user_department, "get_all_users"):
                    user_menu(current_user_department)
                elif choice == "Contrat" and can_perform_action(current_user_department, "get_all_contracts"):
                    contract_menu(current_user_department, current_user_id)
                elif choice == "Événement" and can_perform_action(current_user_department, "get_all_events"):
                    event_menu(current_user_department, current_user_id)
                elif choice == "Client" and can_perform_action(current_user_department, "get_all_clients"):
                    client_menu(current_user_department, current_user_id)
                elif choice == "Déconnexion":
                    logout()
                    current_user_department = None
                    current_user_id = None
                    console.print("[yellow]Vous êtes déconnecté.[/yellow]")
                elif choice == "Quitter":
                    console.print("[red]Fermeture du programme...[/red]")
                    break

    finally:
        db.close()


if __name__ == "__main__":
    main_menu()

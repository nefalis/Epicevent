from sqlalchemy.orm import Session
from config import SessionLocal
from InquirerPy import inquirer
from rich.console import Console
from view.user_view import user_menu
from view.client_view import client_menu
from view.contract_view import contract_menu
from view.event_view import event_menu
from authentication.auth_controller import authenticate_user
import authentication.auth as auth


console = Console()

def main_menu():
    """
    Menu principal pour choisir entre les différentes entités à gérer.
    """
    db: Session = SessionLocal()

    try:
        while True:
            console.print("\n")
            if not auth.is_authenticated():
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
                        auth.login(user)
                        console.print(f"[blue]Connexion réussie! Bienvenue {user.complete_name}.[/blue]")
                    else:
                        console.print("[red]Numéro d'employé ou mot de passe incorrect.[/red]")
                elif choice == "Quitter":
                    console.print("[red]Fermeture du programme...[/red]")
                    break
            else:
                choice = inquirer.select(
                    message="Choisissez un menu:",
                    choices=[
                        "Utilisateur",
                        "Contrat",
                        "Événement",
                        "Client",
                        "Déconnexion",
                        "Quitter"
                    ]
                ).execute()

                if choice == "Utilisateur":
                    user_menu()
                elif choice == "Contrat":
                    contract_menu(db)
                elif choice == "Événement":
                    event_menu(db)
                elif choice == "Client":
                    client_menu()
                elif choice == "Déconnexion":
                    auth.logout()
                    console.print("[yellow]Vous êtes déconnecté.[/yellow]")
                elif choice == "Quitter":
                    console.print("[red]Fermeture du programme...[/red]")
                    break

    finally:
        db.close()

if __name__ == "__main__":
    main_menu()
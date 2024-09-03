from sqlalchemy.orm import Session
from config import SessionLocal
from InquirerPy import inquirer
from rich.console import Console
from view.user_view import user_menu
from view.client_view import client_menu
from view.contract_view import contract_menu


console = Console()

def main_menu():
    """
    Menu principal pour choisir entre les différentes entités à gérer.
    """
    db: Session = SessionLocal()

    try:
        while True:
            console.print("\n")
            choice = inquirer.select(
                message="Choisissez un menu:",
                choices=[
                    "Utilisateur",
                    "Contrat",
                    "Événement",
                    "Client",
                    "Quitter"
                ]
            ).execute()

            if choice == "Utilisateur":
                user_menu(db)
            elif choice == "Contrat":
                contract_menu(db)
            elif choice == "Événement":
                console.print("[cyan]Menu Événement (en développement)[/cyan]")
            elif choice == "Client":
                client_menu(db)
            elif choice == "Quitter":
                console.print("[red]Fermeture du programme...[/red]")
                break

    finally:
        db.close()

if __name__ == "__main__":
    main_menu()
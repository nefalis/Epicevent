from sqlalchemy.orm import Session
from config import SessionLocal
from InquirerPy import inquirer
from rich.console import Console
from view.user_view import menu as user_menu


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
                user_menu()
            elif choice == "Contrat":
                console.print("[cyan]Menu Contrat (en développement)[/cyan]")
            elif choice == "Événement":
                console.print("[cyan]Menu Événement (en développement)[/cyan]")
            elif choice == "Client":
                console.print("[cyan]Menu Client (en développement)[/cyan]")
            elif choice == "Quitter":
                console.print("[red]Fermeture du programme...[/red]")
                break
            
    finally:
        db.close()

if __name__ == "__main__":
    main_menu()
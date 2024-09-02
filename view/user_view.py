from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
from sqlalchemy.orm import Session
from controller.user_controller import get_all_users, create_user, update_user, delete_user
from config import SessionLocal


console = Console()

def get_role_color(role):
    """
    Retourne une couleur spécifique pour chaque rôle d'utilisateur.
    """
    role_colors = {
        "management": "bold cyan",
        "commercial": "bold green",
        "support": "bold magenta"
    }
    return role_colors.get(role, "white")


def display_users(db: Session):
    """
    Fonction pour afficher tous les utilisateurs dans une table formatée.
    """
    users = get_all_users(db)
    table = Table(title="Liste des Utilisateurs")

    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Numéro Employé", style="blue")
    table.add_column("Nom Complet", style="blue")
    table.add_column("Email", style="blue")
    table.add_column("Rôle", style="blue")
    table.add_column("Date de Création", style="blue")

    for user in users:
        role_color = get_role_color(user.role)
        table.add_row(
            f"[{role_color}]{user.id}[/{role_color}]",
            f"[{role_color}]{user.employee_number}[/{role_color}]",
            f"[{role_color}]{user.complete_name}[/{role_color}]",
            f"[{role_color}]{user.email}[/{role_color}]",
            f"[{role_color}]{user.role}[/{role_color}]",
            f"[{role_color}]{user.creation_date}[/{role_color}]"
        )

    console.print("\n")
    console.print(table)
    console.print("\n")


def prompt_create_user(db: Session):
    """
    Fonction pour demander les informations de l'utilisateur pour la création.
    """
    employee_number = inquirer.text(
        message="Entrez le numéro d'employé:"
    ).execute()

    complete_name = inquirer.text(
        message="Entrez le nom complet:"
    ).execute()

    email = inquirer.text(
        message="Entrez l'email:"
    ).execute()

    password = inquirer.secret(
        message="Entrez le mot de passe:"
    ).execute()

    role = inquirer.select(
        message="Choisissez un rôle:",
        choices=["management", "commercial", "support"]
    ).execute()

    new_user = create_user(
        db,
        employee_number=employee_number,
        complete_name=complete_name,
        email=email,
        password=password,
        role=role
    )

    console.print(f"\n [blue]Nouvel utilisateur créé : Nom: {new_user.complete_name}, Numéro d'employé: {new_user.employee_number}, Email: {new_user.email}, Département: {new_user.role} \n")


def prompt_update_user(db: Session):
    user_id = int(inquirer.text(message="Entrez l'ID de l'utilisateur à modifier:").execute())
    complete_name = inquirer.text(message="Entrez le nouveau nom complet (laissez vide pour ne pas changer):").execute()
    email = inquirer.text(message="Entrez le nouvel email (laissez vide pour ne pas changer):").execute()
    password = inquirer.secret(message="Entrez le nouveau mot de passe (laissez vide pour ne pas changer):").execute()
    role = inquirer.select(message="Choisissez le nouveau rôle:", choices=["management", "commercial", "support", "Ne pas changer"]).execute()

    role = None if role == "Ne pas changer" else role

    updated_user = update_user(db, user_id, complete_name, email, password, role)
    if updated_user:
        console.print(f"\n [blue]Nouvel utilisateur créé : Nom: {updated_user.complete_name}, Numéro d'employé: {updated_user.employee_number}, Email: {updated_user.email}, Département: {updated_user.role} \n")
    else:
        console.print("\n [blue]Utilisateur non trouvé.[/blue] \n")

def prompt_delete_user(db: Session):
    user_id = int(inquirer.text(message="Entrez l'ID de l'utilisateur à supprimer:").execute())
    user = delete_user(db, user_id)
    if user:
        console.print(f"\n [blue]Utilisateur supprimé :[/blue] {user.id}, [blue]Nom:[/blue] {user.complete_name} \n")
    else:
        console.print("\n [blue]Utilisateur non trouvé.[/blue] \n")

def menu():
    db: Session = SessionLocal()

    try:
        while True:
            choice = inquirer.select(
                message="Choisissez une option:",
                choices=[
                    "Afficher tous les utilisateurs",
                    "Créer un nouvel utilisateur",
                    "Modifier un utilisateur",
                    "Supprimer un utilisateur",
                    "Quitter"
                ]
            ).execute()

            if choice == "Afficher tous les utilisateurs":
                display_users(db)
            elif choice == "Créer un nouvel utilisateur":
                prompt_create_user(db)
            elif choice == "Modifier un utilisateur":
                prompt_update_user(db)
            elif choice == "Supprimer un utilisateur":
                prompt_delete_user(db)
            elif choice == "Quitter":
                console.print("[red]Fermeture du programme...[/red]")
                break
    finally:
        db.close()
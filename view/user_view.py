from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from InquirerPy import inquirer
from sqlalchemy.orm import Session
from controller.user_controller import get_all_users, create_user, update_user, delete_user
from config import SessionLocal
from authentication.auth_service import can_perform_action
from view.validation import validate_email, validate_employee_number, validate_password, validate_text


console = Console()

def get_depatment_color(department_name):
    """
    Retourne une couleur spécifique pour chaque rôle d'utilisateur.
    """
    role_colors = {
        "gestion": "bold cyan",
        "commercial": "bold green",
        "support": "bold magenta"
    }
    return role_colors.get(department_name, "white")


def display_users(db: Session):
    """
    Fonction pour afficher tous les utilisateurs.
    """
    users = get_all_users(db)
    table = Table(title="Liste des Utilisateurs", border_style="cyan", title_style="bold yellow",
        show_footer=True)

    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Numéro Employé", style="blue")
    table.add_column("Nom Complet", style="blue")
    table.add_column("Email", style="blue")
    table.add_column("Département", style="blue")
    table.add_column("Date de Création", style="blue")

    for user in users:
        department_name = user.department.name if user.department else "Inconnu"
        department_color = get_depatment_color(department_name) if user.department else "white"
        table.add_row(
            f"[{department_color }]{user.id}[/{department_color }]",
            f"[{department_color }]{user.employee_number}[/{department_color }]",
            f"[{department_color }]{user.complete_name}[/{department_color }]",
            f"[{department_color }]{user.email}[/{department_color }]",
            f"[{department_color }]{department_name}[/{department_color }]",
            f"[{department_color }]{user.creation_date}[/{department_color }]"
        )

    console.print(table)
    console.print("\n")


def prompt_create_user(db: Session):
    """
    Fonction pour demander les informations de l'utilisateur pour la création.
    """

    start_creation = inquirer.select(
        message="Souhaitez-vous créer un nouvel utilisateur ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_creation == "Retour en arrière":
        console.print("\n[blue]Création annulée, retour en arrière.[/blue]\n")
        return
    
    employee_number = inquirer.text(
        message="Entrez le numéro d'employé (2 lettres suivies de 4 chiffres) :",
        validate=lambda result: validate_employee_number(result),
        invalid_message="Le numéro d'employé doit être composé de 2 lettres suivies de 4 chiffres (ex: AB1234)."
    ).execute()

    complete_name = inquirer.text(
        message="Entrez le nom complet :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    email = inquirer.text(
        message="Entrez l'email :",
        validate=lambda result: validate_email(result),
        invalid_message="Veuillez entrer un email valide (exemple: utilisateur@domaine.com)."
    ).execute()

    password = inquirer.secret(
        message="Entrez le mot de passe :",
        validate=lambda result: validate_password(result),
        invalid_message="Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre."
    ).execute()

    department_name = inquirer.select(
        message="Choisissez un département:",
        choices=["gestion", "commercial", "support"]
    ).execute()

    new_user = create_user(
        db,
        employee_number=employee_number,
        complete_name=complete_name,
        email=email,
        password=password,
        department_name=department_name
    )

    console.print(f"\n [green]Nouvel utilisateur créé :[/green] Nom: {new_user.complete_name}, Numéro d'employé: {new_user.employee_number}, Email: {new_user.email}, Département: {department_name} \n")


def prompt_update_user(db: Session):
    """
    Fonction pour demander les informations pour mettre à jour un utilisateur avec possibilité de retour en arrière.
    """

    start_update = inquirer.select(
        message="Souhaitez-vous mettre à jour un utilisateur ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_update == "Retour en arrière":
        console.print("\n[blue]Mise à jour annulée, retour en arrière.[/blue]\n")
        return

    # Récupérer tous les utilisateurs
    users = get_all_users(db)
    if not users:
        console.print("\n[red]Aucun utilisateur trouvé.[/red]\n")
        return

    # Créer une liste de choix avec les noms et IDs des utilisateurs
    user_choices = [f"{user.complete_name} (ID: {user.id})" for user in users]
    selected_user = inquirer.select(
        message="Sélectionnez l'utilisateur à modifier :",
        choices=user_choices
    ).execute()

    # Extraire l'ID de l'utilisateur sélectionné
    user_id = int(selected_user.split("(ID: ")[1].split(")")[0])

    complete_name = inquirer.text(
        message="Entrez le nouveau nom complet (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()

    email = inquirer.text(
        message="Entrez le nouvel email (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_email(result) if result else True,
        invalid_message="Veuillez entrer un email valide (exemple : utilisateur@domaine.com)."
    ).execute()

    password = inquirer.secret(
        message="Entrez le nouveau mot de passe (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_password(result) if result else True,
        invalid_message="Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre."
    ).execute()

    department_name = inquirer.select(message="Choisissez le nouveau département:", choices=["gestion", "commercial", "support", "Ne pas changer"]).execute()

    department_name = None if department_name == "Ne pas changer" else department_name

    updated_user = update_user(db, user_id, complete_name, email, password, department_name)
    if updated_user:
        console.print(f"\n [green] Utilisateur modifié : Nom: {updated_user.complete_name}, Numéro d'employé: {updated_user.employee_number}, Email: {updated_user.email} [/green]\n")
    else:
        console.print("\n [blue]Utilisateur non trouvé.[/blue] \n")


def prompt_delete_user(db: Session):
    """
    Fonction pour demander la suppression d'un utilisateur avec possibilité de retour en arrière.
    """

    start_deletion = inquirer.select(
        message="Souhaitez-vous supprimer un utilisateur ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_deletion == "Retour en arrière":
        console.print("\n[blue]Suppression annulée, retour en arrière.[/blue]\n")
        return
    
    # Récupérer tous les utilisateurs
    users = get_all_users(db)
    if not users:
        console.print("\n[red]Aucun utilisateur trouvé.[/red]\n")
        return
    
    # Créer une liste de choix avec les noms et IDs des utilisateurs
    user_choices = [f"{user.complete_name} (ID: {user.id})" for user in users]
    selected_user = inquirer.select(
        message="Sélectionnez l'utilisateur à supprimer :",
        choices=user_choices
    ).execute()

    # Extraire l'ID de l'utilisateur sélectionné
    user_id = int(selected_user.split("(ID: ")[1].split(")")[0])

    user = delete_user(db, user_id)
    if user:
        console.print(f"\n [green]Utilisateur supprimé :[/green] ID: {user.id}, Nom: {user.complete_name} \n")
    else:
        console.print("\n [blue]Utilisateur non trouvé.[/blue] \n")


def user_menu(current_user_role):
    """
    Menu principal pour la gestion des utilisateurs.
    """
    db: Session = SessionLocal()

    try:
        while True:
            # Obtenir les options de menu en fonction des permissions
            menu_options = []
            if can_perform_action(current_user_role, "get_all_users"):
                menu_options.append("Afficher tous les utilisateurs")
            if can_perform_action(current_user_role, "create_user"):
                menu_options.append("Créer un nouvel utilisateur")
            if can_perform_action(current_user_role, "update_user"):
                menu_options.append("Modifier un utilisateur")
            if can_perform_action(current_user_role, "delete_user"):
                menu_options.append("Supprimer un utilisateur")

            menu_options.append("Retour au menu principal")

            choice = inquirer.select(
                message="Choisissez une option:",
                choices=menu_options
            ).execute()

            if choice == "Afficher tous les utilisateurs":
                display_users(db)
            elif choice == "Créer un nouvel utilisateur":
                prompt_create_user(db)
            elif choice == "Modifier un utilisateur":
                prompt_update_user(db)
            elif choice == "Supprimer un utilisateur":
                prompt_delete_user(db)
            elif choice == "Retour au menu principal":
                break
    finally:
        db.close()
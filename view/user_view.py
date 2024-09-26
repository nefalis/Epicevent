from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
from sqlalchemy.orm import Session
from controller.user_controller import (
    get_all_users,
    create_user,
    update_user,
    delete_user
    )
from config import SessionLocal
from authentication.auth_service import can_perform_action
from view.validation import (
    validate_email,
    validate_employee_number,
    validate_password,
    validate_text
    )


console = Console()


def get_department_color(department_name):
    """
    Retourne une couleur spécifique pour chaque rôle d'utilisateur.
    """
    role_colors = {
        "gestion": "bold cyan",
        "commercial": "bold green",
        "support": "bold magenta"
    }
    return role_colors.get(department_name, "white")


def display_users(db: Session, token: str):
    """
    Fonction pour afficher tous les utilisateurs.
    """
    users = get_all_users(db, token)
    console.print("\n")
    table = Table(title="Liste des Utilisateurs", border_style="cyan", title_style="cyan")

    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Numéro Employé", style="blue")
    table.add_column("Nom Complet", style="blue")
    table.add_column("Email", style="blue")
    table.add_column("Département", style="blue")
    table.add_column("Date de Création", style="blue")

    for user in users:
        department_name = user.department.name if user.department else "Inconnu"
        department_color = get_department_color(department_name) if user.department else "white"
        table.add_row(
            f"[{department_color}] {user.id}[/{department_color}]",
            f"[{department_color}] {user.employee_number}[/{department_color}]",
            f"[{department_color}] {user.complete_name}[/{department_color}]",
            f"[{department_color}] {user.email}[/{department_color}]",
            f"[{department_color}] {department_name}[/{department_color}]",
            f"[{department_color}] {user.creation_date}[/{department_color}]"
        )

    console.print(table)
    console.print("\n")


def prompt_create_user(db: Session, user_id: int, token: str):
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
        invalid_message="Le numéro d'employé doit être"
        "composé de 2 lettres suivies de 4 chiffres (ex: AB1234)."
    ).execute()

    complete_name = inquirer.text(
        message="Entrez le nom complet :",
        validate=lambda result: validate_text(result),
        invalid_message="Le nom doit contenir uniquement"
        "des lettres, espaces ou tiret."
    ).execute()

    email = inquirer.text(
        message="Entrez l'email :",
        validate=lambda result: validate_email(result),
        invalid_message="Veuillez entrer un email valide (exemple: utilisateur@domaine.com)."
    ).execute()

    password = inquirer.secret(
        message="Entrez le mot de passe :",
        validate=lambda result: validate_password(result),
        invalid_message="Le mot de passe doit contenir au moins 8 caractères,"
        "une majuscule, une minuscule et un chiffre."
    ).execute()

    department_name = inquirer.select(
        message="Choisissez un département:",
        choices=["gestion", "commercial", "support"]
    ).execute()

    new_user = create_user(
        db,
        user_id=user_id,
        employee_number=employee_number,
        complete_name=complete_name,
        email=email,
        password=password,
        department_name=department_name,
        token=token
    )

    console.print(
        f"\n[green]Nouvel utilisateur créé :[/green]\n"
        f"Nom: {new_user.complete_name},\n"
        f"Numéro d'employé: {new_user.employee_number},\n"
        f"Email: {new_user.email},\n"
        f"Département: {department_name}\n"
    )


def prompt_update_user(db: Session, user_id: int, token: str):
    """
    Fonction pour demander les informations pour
    mettre à jour un utilisateur avec possibilité de retour en arrière.
    """

    console.print(f"debug l139 update user {user_id}")
    start_update = inquirer.select(
        message="Souhaitez-vous mettre à jour un utilisateur ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_update == "Retour en arrière":
        console.print("\n[blue]Mise à jour annulée, retour en arrière.[/blue]\n")
        return

    users = get_all_users(db, token)
    if not users:
        console.print("\n[red]Aucun utilisateur trouvé.[/red]\n")
        return
    console.print(f"debug l153 update user {user_id}")
    user_choices = [f"{user.complete_name} (ID: {user.id})" for user in users]
    selected_user = inquirer.select(
        message="Sélectionnez l'utilisateur à modifier :",
        choices=user_choices
    ).execute()

    selected_user_id = int(selected_user.split("(ID: ")[1].split(")")[0])
    console.print(f"debug l161 update user {user_id}")
    complete_name = inquirer.text(
        message="Entrez le nouveau nom complet (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_text(result) if result else True,
        invalid_message="Le nom doit contenir uniquement des lettres, espaces ou tiret."
    ).execute()
    console.print(f"debug l167 update user {user_id}")
    email = inquirer.text(
        message="Entrez le nouvel email (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_email(result) if result else True,
        invalid_message="Veuillez entrer un email valide (exemple : utilisateur@domaine.com)."
    ).execute()
    console.print(f"debug l174 update user {user_id}")
    password = inquirer.secret(
        message="Entrez le nouveau mot de passe (laissez vide pour ne pas changer) :",
        validate=lambda result: validate_password(result) if result else True,
        invalid_message="Le mot de passe doit contenir au moins 8 caractères,"
                        "une majuscule, une minuscule et un chiffre."
    ).execute()
    console.print(f"debug l182 update user {user_id}")
    department_name = inquirer.select(
        message="Choisissez le nouveau département:",
        choices=["gestion", "commercial", "support", "Ne pas changer"]).execute()

    console.print(f"debug l187 update user {user_id}")

    department_name = None if department_name == "Ne pas changer" else department_name

    updated_user = update_user(
        db, selected_user_id, token, complete_name, email, password, department_name
        )
    console.print(f"debug l192 update user {user_id}")
    if updated_user:
        console.print(
            f"\n [green] Utilisateur modifié : Nom: {updated_user.complete_name},"
            f"Numéro d'employé: {updated_user.employee_number},"
            f"Email: {updated_user.email} [/green]\n"
            )
    else:
        console.print("\n [blue]Utilisateur non trouvé.[/blue] \n")


def prompt_delete_user(db: Session, token: str):
    """
    Fonction pour demander la suppression d'un utilisateur
    avec possibilité de retour en arrière.
    """
    start_deletion = inquirer.select(
        message="Souhaitez-vous supprimer un utilisateur ?",
        choices=["Oui", "Retour en arrière"]
    ).execute()

    if start_deletion == "Retour en arrière":
        console.print("\n[blue]Suppression annulée, retour en arrière.[/blue]\n")
        return

    users = get_all_users(db, token)
    if not users:
        console.print("\n[red]Aucun utilisateur trouvé.[/red]\n")
        return

    # Créer une liste de choix avec les noms et IDs des utilisateurs
    user_choices = [f"{user.complete_name} (ID: {user.id})" for user in users]
    user_choices.insert(0, "Retour en arrière")
    selected_user = inquirer.select(
        message="Sélectionnez l'utilisateur à supprimer :",
        choices=user_choices
    ).execute()

    if selected_user == "Retour en arrière":
        console.print("\n[blue]Suppression annulée, retour au menu précédent.[/blue]\n")
        return

    # Extraire l'ID de l'utilisateur sélectionné
    user_id = int(selected_user.split("(ID: ")[1].split(")")[0])

    confirmation = inquirer.confirm(
        message=f"Êtes-vous sûr de vouloir supprimer l'utilisateur {selected_user} ?",
        default=False
    ).execute()

    if not confirmation:
        console.print("\n[blue]Suppression annulée, utilisateur non supprimé.[/blue]\n")
        return

    # Supprimer l'utilisateur après confirmation
    user = delete_user(db, user_id, token=token)
    if user:
        console.print(
            f"\n [green]Utilisateur supprimé :[/green] "
            f"ID: {user.id}, Nom: {user.complete_name} \n"
        )
    else:
        console.print("\n [blue]Utilisateur non trouvé.[/blue] \n")


def user_menu(current_user_role, user_id, token):
    """
    Menu principal pour la gestion des utilisateurs.
    """
    db: Session = SessionLocal()

    try:
        while True:
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

            try:
                if choice == "Afficher tous les utilisateurs":
                    display_users(db, token)
                elif choice == "Créer un nouvel utilisateur":
                    prompt_create_user(db, user_id, token)
                elif choice == "Modifier un utilisateur":
                    prompt_update_user(db, user_id, token)
                elif choice == "Supprimer un utilisateur":
                    prompt_delete_user(db, token)
                elif choice == "Retour au menu principal":
                    break
            except PermissionError as e:
                console.print(f"[red]{str(e)}[/red]")
                break
            except Exception as e:
                console.print(f"[red]Erreur: {str(e)}[/red]")

    finally:
        db.close()

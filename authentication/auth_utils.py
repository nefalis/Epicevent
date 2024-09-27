from functools import wraps
import sentry_sdk
from jwt import ExpiredSignatureError
from authentication.auth_service import (
    get_current_user_role,
    can_perform_action
    )
from rich.console import Console


console = Console()


def requires_permission(action):
    """
    Décorateur pour vérifier les permissions de
    l'utilisateur avant d'exécuter une fonction.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(db, user_id, token, *args, **kwargs):
            user_role = get_current_user_role(user_id, db, token)
            if not can_perform_action(user_role, action):
                raise PermissionError("Action non autorisée.")
            return func(db, user_id, token, *args, **kwargs)
        return wrapper
    return decorator


def handle_errors(func):
    """
    Décorateur pour gérer les exceptions courantes
    et fournir des messages d'erreur cohérents.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError as pe:
            console.print(f"[red]Erreur de permission : {str(pe)}[/red]")
            raise PermissionError(str(pe))
        except ValueError as ve:
            console.print(f"[yellow]Erreur de validation : {str(ve)}[/yellow]")
            raise ValueError(str(ve))
        except ExpiredSignatureError:
            console.print(
                "[red]Jeton expiré. Veuillez vous reconnecter.[/red]"
                )
            raise PermissionError("Jeton expiré. Veuillez vous reconnecter.")
        except Exception as e:
            console.print(f"[red]Erreur inattendue : {str(e)}[/red]")
            sentry_sdk.capture_exception(e)
            raise Exception(f"Erreur inattendue : {str(e)}")
    return wrapper

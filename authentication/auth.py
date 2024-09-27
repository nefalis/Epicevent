current_user = None


def is_authenticated():
    """Vérifie si un utilisateur est authentifié."""
    return current_user is not None


def login(user):
    """Authentifie un utilisateur en stockant ses informations dans current_user."""
    global current_user
    current_user = user


def logout():
    """Déconnexion de l'utilisateur actuel en réinitialisant current_user à None."""
    global current_user
    current_user = None


def get_current_user():
    """Récupère les informations de l'utilisateur actuellement authentifié."""
    return current_user

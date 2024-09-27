import pytest
from datetime import timedelta
from authentication.auth_token import (
    create_jwt_token, verify_jwt_token, check_token_expiry
)
from config import SECRET_KEY_TOKEN, ALGORITHM


def test_expired_token():
    """
    Test pour un token expiré.
    """
    # Crée un token déjà expiré
    expired_token = create_jwt_token(
        user_id=1,
        secret_key=SECRET_KEY_TOKEN,
        algorithm=ALGORITHM,
        expires_delta=timedelta(seconds=-10)
    )

    assert not check_token_expiry(expired_token)


def test_modified_token():
    """
    Test pour un token modifié.
    """
    valid_token = create_jwt_token(
        user_id=1,
        secret_key=SECRET_KEY_TOKEN,
        algorithm=ALGORITHM,
        expires_delta=timedelta(minutes=5)
    )

    # Modifie le token en y ajoutant des données pour provoquer une erreur
    modified_token = valid_token + 'extra-part'

    # Vérifie qu'une exception est levée pour un token modifié
    with pytest.raises(PermissionError) as exc_info:
        verify_jwt_token(modified_token, SECRET_KEY_TOKEN, ALGORITHM)

    assert str(exc_info.value) == "Erreur lors de la vérification du jeton."


def test_token_length():
    """
    Test pour vérifier que le token a le bon nombre de caractères.
    """
    valid_token = create_jwt_token(
        user_id=1,
        secret_key=SECRET_KEY_TOKEN,
        algorithm=ALGORITHM,
        expires_delta=timedelta(minutes=5)
    )

    token_parts = valid_token.split('.')

    # Vérifie que le token contient bien 3 parties
    assert len(token_parts) == 3, "Le token JWT ne contient pas 3 parties"

    # Vérifie que chaque partie du token n'est pas vide
    for part in token_parts:
        assert len(part) > 0, "Une partie du token est vide"

    # Vérifie que le token a une longueur minimale
    assert len(valid_token) > 100, "Le token est trop court pour être valide"

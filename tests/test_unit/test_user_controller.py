from unittest import mock
from controller.user_controller import get_all_users, create_user, update_user
from model.user_model import User, Department

def test_get_all_users():
    mock_session = mock.MagicMock()

    # Création d'exemples d'utilisateurs avec leurs départements
    department_gestion = Department(id=1, name="gestion")
    department_commercial = Department(id=2, name="commercial")
    user1 = User(id=1, complete_name="John Doe", department=department_gestion)
    user2 = User(id=2, complete_name="Jane Smith", department=department_commercial)

    # Simuler la réponse de la requête
    mock_session.query().join().filter().all.return_value = [user1, user2]

    # Exécution de la fonction à tester
    users = get_all_users(mock_session)

    # Vérification que la liste d'utilisateurs contient bien les deux utilisateurs simulés
    assert len(users) == 2
    assert users[0].complete_name == "John Doe"
    assert users[1].complete_name == "Jane Smith"


def test_create_user():
    mock_session = mock.MagicMock()

    # Simuler le département dans la base de données
    department_gestion = Department(id=1, name="gestion")
    mock_session.query().filter().first.return_value = department_gestion

    # Simuler la création de l'utilisateur
    employee_number = "ma8466"
    complete_name = "Bob Eponge"
    email = "bob@example.com"
    password = "Fr45451232d"
    department_name = "gestion"

    # Exécution de la fonction à tester
    new_user = create_user(mock_session, employee_number, complete_name, email, password, department_name)

    # Vérification que l'utilisateur est bien ajouté à la session
    mock_session.add.assert_called_once_with(new_user)
    # Vérification que les changements ont bien été commités
    mock_session.commit.assert_called_once()


def test_update_user():
    # Mock de la session SQLAlchemy
    mock_session = mock.MagicMock()

    # Simuler un utilisateur existant
    user = User(id=1, complete_name="Boby Eponge", email="bobyeponge@example.com")
    mock_session.query().filter().first.return_value = user

    # Exécution de la fonction à tester
    updated_user = update_user(mock_session, 1, complete_name="Boby Eponge", email="bobyeponge@example.com")

    # Vérification que l'utilisateur est bien mis à jour
    assert updated_user.complete_name == "Boby Eponge"
    assert updated_user.email == "bobyeponge@example.com"
    
    # Vérification que les changements ont bien été commités
    mock_session.commit.assert_called_once()

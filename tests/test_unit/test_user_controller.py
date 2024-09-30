from unittest import mock
from controller.user_controller import (
    create_user,
    update_user,
    delete_user
    )
from model.user_model import User, Department


@mock.patch("sqlalchemy.orm.Session")
@mock.patch("authentication.auth_utils.get_current_user_role")
@mock.patch(
    "authentication.auth_utils.can_perform_action",
    return_value=True
    )
def test_create_user(
    mock_can_perform_action, mock_get_current_user_role, mock_session
):
    """Test pour la création d'un utilisateur"""
    mock_db = mock.Mock()
    mock_get_current_user_role.return_value = "manager"

    mock_session.return_value = mock_db

    department = Department(name='gestion', id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = (
        department
    )

    user = create_user(
        db=mock_db,
        user_id=1,
        token="fake_token",
        employee_number="AB1234",
        complete_name="Test User",
        email="test@example.com",
        password="Password1",
        department_name="gestion"
    )

    assert isinstance(user, User)
    assert user.complete_name == "Test User"
    assert user.email == "test@example.com"
    assert user.department_id == department.id

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@mock.patch("sqlalchemy.orm.Session")
@mock.patch("authentication.auth_utils.get_current_user_role")
@mock.patch(
    "authentication.auth_utils.can_perform_action", return_value=True
    )
def test_update_user(
    mock_can_perform_action, mock_get_current_user_role, mock_session
):
    """Test pour la modification d'un utilisateur."""
    mock_db = mock.Mock()
    mock_get_current_user_role.return_value = "manager"
    mock_session.return_value = mock_db

    user = User(id=1, complete_name="Old Name", email="old@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = user

    updated_user = update_user(
        db=mock_db,
        user_id=1,
        token="fake_token",
        complete_name="New Name",
        email="new@example.com",
        password=None,
        department_name=None,
        selected_user_id=user.id
    )
    assert updated_user.complete_name == "New Name"
    assert updated_user.email == "new@example.com"
    mock_db.commit.assert_called_once()


@mock.patch("sqlalchemy.orm.Session")
@mock.patch("authentication.auth_utils.get_current_user_role")
@mock.patch(
    "authentication.auth_utils.can_perform_action", return_value=True
    )
def test_delete_user(
    mock_can_perform_action, mock_get_current_user_role, mock_session
):
    """Test pour supprimer un utilisateur."""
    mock_db = mock.Mock()
    mock_get_current_user_role.return_value = "manager"
    mock_session.return_value = mock_db

    user = User(id=1, complete_name="Test User", email="test@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = user

    deleted_user = delete_user(
        db=mock_db,
        user_id=1,
        selected_user_id=user.id,
        token="fake_token"
    )

    assert deleted_user.complete_name == "Test User"
    mock_db.delete.assert_called_once_with(user)
    mock_db.commit.assert_called_once()

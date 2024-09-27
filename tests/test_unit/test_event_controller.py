from unittest import mock
from datetime import datetime
from controller.event_controller import create_event


@mock.patch("sqlalchemy.orm.Session")
@mock.patch("authentication.auth_utils.get_current_user_role")
@mock.patch("authentication.auth_utils.can_perform_action")
def test_create_event(
    mock_can_perform_action, mock_get_current_user_role, mock_session
):
    """Test pour la création d'un événement."""
    mock_db = mock.Mock()

    mock_get_current_user_role.return_value = "manager"
    mock_can_perform_action.return_value = True
    mock_session.return_value = mock_db

    event_name = "Test Event"
    client_name = "Client Test"
    location = "Paris"

    event = create_event(
        db=mock_db,
        user_id=10,
        token="fake_token",
        event_name=event_name,
        contract_id=1,
        client_id=1,
        client_name=client_name,
        client_contact="test@test.com",
        date_start=datetime(2024, 9, 20, 10, 0),
        date_end=datetime(2024, 9, 20, 12, 0),
        support_contact_id=1,
        location=location,
        attendees=100,
        notes="Ceci est un test."
    )

    assert event.event_name == event_name
    assert event.client_name == client_name
    assert event.location == location

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

from unittest import mock
from controller.event_controller import get_all_events, create_event
from model.event_model import Event
from datetime import datetime

def test_get_all_events():
    mock_session = mock.MagicMock()

    # Créer des exemples d'événements
    event1 = Event(id=1, event_name="Event 1")
    event2 = Event(id=2, event_name="Event 2")

    # Simuler la réponse de la requête
    mock_session.query().all.return_value = [event1, event2]

    # Appel de la fonction à tester
    events = get_all_events(mock_session)

    # Vérifications
    assert len(events) == 2
    assert events[0].event_name == "Event 1"
    assert events[1].event_name == "Event 2"


def test_create_event():
    mock_session = mock.MagicMock()

    # Simuler la fonction `get_current_user_role` et `can_perform_action`
    with mock.patch('controller.event_controller.get_current_user_role', return_value='admin'):
        with mock.patch('controller.event_controller.can_perform_action', return_value=True):
            
            # Données de test
            event_data = {
                "event_name": "Test Event",
                "contract_id": 1,
                "client_id": 2,
                "client_name": "Test Client",
                "client_contact": "Test Contact",
                "date_start": datetime(2024, 9, 15, 10, 0),
                "date_end": datetime(2024, 9, 15, 12, 0),
                "support_contact_id": 5,
                "location": "Test Location",
                "attendees": 50,
                "notes": "Test Notes"
            }

            # Appel de la fonction à tester
            new_event = create_event(mock_session, 10, **event_data)

            # Vérifications
            mock_session.add.assert_called_once_with(new_event)
            mock_session.commit.assert_called_once()
            assert isinstance(new_event, Event)
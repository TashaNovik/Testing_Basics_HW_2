import pytest
from app import crud, db, models
import uuid


# --- Tests for crud.get_user_by_email() ---

def test_get_user_by_email_positive_found(sample_users_data):
    """Позитивный: пользователь найден."""

    email_to_find = "testuser@example.com"
    user = crud.get_user_by_email(email_to_find)
    assert user is not None
    assert user["email"] == email_to_find
    assert user["id"] == sample_users_data[email_to_find]["id"]


def test_get_user_by_email_positive_another_found(sample_users_data):
    """Позитивный: другой пользователь найден."""

    email_to_find = "anotheruser@example.com"
    user = crud.get_user_by_email(email_to_find)
    assert user is not None
    assert user["email"] == email_to_find

def test_get_user_by_email_negative_not_found(sample_users_data):
    """Негативный: пользователь не найден."""

    user = crud.get_user_by_email("nonexistent@example.com")
    assert user is None

def test_get_user_by_email_negative_empty_db():
    """Негативный: база данных пользователей пуста."""

    user = crud.get_user_by_email("any@example.com")
    assert user is None

# --- Tests for crud.create_session() ---

def test_create_session_positive_generates_and_stores(mocker, sample_users_data):
    """Позитивный: сессия успешно создана и сохранена."""

    mock_uuid = mocker.patch('app.crud.uuid.uuid4')
    test_uuid_str = "12345678-1234-5678-1234-567812345678"
    mock_uuid.return_value = uuid.UUID(test_uuid_str)
    email = "testuser@example.com"
    session_id = crud.create_session(email)
    assert session_id == test_uuid_str
    assert db.sessions_db[test_uuid_str] == email
    mock_uuid.assert_called_once()


def test_create_session_positive_uniqueness(mocker, sample_users_data):
    """Позитивный: сессии уникальны при повторных вызовах."""

    mock_uuid_gen = mocker.patch('app.crud.uuid.uuid4')
    uuid1_str = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    uuid2_str = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    mock_uuid_gen.side_effect = [uuid.UUID(uuid1_str), uuid.UUID(uuid2_str)]
    email = "testuser@example.com"
    session_id1 = crud.create_session(email)
    session_id2 = crud.create_session(email)  # Для того же пользователя
    assert session_id1 == uuid1_str
    assert session_id2 == uuid2_str
    assert session_id1 != session_id2
    assert db.sessions_db[uuid1_str] == email
    assert db.sessions_db[uuid2_str] == email
    assert mock_uuid_gen.call_count == 2


@pytest.mark.parametrize("invalid_email", ["", "notanemail", "user@", "@domain.com"])
def test_create_session_negative_invalid_email_input(invalid_email, mocker):
    """ Негативный: поведение с невалидным email. """

    mock_uuid = mocker.patch('app.crud.uuid.uuid4')
    test_uuid_str = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
    mock_uuid.return_value = uuid.UUID(test_uuid_str)
    session_id = crud.create_session(invalid_email)
    assert session_id == test_uuid_str
    assert db.sessions_db[test_uuid_str] == invalid_email



def test_create_session_negative_empty_email_input(mocker):
    """Негативный: пустой email (как частный случай невалидного)."""

    mock_uuid = mocker.patch('app.crud.uuid.uuid4')
    test_uuid_str = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    mock_uuid.return_value = uuid.UUID(test_uuid_str)
    session_id = crud.create_session("")
    assert session_id == test_uuid_str
    assert db.sessions_db[test_uuid_str] == ""

# --- Tests for crud.get_events ---

def test_get_events_positive_no_filters(sample_events_data):
    """Позитивный: без фильтров, возвращает все события."""

    events = crud.get_events()
    assert len(events) == len(sample_events_data)
    event_ids_from_db = sorted(sample_events_data.keys())
    returned_event_ids = sorted([event.id for event in events])
    assert returned_event_ids == event_ids_from_db

@pytest.mark.parametrize("sport_type, expected_count, expected_ids", [
    ("Football", 2, [1, 4]),
    ("Tech", 1, [2]),
    ("wellness", 1, [3]),
])
def test_get_events_positive_filter_by_sport_type(sample_events_data, sport_type, expected_count, expected_ids):
    """Позитивный: фильтрация по sportType."""

    events = crud.get_events(sportType=sport_type)
    assert len(events) == expected_count
    assert sorted([event.id for event in events]) == sorted(expected_ids)

@pytest.mark.parametrize("date, expected_count, expected_ids", [
    ("2024-08", 3, [1, 3, 4]),
    ("2024-09-20", 1, [2]),
])
def test_get_events_positive_filter_by_date(sample_events_data, date, expected_count, expected_ids):
    """Позитивный: фильтрация по дате."""

    events = crud.get_events(date=date)
    assert len(events) == expected_count
    assert sorted([event.id for event in events]) == sorted(expected_ids)

@pytest.mark.parametrize("location, expected_count, expected_ids", [
    ("Stadium", 1, [1]),
    ("expo center", 1, [2]),
])
def test_get_events_positive_filter_by_location(sample_events_data, location, expected_count, expected_ids):
    """Позитивный: фильтрация по местоположению."""

    events = crud.get_events(location=location)
    assert len(events) == expected_count
    assert sorted([event.id for event in events]) == sorted(expected_ids)

def test_get_events_positive_filter_combination(sample_events_data):
    """Позитивный: комбинация фильтров."""

    events = crud.get_events(sportType="Football", date="2024-08", location="Stadium")
    assert len(events) == 1
    assert events[0].id == 1

@pytest.mark.parametrize("filters", [
    {"sportType": "NonExistentSport"},
    {"date": "3000-01-01"},
    {"location": "Mars"},
    {"sportType": "Football", "date": "2025"},
])
def test_get_events_negative_no_results_for_filters(sample_events_data, filters):
    """Негативный: фильтр по несуществующим значениям (ожидаем пустой список)."""

    events = crud.get_events(**filters)
    assert len(events) == 0


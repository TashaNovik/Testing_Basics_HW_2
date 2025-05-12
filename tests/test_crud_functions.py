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


# --- Tests for crud.create_booking ---

def test_create_booking_positive_with_userid(sample_users_data, sample_events_data, mocker):
    """Позитивный: успешное создание бронирования с userId."""

    mocker.patch('app.crud.uuid.uuid4', return_value=uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"))
    user_id = sample_users_data["testuser@example.com"]["id"]
    event_id = 1
    booking_data = models.BookingCreate(eventId=event_id, tickets=2, userId=user_id)
    created_booking = crud.create_booking(booking_in=booking_data, user_email="testuser@example.com")
    assert created_booking.bookingId == "bk_cccccccc-cccc-cccc-cccc-cccccccccccc"
    assert created_booking.eventId == event_id
    assert created_booking.tickets == 2
    assert created_booking.status == "PENDING_PAYMENT"
    assert created_booking.userId == user_id
    assert "bk_cccccccc-cccc-cccc-cccc-cccccccccccc" in db.bookings_db
    db_booking = db.bookings_db["bk_cccccccc-cccc-cccc-cccc-cccccccccccc"]
    assert db_booking["userId"] == user_id
    assert db_booking["user_email"] == "testuser@example.com"


def test_create_booking_positive_with_user_email_no_userid(sample_users_data, sample_events_data, mocker):
    """Позитивный: успешное создание с user_email, когда userId не предоставлен."""

    mocker.patch('app.crud.uuid.uuid4', return_value=uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"))
    user_email_for_booking = "anotheruser@example.com"
    expected_user_id = sample_users_data[user_email_for_booking]["id"]
    event_id = 2
    booking_data = models.BookingCreate(eventId=event_id, tickets=1)
    created_booking = crud.create_booking(booking_in=booking_data, user_email=user_email_for_booking)
    assert created_booking.bookingId == "bk_dddddddd-dddd-dddd-dddd-dddddddddddd"
    assert created_booking.eventId == event_id
    assert created_booking.userId == expected_user_id
    assert "bk_dddddddd-dddd-dddd-dddd-dddddddddddd" in db.bookings_db
    db_booking = db.bookings_db["bk_dddddddd-dddd-dddd-dddd-dddddddddddd"]
    assert db_booking["user_email"] == user_email_for_booking


def test_create_booking_negative_user_email_not_found_no_userid(sample_events_data, mocker):
    """Негативный: user_email (для определения userId) не найден в db.users_db."""

    mocker.patch('app.crud.uuid.uuid4')
    non_existent_email = "ghost@example.com"
    event_id = 1
    booking_data = models.BookingCreate(eventId=event_id, tickets=1)
    with pytest.raises(KeyError) as excinfo:
        crud.create_booking(booking_in=booking_data, user_email=non_existent_email)
    assert non_existent_email in str(excinfo.value)

# def test_create_booking_negative_invalid_tickets_in_crud(sample_users_data, sample_events_data, mocker):
#     mocker.patch('app.crud.uuid.uuid4')
#     booking_data = models.BookingCreate(eventId=1, tickets=0, userId=sample_users_data["testuser@example.com"]["id"])
#     with pytest.raises(ValueError) as excinfo:
#         crud.create_booking(booking_in=booking_data, user_email="testuser@example.com")
#     assert "Tickets must be greater than 0" in str(excinfo.value)



# --- Tests for crud.update_booking_status ---

def test_update_booking_status_positive_update_status_only(sample_bookings_data):
    """Позитивный: обновление только статуса."""

    booking_id_to_update = "bk_1"
    new_status = "CONFIRMED"
    updated_booking = crud.update_booking_status(booking_id_to_update, new_status)
    assert updated_booking is not None
    assert updated_booking["bookingId"] == booking_id_to_update
    assert updated_booking["status"] == new_status
    assert db.bookings_db[booking_id_to_update]["status"] == new_status
    assert "amount" not in db.bookings_db[booking_id_to_update]


def test_update_booking_status_positive_update_status_and_amount(sample_bookings_data):
    """Позитивный: обновление статуса и суммы."""

    booking_id_to_update = "bk_1"
    new_status = "PAID"
    new_amount = 150.75
    updated_booking = crud.update_booking_status(booking_id_to_update, new_status, amount=new_amount)
    assert updated_booking is not None
    assert updated_booking["status"] == new_status
    assert updated_booking["amount"] == new_amount
    assert db.bookings_db[booking_id_to_update]["status"] == new_status
    assert db.bookings_db[booking_id_to_update]["amount"] == new_amount


def test_update_booking_status_positive_update_existing_amount(sample_bookings_data):
    """Позитивный: обновление статуса и существующей суммы."""

    booking_id_to_update = "bk_2"
    new_status = "REFUNDED"
    new_amount = 45.00
    updated_booking = crud.update_booking_status(booking_id_to_update, new_status, amount=new_amount)
    assert updated_booking is not None
    assert updated_booking["status"] == new_status
    assert updated_booking["amount"] == new_amount
    assert db.bookings_db[booking_id_to_update]["status"] == new_status
    assert db.bookings_db[booking_id_to_update]["amount"] == new_amount


def test_update_booking_status_negative_booking_not_found():
    """Негативный: попытка обновить несуществующее бронирование."""

    updated_booking = crud.update_booking_status("non_existent_bk_id", "PAID")
    assert updated_booking is None


def test_update_booking_status_negative_no_amount_change_if_not_provided(sample_bookings_data):
    """Негативный (проверка поведения): сумма не меняется, если не передана."""

    booking_id_to_update = "bk_2"
    original_amount = db.bookings_db[booking_id_to_update]["amount"]
    new_status = "PENDING_REFUND"
    updated_booking = crud.update_booking_status(booking_id_to_update, new_status)
    assert updated_booking is not None
    assert updated_booking["status"] == new_status
    assert updated_booking["amount"] == original_amount
    assert db.bookings_db[booking_id_to_update]["amount"] == original_amount
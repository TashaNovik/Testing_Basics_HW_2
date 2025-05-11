import pytest
import sys
import os
from app import db

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(autouse=True)
def clear_dbs_before_test():
    """ Очистка БД перед каждым тестом """

    db.users_db.clear()
    db.sessions_db.clear()
    db.bookings_db.clear()
    db.events_db.clear()


@pytest.fixture
def sample_users_data():
    """ Фикстура для предоставления тестовых данных пользователей"""

    users_data = {

        "testuser@example.com":
            {"email": "testuser@example.com",
             "password": "password123",
             "id": "user_1"
             },

        "anotheruser@example.com":
            {"email": "anotheruser@example.com",
             "password": "securepassword",
             "id": "user_2"
             }
    }
    db.users_db.update(users_data)
    return users_data


@pytest.fixture
def sample_events_data():
    """ Фикстура для предоставления тестовых данных событий"""

    events_data = {

        1: {"id": 1,
            "title": "Football Match",
            "date": "2024-08-15T18:00:00Z",
            "location": "Main Stadium",
            "sportType": "Football",
            "availableTickets": 100
            },

        2: {"id": 2,
            "title": "Tech Conference",
            "date": "2024-09-20T09:00:00Z",
            "location": "Expo Center",
            "sportType": "Tech",
            "availableTickets": 50
            },

        3: {"id": 3,
            "title": "Yoga Retreat",
            "date": "2024-08-25T10:00:00Z",
            "location": "Serene Valley",
            "sportType": "Wellness",
            "availableTickets": 20
            },

        4: {"id": 4,
            "title": "Another Football Match",
            "date": "2024-08-30T19:00:00Z",
            "location": "City Arena",
            "sportType": "Football",
            "availableTickets": 0
            },

    }
    db.events_db.update(events_data)
    return events_data

@pytest.fixture
def sample_bookings_data(sample_users_data, sample_events_data):
    """ Фикстура для предоставления тестовых данных бронирований"""

    user1_email = "testuser@example.com"
    event1_id = 1

    bookings_data = {

        "bk_1": {
            "bookingId": "bk_1",
            "eventId": event1_id,
            "tickets": 2,
            "status": "PENDING_PAYMENT",
            "userId": db.users_db[user1_email]["id"],
            "user_email": user1_email
        },

        "bk_2": {
            "bookingId": "bk_2",
            "eventId": 2,
            "tickets": 1,
            "status": "PAID",
            "userId": db.users_db["anotheruser@example.com"]["id"],
            "user_email": "anotheruser@example.com",
            "amount": 50.00
        }
    }
    db.bookings_db.update(bookings_data)
    return bookings_data


# app/crud.py
import uuid
from typing import List, Optional, Dict
from . import models, db # Относительные импорты

# --- User / Auth ---
def get_user_by_email(email: str) -> Optional[Dict]:
    return db.users_db.get(email)

def create_user_for_test(user_in: models.UserLogin) -> Dict:
    user_data = {"email": user_in.email, "password": user_in.password, "id": "user_" + str(uuid.uuid4())}
    db.users_db[user_in.email] = user_data
    return user_data

def create_session(email: str) -> str:
    session_id = str(uuid.uuid4())
    db.sessions_db[session_id] = email
    return session_id

# --- Events ---
def get_events(sportType: Optional[str] = None, date: Optional[str] = None, location: Optional[str] = None) -> List[models.Event]:
    results = [models.Event(**event_data) for event_data in db.events_db.values()] # Преобразуем в Pydantic модели
    if sportType:
        results = [event for event in results if event.sportType.lower() == sportType.lower()]
    if date:
        results = [event for event in results if event.date.startswith(date)]
    if location:
        results = [event for event in results if location.lower() in event.location.lower()]
    return results

def get_event_by_id(event_id: int) -> Optional[Dict]:
    return db.events_db.get(event_id)

# --- Bookings ---
def create_booking(booking_in: models.BookingCreate, user_email: str) -> models.BookingResponse:
    booking_id = "bk_" + str(uuid.uuid4())
    # Используем email текущего пользователя, если userId не предоставлен в запросе
    user_identifier_for_booking = booking_in.userId if booking_in.userId else db.users_db[user_email].get("id", user_email)

    new_booking_data = {
        "bookingId": booking_id,
        "eventId": booking_in.eventId,
        "tickets": booking_in.tickets,
        "status": "PENDING_PAYMENT",
        "userId": user_identifier_for_booking,
        "user_email": user_email # Сохраняем email пользователя, совершившего бронь
    }
    db.bookings_db[booking_id] = new_booking_data
    # Уменьшение билетов (упрощенно, без блокировок)
    # if db.events_db[booking_in.eventId]["availableTickets"] >= booking_in.tickets : # Доп. проверка
    #     db.events_db[booking_in.eventId]["availableTickets"] -= booking_in.tickets
    return models.BookingResponse(**new_booking_data)

def get_booking_by_id(booking_id: str) -> Optional[Dict]:
    return db.bookings_db.get(booking_id)

def update_booking_status(booking_id: str, status: str, amount: Optional[float] = None) -> Optional[Dict]:
    if booking_id in db.bookings_db:
        db.bookings_db[booking_id]["status"] = status
        if amount is not None:
            db.bookings_db[booking_id]["amount"] = amount
        return db.bookings_db[booking_id]
    return None
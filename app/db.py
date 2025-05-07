# app/db.py
from typing import Dict

# In-memory "Databases"
# (В реальном приложении здесь была бы интеграция с БД)
users_db: Dict[str, Dict] = {} # email -> user_data (password, id)
sessions_db: Dict[str, str] = {} # sessionId -> email
events_db: Dict[int, Dict] = {
    123: {"id": 123, "title": "FastAPI Workshop", "date": "2024-09-15T10:00:00Z", "location": "Online", "sportType": "tech", "availableTickets": 50},
    456: {"id": 456, "title": "Python Conference", "date": "2024-10-20T09:00:00Z", "location": "Convention Center", "sportType": "conference", "availableTickets": 100},
    789: {"id": 789, "title": "Running Marathon", "date": "2024-12-31T08:00:00Z", "location": "City Park", "sportType": "running", "availableTickets": 10}, # Изменил на 10 для теста
}
bookings_db: Dict[str, Dict] = {} # bookingId -> booking_data (включая user_email для связи)
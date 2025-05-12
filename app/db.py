from typing import Dict

users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, str] = {}
events_db: Dict[int, Dict] = {
    123: {"id": 123, "title": "FastAPI Workshop", "date": "2024-09-15T10:00:00Z", "location": "Online", "sportType": "tech", "availableTickets": 50},
    456: {"id": 456, "title": "Python Conference", "date": "2024-10-20T09:00:00Z", "location": "Convention Center", "sportType": "conference", "availableTickets": 100},
    789: {"id": 789, "title": "Running Marathon", "date": "2024-12-31T08:00:00Z", "location": "City Park", "sportType": "running", "availableTickets": 10},
}
bookings_db: Dict[str, Dict] = {}
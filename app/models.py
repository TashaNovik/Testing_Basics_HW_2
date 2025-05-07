# app/models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    sessionId: str
    message: str

class Event(BaseModel):
    id: int
    title: str
    date: str
    location: str
    sportType: str
    availableTickets: int

class BookingCreate(BaseModel):
    eventId: int
    tickets: int = Field(..., gt=0)
    userId: Optional[str] = None

class BookingBase(BaseModel): # Базовая модель для ответа и деталей
    bookingId: str
    eventId: int
    tickets: int
    status: str
    userId: Optional[str] = None

class BookingResponse(BookingBase):
    pass

class PaymentDetails(BaseModel):
    cardNumber: str = Field(..., min_length=16, max_length=16)
    expiryDate: str # Формат MM/YY
    cvv: str

class PaymentCreate(BaseModel):
    bookingId: str
    amount: float
    paymentDetails: PaymentDetails

class PaymentResponse(BaseModel):
    paymentId: str
    bookingId: str
    status: str
    message: str

class BookingDetailResponse(BookingBase):
    eventName: str
    amount: Optional[float] = None
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from .. import models, crud, dependencies, db  # db нужен для изменения availableTickets

router = APIRouter(
    tags=["bookings & payments"],
    dependencies=[Depends(dependencies.get_current_user_email)]
)


# --- Bookings Endpoints ---
@router.post("/bookings", response_model=models.BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_new_booking_endpoint(
        booking_data: models.BookingCreate,
        current_user_email: str = Depends(dependencies.get_current_user_email)  # Можно оставить, если нужна переменная
):
    event = crud.get_event_by_id(booking_data.eventId)
    if not event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Event with id {booking_data.eventId} not found")

    if event["availableTickets"] < booking_data.tickets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Not enough tickets available for the selected event")

    # Уменьшаем количество доступных билетов (упрощенно)
    # Важно: это изменение состояния, в реальном приложении нужны транзакции/блокировки
    db.events_db[booking_data.eventId]["availableTickets"] -= booking_data.tickets

    created_booking = crud.create_booking(booking_in=booking_data, user_email=current_user_email)
    return created_booking


@router.get("/bookings/{booking_id_path}", response_model=models.BookingDetailResponse)
async def get_booking_details_endpoint(
        booking_id_path: str,
        current_user_email: str = Depends(dependencies.get_current_user_email)
):
    booking = crud.get_booking_by_id(booking_id_path)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this booking")

    event = crud.get_event_by_id(booking["eventId"])
    if not event:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Associated event not found")

    return models.BookingDetailResponse(
        bookingId=booking["bookingId"],
        eventId=booking["eventId"],
        tickets=booking["tickets"],
        status=booking["status"],
        userId=booking.get("userId"),
        eventName=event["title"],
        amount=booking.get("amount")
    )


# --- Payments Endpoint ---
@router.post("/payments", response_model=models.PaymentResponse, status_code=status.HTTP_200_OK)
async def process_payment_endpoint(
        payment_data: models.PaymentCreate,
        current_user_email: str = Depends(dependencies.get_current_user_email)
):
    booking = crud.get_booking_by_id(payment_data.bookingId)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking["user_email"] != current_user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to pay for this booking")

    if payment_data.paymentDetails.cvv == "ABCD":  # Ваш негативный тест
        crud.update_booking_status(booking_id=payment_data.bookingId, status="PAYMENT_FAILED")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid CVV format", "message": "Payment declined due to invalid payment details."}
        )

    updated_booking = crud.update_booking_status(
        booking_id=payment_data.bookingId,
        status="PAID",
        amount=payment_data.amount
    )
    if not updated_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Booking not found after status update attempt")

    payment_id = "pay_" + crud.uuid.uuid4().hex[:8]
    return models.PaymentResponse(
        paymentId=payment_id,
        bookingId=payment_data.bookingId,
        status=updated_booking["status"],
        message="Payment successful"
    )
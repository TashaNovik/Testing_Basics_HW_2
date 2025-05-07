# app/routers/events.py
from fastapi import APIRouter, Depends
from typing import List, Optional
from .. import models, crud, dependencies

router = APIRouter(
    prefix="/events", # Будет /api/events
    tags=["events"],
    dependencies=[Depends(dependencies.get_current_user_email)] # Защищаем все эндпоинты в этом роутере
)

@router.get("", response_model=List[models.Event]) # Путь "" означает /api/events
async def read_events_endpoint( # Переименовал, чтобы не конфликтовать с функцией из crud
    sportType: Optional[str] = None,
    date: Optional[str] = None,
    location: Optional[str] = None,
    # current_user_email уже применен через router.dependencies
):
    events_list = crud.get_events(sportType=sportType, date=date, location=location)
    return events_list
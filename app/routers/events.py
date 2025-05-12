from fastapi import APIRouter, Depends
from typing import List, Optional
from .. import models, crud, dependencies

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(dependencies.get_current_user_email)]
)

@router.get("", response_model=List[models.Event])
async def read_events_endpoint(
    sportType: Optional[str] = None,
    date: Optional[str] = None,
    location: Optional[str] = None,
):
    events_list = crud.get_events(sportType=sportType, date=date, location=location)
    return events_list
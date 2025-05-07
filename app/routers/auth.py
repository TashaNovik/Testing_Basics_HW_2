# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from .. import models, crud # Относительные импорты из родительской папки app

router = APIRouter(
    prefix="/auth", # Префикс для этого роутера, будет /api/auth/...
    tags=["authentication"] # Теги для документации Swagger/OpenAPI
)

@router.post("/login", response_model=models.LoginResponse, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: models.UserLogin):
    user = crud.get_user_by_email(form_data.email)
    if not user:
        user = crud.create_user_for_test(form_data)
        print(f"User {form_data.email} registered for testing.")

    if user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session_id = crud.create_session(user["email"])
    return {"sessionId": session_id, "message": "Login successful"}
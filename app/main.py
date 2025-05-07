from fastapi import FastAPI
from app.routers import auth, events, bookings

app = FastAPI(title="Booking API")

# Включаем роутеры с общим префиксом /api
app.include_router(auth.router, prefix="/api", tags=["Authentication"]) # Теги здесь для общего раздела в Swagger
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(bookings.router, prefix="/api", tags=["Bookings & Payments"]) # bookings.router уже имеет свои подпути

# Если нужно, можно добавить корневой эндпоинт для проверки, что API работает
@app.get("/")
async def root():
    return {"message": "Welcome to the Booking API!"}

# Запуск Uvicorn (если вы хотите запускать через python main.py)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3001, reload=True)
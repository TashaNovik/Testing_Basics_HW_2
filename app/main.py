from fastapi import FastAPI
from app.routers import auth, events, bookings

app = FastAPI(title="Booking API")
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(bookings.router, prefix="/api", tags=["Bookings & Payments"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Booking API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3001, reload=True)
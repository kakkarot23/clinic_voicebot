import os
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import engine, Base, SessionLocal, get_db
from app.database.seed_data import seed_database
from app.api import (
    voice_api,
    appointments_api,
    hospital_api,
    whatsapp_api,
    kiosk_api,
    admin_api
)

# 1. Create DB tables
Base.metadata.create_all(bind=engine)

# 2. Seed Database
db_session = SessionLocal()
try:
    seed_database(db_session)
finally:
    db_session.close()

# 3. Create FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Kerala Medical Center 24x7 Malayalam Front Office AI Voice Bot Backend",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 4. Static files & Templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 5. Page Routes
@app.get("/")
def page_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"title": settings.PROJECT_NAME})

@app.get("/whatsapp")
def page_whatsapp(request: Request):
    return templates.TemplateResponse(request=request, name="whatsapp.html")

@app.get("/kiosk")
def page_kiosk(request: Request):
    return templates.TemplateResponse(request=request, name="kiosk.html")

@app.get("/dashboard")
def page_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/admin")
def page_admin(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")

# 6. Include API Routers
app.include_router(voice_api.router)
app.include_router(appointments_api.router)
app.include_router(hospital_api.router)
app.include_router(whatsapp_api.router)
app.include_router(kiosk_api.router)
app.include_router(admin_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)

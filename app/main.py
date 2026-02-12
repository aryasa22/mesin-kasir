from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.reports import router as reports_router
from app.api.transactions import router as transactions_router
from app.core.config import settings
from app.db.session import Base, engine
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(transactions_router)
app.include_router(reports_router)


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})


@app.get("/cashier", response_class=HTMLResponse)
def cashier_page(request: Request):
    return templates.TemplateResponse("cashier.html", {"request": request, "store_name": settings.store_name})


@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})


@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})

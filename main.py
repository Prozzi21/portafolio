from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db, get_hero, get_projects, get_skills, get_contact
from routers.admin import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Mi Portafolio", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(admin_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    hero = await get_hero()
    return templates.TemplateResponse("index.html", {
        "request": request, "hero": hero, "active": "inicio"
    })

@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    projects_data = await get_projects()
    return templates.TemplateResponse("projects.html", {
        "request": request, "projects": projects_data, "active": "proyectos"
    })

@app.get("/skills", response_class=HTMLResponse)
async def skills(request: Request):
    skills_data = await get_skills()
    return templates.TemplateResponse("skills.html", {
        "request": request, "skills": skills_data, "active": "habilidades"
    })

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    contact_data = await get_contact()
    return templates.TemplateResponse("contact.html", {
        "request": request, "contact": contact_data, "active": "contacto"
    })

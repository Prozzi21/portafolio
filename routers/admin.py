from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import hash_password, verify_password, create_token, require_admin
from database import (
    get_hero, update_hero,
    get_projects, create_project, update_project, delete_project,
    get_skills, create_skill, update_skill, delete_skill,
    get_contact, update_contact, get_user
)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

async def get_admin_or_redirect(request: Request):
    try:
        return await require_admin(request)
    except HTTPException:
        return None

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(), password: str = Form()):
    user = await get_user(username)
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse("admin/login.html", {
            "request": request, "error": "Usuario o contraseña incorrectos"
        })
    token = create_token(username)
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(key="admin_token", value=token, httponly=True, max_age=7200)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("admin_token")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "admin_user": user})

@router.get("/hero", response_class=HTMLResponse)
async def hero_page(request: Request):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    hero = await get_hero()
    return templates.TemplateResponse("admin/hero.html", {"request": request, "hero": hero, "admin_user": user})

@router.post("/hero")
async def hero_save(request: Request, name: str = Form(), subtitle: str = Form(), description: str = Form()):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    await update_hero(name, subtitle, description)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@router.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    projects = await get_projects()
    return templates.TemplateResponse("admin/projects.html", {"request": request, "projects": projects, "admin_user": user})

@router.post("/projects/create")
async def project_create(
    request: Request,
    title: str = Form(), tech: str = Form(),
    description: str = Form(), features: str = Form(), icon: str = Form()
):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    features_list = [f.strip() for f in features.split(",") if f.strip()]
    await create_project(title, tech, description, features_list, icon)
    return RedirectResponse(url="/admin/projects", status_code=303)

@router.post("/projects/{project_id}/edit")
async def project_edit(
    request: Request, project_id: int,
    title: str = Form(), tech: str = Form(),
    description: str = Form(), features: str = Form(), icon: str = Form()
):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    features_list = [f.strip() for f in features.split(",") if f.strip()]
    await update_project(project_id, title, tech, description, features_list, icon)
    return RedirectResponse(url="/admin/projects", status_code=303)

@router.post("/projects/{project_id}/delete")
async def project_delete(request: Request, project_id: int):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    await delete_project(project_id)
    return RedirectResponse(url="/admin/projects", status_code=303)

@router.get("/skills", response_class=HTMLResponse)
async def skills_page(request: Request):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    skills = await get_skills()
    return templates.TemplateResponse("admin/skills.html", {"request": request, "skills": skills, "admin_user": user})

@router.post("/skills/create")
async def skill_create(request: Request, name: str = Form(), level: int = Form(), icon: str = Form()):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    await create_skill(name, level, icon)
    return RedirectResponse(url="/admin/skills", status_code=303)

@router.post("/skills/{skill_id}/edit")
async def skill_edit(request: Request, skill_id: int, name: str = Form(), level: int = Form(), icon: str = Form()):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    await update_skill(skill_id, name, level, icon)
    return RedirectResponse(url="/admin/skills", status_code=303)

@router.post("/skills/{skill_id}/delete")
async def skill_delete(request: Request, skill_id: int):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    await delete_skill(skill_id)
    return RedirectResponse(url="/admin/skills", status_code=303)

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    contact = await get_contact()
    return templates.TemplateResponse("admin/contact.html", {"request": request, "contact": contact, "admin_user": user})

@router.post("/contact")
async def contact_save(request: Request, email: str = Form(), github: str = Form(), linkedin: str = Form()):
    user = await get_admin_or_redirect(request)
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    await update_contact(email, github, linkedin)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

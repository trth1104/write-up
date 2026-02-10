from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from src.db_helpers import get_user_by_username, get_user_by_email, create_user
from src.auth import (
    get_password_hash,
    authenticate_user,
)
from src.templates_helper import render_template

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return HTMLResponse(content=render_template("login.html", {"request": request}))

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)
    if not user:
        return HTMLResponse(content=render_template(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        ))
    request.session["user_id"] = str(user['id'])
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return HTMLResponse(content=render_template("register.html", {"request": request}))

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    if get_user_by_username(username):
        return HTMLResponse(content=render_template(
            "register.html",
            {"request": request, "error": "Username already exists"}
        ))
    if get_user_by_email(email):
        return HTMLResponse(content=render_template(
            "register.html",
            {"request": request, "error": "Email already exists"}
        ))
    
    user = create_user(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        role='user'
    )
    
    request.session["user_id"] = str(user['id'])
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

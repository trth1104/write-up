from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from src.db_helpers import get_user_favorites, get_music_by_id, check_favorite, add_favorite, remove_favorite, update_user_email, get_user_by_id
from src.auth import get_current_user
from src.templates_helper import render_template
import re
from src.config import FLAG_CONMEO, FLAG_ADMIN

router = APIRouter()

@router.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    current_user = Depends(get_current_user)
):
    favorite_music = get_user_favorites(str(current_user['id']))
    secret = None
    # Get success message from query parameter
    success_msg = request.query_params.get("success")
    if current_user['username'] == 'conmeo':
        secret = FLAG_CONMEO
    elif current_user['username'] == 'admin':
        secret = FLAG_ADMIN

    return HTMLResponse(content=render_template(
        "profile.html",
        {
            "request": request,
            "favorite_music": favorite_music,
            "current_user": current_user,
            "error": None,
            "success": success_msg,
            "secret": secret
        }
    ))

@router.post("/profile/update-email")
async def update_email(
    request: Request,
    new_email: str = Form(...),
    current_user = Depends(get_current_user)
):
    user_id = str(current_user['id'])
    # Validate email format
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    if not re.match(email_pattern, new_email):
        favorite_music = get_user_favorites(user_id)
        return HTMLResponse(content=render_template(
            "profile.html",
            {
                "request": request,
                "favorite_music": favorite_music,
                "current_user": current_user,
                "error": "Invalid email format",
                "success": None
            }
        ))

    
    existing_user = get_user_by_id(int(user_id))
    if existing_user and existing_user['email'] == new_email:
        favorite_music = get_user_favorites(user_id)
        return HTMLResponse(content=render_template(
            "profile.html",
            {
                "request": request,
                "favorite_music": favorite_music,
                "current_user": current_user,
                "error": "Email already exists",
                "success": None
            }
        ))
    
    if update_user_email(user_id, new_email):
        return RedirectResponse(url="/profile?success=Email updated successfully", status_code=status.HTTP_303_SEE_OTHER)
    else:
        favorite_music = get_user_favorites(user_id)
        return HTMLResponse(content=render_template(
            "profile.html",
            {
                "request": request,
                "favorite_music": favorite_music,
                "current_user": current_user,
                "error": "Failed to update email",
                "success": None
            }
        ))

@router.post("/music/{music_id}/favorite")
async def toggle_favorite(
    music_id: str,
    request: Request,
    current_user = Depends(get_current_user)
):
    music = get_music_by_id(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )
    
    user_id = str(current_user['id'])
    is_favorited = check_favorite(user_id, music_id)
    
    if is_favorited:
        remove_favorite(user_id, music_id)
    else:
        add_favorite(user_id, music_id)
    
    return RedirectResponse(url=f"/music/{music_id}", status_code=status.HTTP_303_SEE_OTHER)

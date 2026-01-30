from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from src.db_helpers import get_all_music, get_music_by_id, create_music, delete_music, check_favorite, get_user_by_id, update_music_title
from src.auth import get_current_user, require_admin
from src.config import MUSIC_DIR, COVERS_DIR, UPLOAD_DIR, ALLOWED_AUDIO_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE
from src.templates_helper import render_template
import os
import uuid
import base64
from pathlib import Path

router = APIRouter()

# Ensure upload directories exist
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    return Path(filename).suffix.lower() in allowed_extensions

def image_to_base64(image_path: str) -> str:
    try:
        full_path = os.path.join(UPLOAD_DIR, image_path)
        if not os.path.exists(full_path):
            return ""
        
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/png')

        with open(full_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
    except Exception:
        return ""

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user = Depends(require_admin)
):
    music_list = get_all_music(order_by='created_at DESC')
    
    # Convert cover images to base64
    music_list_base64 = []
    for music in music_list:
        music_dict = dict(music)
        music_dict['cover_image'] = image_to_base64(music['cover_image_path'])
        music_list_base64.append(music_dict)
    
    return HTMLResponse(content=render_template(
        "admin/dashboard.html",
        {
            "request": request,
            "music_list": music_list_base64,
            "current_user": current_user
        }
    ))

@router.post("/admin/music/upload")
async def upload_music(
    request: Request,
    title: str = Form(...),
    artist: str = Form(...),
    cover_image: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    is_premium: str = Form("false"),
    current_user = Depends(require_admin)
):
    if not validate_file_extension(cover_image.filename, ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cover image format"
        )
    if not validate_file_extension(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio file format"
        )
    
    cover_ext = Path(cover_image.filename).suffix
    audio_ext = Path(audio_file.filename).suffix
    cover_filename = f"{uuid.uuid4()}{cover_ext}"
    audio_filename = f"{uuid.uuid4()}{audio_ext}"
    
    cover_path = os.path.join(COVERS_DIR, cover_filename)
    audio_path = os.path.join(MUSIC_DIR, audio_filename)
    
    with open(cover_path, "wb") as f:
        content = await cover_image.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        f.write(content)
    
    with open(audio_path, "wb") as f:
        content = await audio_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        f.write(content)
    
    is_premium_bool = is_premium.lower() == "true"
    
    create_music(
        title=title,
        artist=artist,
        cover_image_path=f"covers/{cover_filename}",
        audio_file_path=f"music/{audio_filename}",
        is_premium=is_premium_bool
    )
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/admin/music/{music_id}/delete")
async def delete_music_route(
    music_id: str,
    current_user = Depends(require_admin)
):
    music = get_music_by_id(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )
    
    cover_path = os.path.join(UPLOAD_DIR, music['cover_image_path'])
    audio_path = os.path.join(UPLOAD_DIR, music['audio_file_path'])
    if os.path.exists(cover_path):
        os.remove(cover_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    delete_music(music_id)
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/admin/music/{music_id}/update")
async def update_music_title_route(
    music_id: str,
    request: Request,
    new_title: str = Form(...),
    current_user = Depends(require_admin)
):
    if len(new_title) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title too long (max 255 characters)"
        )
    music = get_music_by_id(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )
    
    if update_music_title(music_id, new_title):
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update title"
        )

@router.get("/music/{music_id}", response_class=HTMLResponse)
async def music_detail(
    music_id: str,
    request: Request
):
    music = get_music_by_id(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )

    if request.session.get("user_id"):
        current_user = get_current_user(request)
    else:
        return HTMLResponse(content=render_template(
            "detail.html",
            {
                "request": request,
                "music": music,
                "current_user": None,
                "is_favorited": False,
                "can_access": False
            }
        ))
    
    is_favorited = False
    if current_user:
        is_favorited = check_favorite(str(current_user['id']), music_id)
    
    can_access = True
    if music.get('is_premium', False):
        can_access = current_user and (current_user.get('is_premium', False) or current_user.get('role') == 'admin')
    
    return HTMLResponse(content=render_template(
        "detail.html",
        {
            "request": request,
            "music": music,
            "current_user": current_user,
            "is_favorited": is_favorited,
            "can_access": can_access
        }
    ))

@router.get("/music/{music_id}/stream")
async def stream_music(
    music_id: str,
    request: Request
):
    user_id = request.session.get("user_id")
    if user_id:
        current_user = get_user_by_id(user_id)
    else:
        current_user = None
    
    music = get_music_by_id(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )
    
    # Check premium access
    if music.get('is_premium', False):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login required to stream premium music"
            )
        if not (current_user.get('is_premium', False) or current_user.get('role') == 'admin'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium subscription required to stream this music"
            )
    
    # Get file path
    audio_path = os.path.join(UPLOAD_DIR, music['audio_file_path'])
    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    # Return file for streaming (inline, not download)
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline"}
    )

@router.get("/music/{music_id}/download")
async def download_music(
    music_id: str,
    request: Request
):
    """Download music file - requires premium if music is premium"""
    current_user = get_current_user(request)
    
    music = get_music_by_id(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )
    
    # Check premium access
    if music.get('is_premium', False):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login required to download premium music"
            )
    
    # Get file path
    audio_path = os.path.join(UPLOAD_DIR, music['audio_file_path'])
    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    # Return file for download
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"{music['title']}.mp3"
    )

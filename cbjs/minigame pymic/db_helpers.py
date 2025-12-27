from src.database import get_db_cursor
from typing import Optional, Dict, List
from datetime import datetime

def dict_to_music(row: Dict) -> Dict:
    return {
        'id': row['id'],
        'title': row['title'],
        'artist': row['artist'],
        'cover_image_path': row['cover_image_path'],
        'audio_file_path': row['audio_file_path'],
        'is_premium': row['is_premium'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at']
    }
    
def get_user_by_username(username: str) -> Optional[Dict]:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'password_hash': row['password_hash']
            }
        return None

def get_user_by_email(email: str) -> Optional[Dict]:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "SELECT id, username, email FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'email': row['email']
            }
        return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "SELECT id, username, email, role, is_premium FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'role': row['role'],
                'is_premium': row['is_premium']
            }
        return None

def create_user(username: str, email: str, password_hash: str, role: str = 'user', is_premium: bool = False) -> Dict:
    now = datetime.utcnow()
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, role, is_premium, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (username, email, password_hash, role, is_premium, now)
        )
        row = cursor.fetchone()
        return {
            'id': row['id']
        }

def update_user_email(user_id: str, new_email: str) -> bool:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            f"UPDATE users SET email ='{new_email}' WHERE id = '{user_id}'"
        )
        updated = cursor.rowcount > 0
        return updated

def get_music_by_id(music_id: str) -> Optional[Dict]:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "SELECT * FROM music WHERE id = %s",
            (music_id,)
        )
        row = cursor.fetchone()
        return dict_to_music(row) if row else None

def get_all_music(order_by: str = 'created_at DESC') -> List[Dict]:
    with get_db_cursor() as (cursor, conn):
        allowed_orders = ['created_at DESC', 'created_at ASC', 'title ASC', 'title DESC']
        if order_by not in allowed_orders:
            order_by = 'created_at DESC'
        
        cursor.execute(f"SELECT * FROM music ORDER BY {order_by}")
        rows = cursor.fetchall()
        return [dict_to_music(row) for row in rows]

def get_trending_music() -> List[Dict]:
    with get_db_cursor() as (cursor, conn):
        cursor.execute("""
            SELECT 
                m.*,
                COUNT(f.music_id) as favorite_count
            FROM music m
            LEFT JOIN favorites f ON m.id = f.music_id
            GROUP BY m.id
            ORDER BY favorite_count DESC, m.created_at DESC
        """)
        rows = cursor.fetchall()
        return [
            {
                **dict_to_music(row),
                'favorite_count': row['favorite_count']
            }
            for row in rows
        ]

def create_music(title: str, artist: str, cover_image_path: str, audio_file_path: str, is_premium: bool = False) -> Dict:
    now = datetime.utcnow()
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            """
            INSERT INTO music (title, artist, cover_image_path, audio_file_path, is_premium, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (title, artist, cover_image_path, audio_file_path, is_premium, now, now)
        )
        row = cursor.fetchone()
        return dict_to_music(row)

def delete_music(music_id: str) -> bool:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "DELETE FROM music WHERE id = %s",
            (music_id,)
        )
        deleted = cursor.rowcount > 0
        return deleted

def get_user_favorites(user_id: str) -> List[Dict]:
    with get_db_cursor() as (cursor, conn):
        cursor.execute("""
            SELECT m.*
            FROM music m
            INNER JOIN favorites f ON m.id = f.music_id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        return [dict_to_music(row) for row in rows]

def check_favorite(user_id: str, music_id: str) -> bool:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "SELECT 1 FROM favorites WHERE user_id = %s AND music_id = %s",
            (user_id, music_id)
        )
        return cursor.fetchone() is not None

def add_favorite(user_id: str, music_id: str) -> bool:
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute(
                """
                INSERT INTO favorites (user_id, music_id, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, music_id) DO NOTHING
                """,
                (user_id, music_id, datetime.utcnow())
            )
            return cursor.rowcount > 0
    except Exception:
        return False

def remove_favorite(user_id: str, music_id: str) -> bool:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            "DELETE FROM favorites WHERE user_id = %s AND music_id = %s",
            (user_id, music_id)
        )
        deleted = cursor.rowcount > 0
        return deleted

def update_music_title(music_id: str, new_title: str) -> bool:
    with get_db_cursor() as (cursor, conn):
        cursor.execute(
            f"UPDATE music SET title = '{new_title}' WHERE id = '{music_id}'"
        )
        updated = cursor.rowcount > 0
        return updated


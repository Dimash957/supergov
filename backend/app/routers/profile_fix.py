"""
Исправление: Профиль не найден при заполнении данных
Убедимся что профиль создаётся правильно после регистрации
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ..auth import get_current_user
from ..database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.post("/ensure-exists")
async def ensure_profile_exists(current_user = Depends(get_current_user)):
    """
    Убедиться что профиль пользователя существует
    Если существует - вернуть его
    Профиль ДОЛЖЕН БЫТЬ уже создан в get_current_user или во время регистрации
    """
    try:
        user_id = current_user.get("id")
        db = get_db()
        
        # Получить профиль из БД
        profile_res = db.table("users").select("*").eq("id", user_id).execute()
        
        if not profile_res.data:
            # Это не должно случиться, т.к. get_current_user уже создаёт профиль
            raise HTTPException(
                status_code=404,
                detail="Профиль не найден в базе"
            )
        
        profile = profile_res.data[0]
        logger.info(f"Профиль проверен для пользователя {user_id}")
        
        return {
            "success": True,
            "profile": profile,
            "message": "Профиль готов к использованию"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ensuring profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_my_profile(current_user = Depends(get_current_user)):
    """Получить мой профиль"""
    try:
        # Профиль уже загрузился в get_current_user, просто вернуть
        return {
            "success": True,
            "profile": current_user,
            "message": "Профиль загружен"
        }
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me")
async def update_my_profile(
    data: dict,
    current_user = Depends(get_current_user)
):
    """Обновить мой профиль"""
    try:
        user_id = current_user.get("id")
        db = get_db()
        
        # Обновить ТОЛЬКО разрешённые поля
        allowed_fields = ["full_name", "phone", "email", "address", "birth_date", "iin", "language"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return {
                "success": True,
                "message": "Нет данных для обновления"
            }
        
        # Обновить в БД
        db.table("users").update(update_data).eq("id", user_id).execute()
        
        logger.info(f"Профиль обновлен для пользователя {user_id}: {list(update_data.keys())}")
        
        return {
            "success": True,
            "message": "Профиль обновлен",
            "updated": list(update_data.keys())
        }
    
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

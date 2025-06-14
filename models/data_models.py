from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class InstagramProfile:
    """Модель профиля Instagram"""
    username: str
    followers: int
    profile_id: Optional[int] = None


@dataclass
class InstagramPost:
    """Модель поста Instagram"""
    profile_id: int
    display_url: str
    caption: str
    timestamp: Optional[datetime] = None
    post_id: Optional[int] = None


@dataclass
class PhotoDescription:
    """Модель описания фотографии"""
    post_id: int
    description: str
    description_id: Optional[int] = None

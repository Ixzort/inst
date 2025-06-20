from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class InstagramProfile:
    username: str
    followers: int
    data: Optional[str] = None
    portret: Optional[str] = None
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
    post_id: int
    profile_id: int      # добавляем
    description: str
    description_id: Optional[int] = None


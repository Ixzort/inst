from typing import List, Optional
import re


class URLHelper:
    """Вспомогательные функции для работы с URL"""

    @staticmethod
    def extract_username_from_url(url: str) -> Optional[str]:
        """Извлечение username из Instagram URL"""
        pattern = r'instagram\.com/([^/?]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    @staticmethod
    def validate_instagram_url(url: str) -> bool:
        """Проверка корректности Instagram URL"""
        pattern = r'^https?://(www\.)?instagram\.com/[^/?]+/?$'
        return bool(re.match(pattern, url))


class DataValidator:
    @staticmethod
    def is_valid_image_url(url: str) -> bool:
        if not url:
            return False
        # Проверяем наличие .jpg/.jpeg/.png/.webp перед знаком ?
        return re.search(r'\.(jpg|jpeg|png|webp)(\?|$)', url.lower()) is not None

    @staticmethod
    def clean_caption(caption: str) -> str:
        """Очистка текста поста от лишних символов"""
        if not caption:
            return ""

        # Удаление лишних пробелов и переносов строк
        cleaned = re.sub(r'\s+', ' ', caption.strip())
        return cleaned[:1000]  # Ограничение длины

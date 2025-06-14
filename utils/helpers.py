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
    """Валидация данных"""

    @staticmethod
    def is_valid_image_url(url: str) -> bool:
        """Проверка корректности URL изображения"""
        if not url:
            return False

        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        return any(url.lower().endswith(ext) for ext in valid_extensions)

    @staticmethod
    def clean_caption(caption: str) -> str:
        """Очистка текста поста от лишних символов"""
        if not caption:
            return ""

        # Удаление лишних пробелов и переносов строк
        cleaned = re.sub(r'\s+', ' ', caption.strip())
        return cleaned[:1000]  # Ограничение длины

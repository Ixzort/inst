import time
from openai import OpenAI
from typing import Optional
import os

from typing import List, Dict



class ImageProcessorService:
    """Сервис для анализа изображений через OpenAI Vision API"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"
        self.rate_limit_delay = 1  # Задержка между запросами в секундах

    def analyze_image(self, image_url: str) -> Optional[str]:
        """
        Анализ изображения через OpenAI Vision API

        Args:
            image_url: URL изображения для анализа

        Returns:
            Описание изображения или None при ошибке
        """
        try:
            print(f"🤖 Анализ изображения: {image_url[:50]}...")

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — помощник для анализа изображений в социальных сетях. "
                            "Опиши изображение емко и содержательно на русском языке, "
                            "выделяя ключевые элементы: люди, объекты, настроение, стиль, локация."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Проанализируй это изображение из Instagram поста:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )

            description = response.choices[0].message.content
            print(f"✅ Получено описание: {description[:100]}...")

            # Задержка для соблюдения rate limit
            time.sleep(self.rate_limit_delay)

            return description

        except Exception as e:
            print(f"❌ Ошибка анализа изображения {image_url}: {e}")
            return None

    def batch_analyze_images(self, image_urls: List[str]) -> Dict[str, Optional[str]]:
        """
        Пакетный анализ нескольких изображений

        Args:
            image_urls: Список URL изображений

        Returns:
            Словарь {url: description}
        """
        results = {}
        total = len(image_urls)

        for i, url in enumerate(image_urls, 1):
            print(f"🔄 Обработка изображения {i}/{total}")
            results[url] = self.analyze_image(url)

        return results


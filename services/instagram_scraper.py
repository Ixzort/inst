import os
import requests
from typing import List, Dict

class InstagramScraperService:
    """Сервис для получения данных из Instagram через Apify Task API"""

    def __init__(self):
        self.apify_token = os.getenv('APIFY_TOKEN')
        self.task_id = os.getenv('APIFY_TASK_ID', '9gGOHVesIjVRHlEkf')
        self.base_url = f"https://api.apify.com/v2/actor-tasks/{self.task_id}/run-sync-get-dataset-items"

    def fetch_posts(self) -> List[Dict]:
        """
        Получение постов через сохранённую задачу (Task) Apify.
        Вся конфигурация задаётся внутри Apify UI.
        """
        params = {'token': self.apify_token}

        try:
            print(f"📥 Запуск Apify Task (ID: {self.task_id}) ...")
            response = requests.post(
                self.base_url,
                params=params,
                timeout=90  # На таску иногда уходит больше времени!
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ Получено {len(data)} постов из Apify Task")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса к Apify Task: {e}")
            return []

# Пример использования
if __name__ == "__main__":
    service = InstagramScraperService()
    posts_data = service.fetch_posts()
    print(posts_data)

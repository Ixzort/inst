import requests
import os
from typing import List, Dict, Union
from models.data_models import InstagramProfile, InstagramPost
from datetime import datetime

class InstagramScraperService:
    """Сервис для получения данных из Instagram через Apify API"""

    def __init__(self):
        self.apify_token = os.getenv('APIFY_TOKEN')
        self.base_url = "https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items"

    def fetch_posts(self, usernames: Union[str, List[str]], limit: int = 10) -> List[Dict]:
        """
        Получение постов через Apify Instagram Scraper

        Args:
            usernames: username (str) или список username (List[str])
            limit: Максимальное количество постов

        Returns:
            Список данных постов
        """
        if isinstance(usernames, str):
            usernames = [usernames]

        # Формируем URL профилей для Apify
        target_urls = [f"https://www.instagram.com/{username.strip().lstrip('@')}/" for username in usernames]

        headers = {'Content-Type': 'application/json'}

        payload = {
            'directUrls': target_urls,
            'resultsType': 'posts',
            'resultsLimit': limit
        }

        params = {'token': self.apify_token}

        try:
            print(f"📥 Отправка запроса к Apify для {len(target_urls)} профилей: {target_urls}")
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                params=params,
                timeout=300
            )
            response.raise_for_status()
            data = response.json()
            print(f"✅ Получено {len(data)} постов от Apify")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса к Apify: {e}")
            return []

    def parse_profile_data(self, raw_data: Dict) -> InstagramProfile:
        """Парсинг данных профиля из сырых данных Apify"""
        return InstagramProfile(
            username=raw_data.get('username', ''),
            followers=raw_data.get('followersCount', 0)
        )

    def parse_post_data(self, raw_data: Dict, profile_id: int) -> InstagramPost:
        """Парсинг данных поста из сырых данных Apify"""
        timestamp = None
        if raw_data.get('timestamp'):
            try:
                timestamp = datetime.fromisoformat(
                    raw_data['timestamp'].replace('Z', '+00:00')
                )
            except Exception:
                timestamp = datetime.now()

        return InstagramPost(
            profile_id=profile_id,
            display_url=raw_data.get('displayUrl', ''),
            caption=raw_data.get('caption', ''),
            timestamp=timestamp
        )


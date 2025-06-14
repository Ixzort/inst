from services.instagram_scraper import InstagramScraperService
from services.image_processor import ImageProcessorService
from services.database_service import DatabaseService
from utils.helpers import DataValidator
from models.data_models import PhotoDescription, InstagramProfile

class InstagramAnalyzer:
    """Класс для анализа одного Instagram профиля без валидации элементов"""

    def __init__(self):
        self.scraper = InstagramScraperService()
        self.image_processor = ImageProcessorService()
        self.database = DatabaseService()

    def process_username(self, username: str, limit: int = 2):
        print(f"🚀 Обработка профиля: @{username}")

        raw_data = self.scraper.fetch_posts(username, limit)
        if not raw_data:
            print("❌ Нет данных для обработки")
            return

        # Сохраняем профиль один раз
        profile = InstagramProfile(username=username, followers=0)
        profile_id = self.database.save_profile(profile)
        if not profile_id:
            print("❌ Не удалось сохранить профиль")
            return

        processed = 0
        for item in raw_data:
            try:
                post = self.scraper.parse_post_data(item, profile_id)
                post_id = self.database.save_post(post)
                if not post_id:
                    continue

                if DataValidator.is_valid_image_url(post.display_url):
                    desc_text = self.image_processor.analyze_image(post.display_url)
                    if desc_text:
                        description = PhotoDescription(
                            post_id=post_id,
                            profile_id=profile_id,  # передаём связь
                            description=desc_text
                        )
                        self.database.save_photo_description(description)

                processed += 1
                print(f"✅ Обработан пост {processed}/{len(raw_data)}")

            except Exception as e:
                print("❌ Ошибка обработки:", e)

        self.process_new_descriptions(profile_id)

        stats = self.database.get_statistics()
        print(f"\n🎉 Завершено! Обработано постов: {processed}")
        print(
            f"📊 Сводка — Профилей: {stats.get('profiles', 0)}, "
            f"Постов: {stats.get('posts', 0)}, Описаний: {stats.get('descriptions', 0)}"
        )
    def process_new_descriptions(self, profile_id: int):
        posts = self.database.get_posts_without_description_for_profile(profile_id)
        if not posts:
            print("✅ Нет новых изображений для описания.")
            return

        print(f"🔄 Анализируем {len(posts)} изображений для описания...")
        for item in posts:
            post_id = item['post_id']
            url = item['display_url']
            if DataValidator.is_valid_image_url(url):
                desc_text = self.image_processor.analyze_image(url)
                if desc_text:
                    description = PhotoDescription(
                        post_id=post_id,
                        profile_id=profile_id,
                        description=desc_text
                    )
                    self.database.save_photo_description(description)
        print(f"✅ Описаний добавлено: {len(posts)}")


if __name__ == "__main__":
    analyzer = InstagramAnalyzer()
    analyzer.process_username("hello__marusya", limit=5)




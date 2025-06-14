from services.instagram_scraper import InstagramScraperService
from services.image_processor import ImageProcessorService
from services.database_service import DatabaseService
from utils.helpers import URLHelper, DataValidator

class InstagramAnalyzer:
    """Главный класс для анализа одного Instagram профиля"""

    def __init__(self):
        self.scraper = InstagramScraperService()
        self.image_processor = ImageProcessorService()
        self.database = DatabaseService()

    def process_username(self, username: str):
        """
        Основной метод обработки одного username Instagram
        Args:
            username: username для анализа
        """
        print(f"🚀 Запуск анализа Instagram профиля: @{username}")

        # Сборка URL профиля из username
        profile_url = f"https://www.instagram.com/{username}/"
        print(f"🔗 Построен URL: {profile_url}")

        # Валидация URL
        if not URLHelper.validate_instagram_url(profile_url):
            print("❌ Некорректный username или ссылка.")
            return

        # Получение данных от Apify
        raw_data = self.scraper.fetch_posts([profile_url], limit=10)
        if not raw_data:
            print("❌ Нет данных для обработки")
            return

        # Обработка записи (ожидается, что данные по одному профилю)
        processed_count = 0

        for item in raw_data:
            try:
                if not self._validate_raw_data(item):
                    continue

                # Сохранение профиля
                profile = self.scraper.parse_profile_data(item)
                profile_id = self.database.save_profile(profile)
                if not profile_id:
                    continue

                # Сохранение поста
                post = self.scraper.parse_post_data(item, profile_id)
                post_id = self.database.save_post(post)
                if not post_id:
                    continue

                # Анализ изображения
                if DataValidator.is_valid_image_url(post.display_url):
                    description_text = self.image_processor.analyze_image(post.display_url)
                    if description_text:
                        from models.data_models import PhotoDescription
                        description = PhotoDescription(
                            post_id=post_id,
                            description=description_text
                        )
                        self.database.save_photo_description(description)

                processed_count += 1
                print(f"✅ Обработана запись {processed_count}/{len(raw_data)}")

            except Exception as e:
                print(f"❌ Ошибка обработки записи: {e}")
                continue

        # Показ статистики
        self._show_statistics()
        print(f"\n🎉 Обработка завершена! Успешно обработано: {processed_count} записей")

    def _validate_raw_data(self, item: dict) -> bool:
        """Валидация сырых данных от Apify"""
        required_fields = ['username', 'displayUrl']
        return all(item.get(field) for field in required_fields)

    def _show_statistics(self):
        """Отображение статистики базы данных"""
        stats = self.database.get_statistics()
        if stats:
            print(f"\n📊 Статистика базы данных:")
            print(f"   Профилей: {stats.get('profiles', 0)}")
            print(f"   Постов: {stats.get('posts', 0)}")
            print(f"   Описаний: {stats.get('descriptions', 0)}")

def main():
    """Точка входа в приложение"""
    username = "hello__marusya"  # сюда подставь нужный username
    analyzer = InstagramAnalyzer()
    analyzer.process_username(username)

if __name__ == "__main__":
    main()

from services.instagram_scraper import InstagramScraperService
from services.image_processor import ImageProcessorService
from services.database_service import DatabaseService
from utils.helpers import DataValidator
from models.data_models import InstagramProfile, PhotoDescription
from config.database import DatabaseConfig
import argparse

class InstagramAnalyzer:
    """Анализ одного Instagram профиля с сохранением описаний изображений"""

    def __init__(self):
        self.scraper = InstagramScraperService()
        self.image_processor = ImageProcessorService()
        self.database = DatabaseService()

    def process_username(self, username: str, limit: int = 5):
        print(f"🚀 Обработка профиля: @{username}")

        raw_data = self.scraper.fetch_posts(username, limit)
        if not raw_data:
            print("❌ Нет данных для обработки")
            return

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
                processed += 1
                print(f"✅ Пост сохранён и обработан {processed}/{len(raw_data)}")
            except Exception as e:
                print("❌ Ошибка обработки поста:", e)

        self.process_new_descriptions(profile_id)

        # --- Шаг 3: формируем data + портрет профиля ---
        items = self.database.get_posts_with_descriptions(profile_id)
        lines = []
        for idx, it in enumerate(items, 1):
            ts = it['timestamp'].isoformat() if it['timestamp'] else "N/A"
            lines.append(f"{idx}) Фото {idx}")
            lines.append(ts)
            lines.append(it['caption'] or "")
            lines.append(it['description'] or "")
        profile_data = "\n".join(lines)
        print(f"[DATA] profile_data:\n{profile_data}")

        porter_prompt = f"""Проанализируй этот профиль @{username} по данным:
{profile_data}

Составь ответ в формате:
• Возраст, локация, семья
• Интересы, стиль, характер
• Советы по общению, 
• Пример первого сообщения
"""
        resp = self.image_processor.openai_client.chat.completions.create(
            model=self.image_processor.model,
            messages=[
                {"role": "system", "content": "Ты — аналитик соцсетей, делай структурированный ответ."},
                {"role": "user", "content": porter_prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        porter_text = resp.choices[0].message.content
        print(f"[PORTER] porter_text:\n{porter_text}")

        conn = DatabaseConfig.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE instagram_profile SET data = %s, portret = %s WHERE profile_id = %s",
            (profile_data, porter_text, profile_id)
        )
        conn.commit()
        conn.close()
        print("✅ Поля data и portret обновлены в instagram_profile")

        stats = self.database.get_statistics()
        print(f"\n🎉 Завершено! Обработано постов: {processed}")
        print(f"📊 Сводка — Профилей: {stats['profiles']}, Постов: {stats['posts']}, Описаний: {stats['descriptions']}")

    def process_new_descriptions(self, profile_id: int):
        print(f"\n📌 Начинаем запись описаний для профиля ID = {profile_id}")
        posts = self.database.get_posts_without_description_for_profile(profile_id)
        print(f"[NEW_DESC] Найдено постов без описания: {len(posts)}, детали: {posts}")

        if not posts:
            print("✅ Нет новых изображений для описания.")
            return

        for item in posts:
            post_id = item['post_id']
            url = item['display_url']
            print(f"[NEW_DESC] Попытка описания поста {post_id}, URL={url}")

            if not DataValidator.is_valid_image_url(url):
                print(f"[NEW_DESC] Некорректный URL, пропускаем: {url}")
                continue

            desc_text = self.image_processor.analyze_image(url)
            if not desc_text:
                print(f"[NEW_DESC] Пустое описание, пропускаем пост {post_id}")
                continue

            description = PhotoDescription(post_id=post_id, profile_id=profile_id, description=desc_text)
            print(f"[NEW_DESC] Сохраняем описание для post_id={post_id}")
            self.database.save_photo_description(description)

        print("✅ Анализ изображений завершен, описания добавлены!")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Instagram username")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    analyzer = InstagramAnalyzer()
    analyzer.process_username(args.username, limit=args.limit)

if __name__ == "__main__":
    main()






from typing import Optional, List
from config.database import DatabaseConfig
from models.data_models import InstagramProfile, InstagramPost, PhotoDescription


class DatabaseService:
    """Сервис для работы с базой данных"""

    def save_profile(self, profile: InstagramProfile) -> Optional[int]:
        """
        Сохранение профиля в базу данных

        Args:
            profile: Объект профиля Instagram

        Returns:
            ID созданного/существующего профиля
        """
        conn = None
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()

            # Проверка существования профиля
            cursor.execute(
                "SELECT id FROM profiles WHERE username = %s",
                (profile.username,)
            )
            existing_profile = cursor.fetchone()

            if existing_profile:
                print(f"📋 Профиль @{profile.username} уже существует (ID: {existing_profile[0]})")
                return existing_profile[0]

            # Создание нового профиля
            cursor.execute(
                """INSERT INTO profiles (username, followers) 
                   VALUES (%s, %s) RETURNING id""",
                (profile.username, profile.followers)
            )

            profile_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Профиль @{profile.username} сохранён с ID: {profile_id}")
            return profile_id

        except Exception as e:
            print(f"❌ Ошибка сохранения профиля: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def save_post(self, post: InstagramPost) -> Optional[int]:
        """
        Сохранение поста в базу данных

        Args:
            post: Объект поста Instagram

        Returns:
            ID созданного поста
        """
        conn = None
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """INSERT INTO posts (profile_id, display_url, caption, timestamp) 
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (post.profile_id, post.display_url, post.caption, post.timestamp)
            )

            post_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Пост сохранён с ID: {post_id}")
            return post_id

        except Exception as e:
            print(f"❌ Ошибка сохранения поста: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def save_photo_description(self, description: PhotoDescription) -> Optional[int]:
        """
        Сохранение описания фотографии

        Args:
            description: Объект описания фотографии

        Returns:
            ID созданного описания
        """
        conn = None
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """INSERT INTO photo_descriptions (post_id, description) 
                   VALUES (%s, %s) RETURNING id""",
                (description.post_id, description.description)
            )

            description_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Описание сохранено для поста ID: {description.post_id}")
            return description_id

        except Exception as e:
            print(f"❌ Ошибка сохранения описания: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def get_statistics(self) -> dict:
        """Получение статистики по базе данных"""
        conn = None
        try:
            conn = DatabaseConfig.get_dict_connection()
            cursor = conn.cursor()

            # Подсчет записей в таблицах
            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM profiles")
            stats['profiles'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM posts")
            stats['posts'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM photo_descriptions")
            stats['descriptions'] = cursor.fetchone()['count']

            return stats

        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}
        finally:
            if conn:
                conn.close()

from typing import Optional
from config.database import DatabaseConfig
from models.data_models import InstagramProfile, InstagramPost, PhotoDescription
from typing import List, Dict



class DatabaseService:
    """Сервис для работы с базой данных"""

    def save_profile(self, profile: InstagramProfile) -> Optional[int]:
        conn = None
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()

            # Проверка существования профиля
            cursor.execute(
                "SELECT profile_id FROM instagram_profile WHERE username = %s",
                (profile.username,)
            )
            existing = cursor.fetchone()
            if existing:
                print(f"📋 Профиль @{profile.username} уже существует (ID: {existing[0]})")
                return existing[0]

            # Создание нового профиля
            cursor.execute(
                """INSERT INTO instagram_profile (username, followers)
                   VALUES (%s, %s) RETURNING profile_id""",
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
        conn = None
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """INSERT INTO instagram_post (profile_id, display_url, caption, timestamp)
                   VALUES (%s, %s, %s, %s) RETURNING post_id""",
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
        conn = DatabaseConfig.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO photo_description (post_id, profile_id, description)
                   VALUES (%s, %s, %s) RETURNING description_id""",
                (description.post_id, description.profile_id, description.description)
            )
            description_id = cursor.fetchone()[0]
            conn.commit()  # <- ОБЯЗАТЕЛЬНО!
            print(f"✅ Описание сохранено (ID: {description_id}) для поста {description.post_id}")
            return description_id
        except Exception as e:
            print(f"❌ Ошибка сохранения описания: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            conn.close()

    def get_statistics(self) -> dict:
        conn = DatabaseConfig.get_dict_connection()
        cursor = conn.cursor()
        stats = {}

        cursor.execute("SELECT COUNT(*) AS count FROM instagram_profile")
        stats['profiles'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM instagram_post")
        stats['posts'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM photo_description")
        stats['descriptions'] = cursor.fetchone()['count']

        conn.close()
        return stats

    def get_posts_without_description_for_profile(self, profile_id: int) -> List[dict]:
        """
        Возвращает посты заданного профиля, у которых нет описания.
        """
        conn = DatabaseConfig.get_dict_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.post_id, p.display_url
            FROM instagram_post p
            LEFT JOIN photo_description d ON p.post_id = d.post_id
            WHERE p.profile_id = %s AND d.post_id IS NULL
        """, (profile_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows  # [{'post_id':..., 'display_url':...}, ...]



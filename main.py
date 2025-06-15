import os
import logging
from flask import Flask, request, jsonify
from services.instagram_scraper import InstagramScraperService
from services.image_processor import ImageProcessorService
from services.database_service import DatabaseService
from utils.helpers import DataValidator
from models.data_models import InstagramProfile, PhotoDescription
from config.database import DatabaseConfig

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class InstagramAnalyzer:
    """Анализ одного Instagram профиля с сохранением описаний изображений"""
    def __init__(self):
        self.scraper = InstagramScraperService()
        self.image_processor = ImageProcessorService()
        self.database = DatabaseService()

    def process_username(self, username: str, limit: int = 100):
        result = {"processed": 0, "messages": []}
        try:
            result["messages"].append(f"🚀 Обработка профиля: @{username}")
            raw_data = self.scraper.fetch_posts(username, limit)
            if not raw_data:
                return {"error": "Нет данных для обработки"}

            profile = InstagramProfile(username=username, followers=0)
            profile_id = self.database.save_profile(profile)
            if not profile_id:
                return {"error": "Не удалось сохранить профиль"}

            for item in raw_data:
                try:
                    post = self.scraper.parse_post_data(item, profile_id)
                    post_id = self.database.save_post(post)
                    if post_id:
                        result["processed"] += 1
                        result["messages"].append(f"✅ Пост сохранён: {post_id}")
                except Exception as e:
                    result["messages"].append(f"❌ Ошибка поста: {e}")

            self._process_new_descriptions(profile_id)
            profile_data = self._compile_profile_data(profile_id, username)
            porter_text = self._analyze_profile(username, profile_data)
            self._save_profile_analysis(profile_id, profile_data, porter_text)
            result["analysis"] = porter_text
            result["messages"].append("🎉 Анализ завершён")

            return result

        except Exception as e:
            return {"error": str(e)}

    def _process_new_descriptions(self, profile_id: int):
        posts = self.database.get_posts_without_description_for_profile(profile_id)
        for item in posts:
            url = item['display_url']
            if not DataValidator.is_valid_image_url(url):
                continue
            desc = self.image_processor.analyze_image(url)
            if not desc:
                continue
            photo_desc = PhotoDescription(post_id=item['post_id'], profile_id=profile_id, description=desc)
            self.database.save_photo_description(photo_desc)

    def _compile_profile_data(self, profile_id: int, username: str):
        items = self.database.get_posts_with_descriptions(profile_id)
        lines = [
            f"{idx}) Фото {idx}\n{it['timestamp'].isoformat() if it['timestamp'] else 'N/A'}\n{it['caption'] or ''}\n{it['description'] or ''}"
            for idx, it in enumerate(items, 1)
        ]
        return "\n".join(lines)

    def _analyze_profile(self, username: str, profile_data: str):
        prompt = f"""Проанализируй этот профиль @{username} по данным:
{profile_data}

Составь ответ в формате:
• Возраст, локация, семья
• Интересы, стиль, характер
• Советы по общению,
• Пример первого сообщения
"""
        resp = self.image_processor.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — аналитик соцсетей, делай структурированный ответ."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return resp.choices[0].message.content

    def _save_profile_analysis(self, profile_id: int, profile_data: str, porter_text: str):
        conn = DatabaseConfig.get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE instagram_profile SET data = %s, portret = %s WHERE profile_id = %s",
            (profile_data, porter_text, profile_id)
        )
        conn.commit()
        conn.close()

analyzer = InstagramAnalyzer()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        username = request.args.get('username')
        logging.info(f"[FLASK] GET request, username from args: {username}")
    else:
        data = request.get_json(force=True, silent=True)
        username = data.get("username") if isinstance(data, dict) else None
        logging.info(f"[FLASK] POST request, username from JSON: {username}")

    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    result = analyzer.process_username(username)
    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 200

    return jsonify({"status": "success", "username": username, "result": result}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)







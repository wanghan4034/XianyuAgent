from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from .agent import XianyuAgent
from .service import summarize_prices
from .web_utils import ALLOWED_EXTENSIONS, is_allowed_image, parse_max_items


def create_app() -> Flask:
    app = Flask(__name__)
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/capability")
    def capability_probe():
        headed = request.args.get("headed", "false").lower() == "true"
        agent = XianyuAgent(headless=not headed)
        try:
            result = agent.probe_image_search_support()
            return jsonify(result)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.post("/api/search-by-keyword")
    def search_by_keyword():
        payload = request.get_json(silent=True) or {}
        keyword = (payload.get("keyword") or "").strip()
        if not keyword:
            return jsonify({"error": "缺少 keyword"}), 400

        max_items = parse_max_items(str(payload.get("max_items", "20")))
        headed = str(payload.get("headed", "false")).lower() == "true"

        agent = XianyuAgent(headless=not headed)
        try:
            products = agent.crawl_keyword(keyword, max_items=max_items)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

        return jsonify(
            {
                "summary": summarize_prices(products),
                "items": [item.to_dict() for item in products],
            }
        )

    @app.post("/api/search-by-image")
    def search_by_image():
        if "image" not in request.files:
            return jsonify({"error": "缺少 image 文件字段"}), 400

        file = request.files["image"]
        if not file.filename:
            return jsonify({"error": "未选择文件"}), 400

        if not is_allowed_image(file.filename):
            return jsonify({"error": "仅支持 jpg/jpeg/png/webp 图片"}), 400

        safe_name = secure_filename(file.filename)
        target = upload_dir / f"{uuid4().hex}_{safe_name}"
        file.save(target)

        max_items = parse_max_items(request.form.get("max_items", "20"))
        headed = request.form.get("headed", "false").lower() == "true"

        agent = XianyuAgent(headless=not headed)
        try:
            products = agent.crawl_image(str(target), max_items=max_items)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

        return jsonify(
            {
                "summary": summarize_prices(products),
                "items": [item.to_dict() for item in products],
            }
        )

    @app.get("/api/meta")
    def meta():
        return jsonify({
            "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
            "default_max_items": 20,
            "max_items_range": [1, 100],
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)

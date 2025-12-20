from flask import Blueprint, request, session, jsonify
from db import get_db
from services.action.create.post import to_tile
from psycopg2.extras import RealDictCursor

post_bp = Blueprint("create_post", __name__, url_prefix="/post")

@post_bp.route("/to-tile", methods=["POST"])
def post():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "invalid payload"}), 400

    content = data["text"].strip()
    if content == "":
        return jsonify({"error": "empty post"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    post_obj = to_tile(
        cur,
        user_id=session["user_id"],
        content=content
    )

    if post_obj is None:
        cur.close()
        conn.close()
        return jsonify({"error": "invalid user"}), 400

    conn.commit()
    cur.close()
    conn.close()

    # WebSocket で post_obj をブロードキャスト予定
    return jsonify(post_obj)
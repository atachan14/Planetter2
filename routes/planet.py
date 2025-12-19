from flask import Blueprint, request, session, jsonify
from db import get_db
from services.planet import walk_user, turn_user, post_user, fetch_planet_data,fetch_here_data
from psycopg2.extras import RealDictCursor

planet_bp = Blueprint("planet", __name__, url_prefix="/planet")



# ========================
# --------display-----------
# ====================

@planet_bp.route("/data")
def state():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        data = fetch_planet_data(cur, session["user_id"])
        return jsonify(data)
    finally:
        cur.close()
        conn.close()


@planet_bp.route("/here")
def just_pos():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        data = fetch_here_data(cur, session["user_id"])
        return jsonify(data)
    finally:
        cur.close()
        conn.close()







# ========================
# --------action-----------
# ========================

@planet_bp.route("/walk", methods=["POST"])
def walk():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    temp = walk_user(cur, session["user_id"])
    if temp is None:
        return jsonify({"error": "invalid user"}), 400

    conn.commit()
    cur.close()
    conn.close()

    # WebSocketでtempを送信 
    return jsonify({
    })


@planet_bp.route("/turn", methods=["POST"])
def turn():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    # left = -1, right = +1 を想定
    try:
        turn = int(request.form.get("turn"))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid turn"}), 400

    if turn not in (-1, 1):
        return jsonify({"error": "invalid turn"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    temp = turn_user(cur, session["user_id"], turn)
    if temp is None:
        return jsonify({"error": "invalid user"}), 400

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
    })

@planet_bp.route("/post", methods=["POST"])
def post():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "invalid payload"}), 400

    value = data["text"].strip()
    if value == "":
        return jsonify({"error": "empty post"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    post_obj = post_user(
        cur,
        user_id=session["user_id"],
        value=value
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

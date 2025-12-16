from flask import Blueprint, request, session, jsonify
from db import get_db
from services.planet import walk_player, turn_player, get_surroundings,get_planet_tiles
from psycopg2.extras import RealDictCursor

planet_bp = Blueprint("planet", __name__, url_prefix="/planet")



# ========================
# --------display-----------
# ====================

@planet_bp.route("/tiles")
def planet_tiles():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        data = get_planet_tiles(cur, session["user_id"])
        return jsonify(data)
    finally:
        cur.close()
        conn.close()

@planet_bp.route("/surroundings")
def surroundings():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    return jsonify({
        "tiles": {
            "4": {"type": "none"},
            "5": {"type": "player"},
            "6": {"type": "post", "value": "hello"},
            "7": {"type": "book", "name": "魔導書"},
            "8": {"type": "page", "name": "はじめに"},
            "9": {"type": "none"},
        }
    })









# ========================
# --------action-----------
# ====================

@planet_bp.route("/walk", methods=["POST"])
def walk():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    temp = walk_player(cur, session["user_id"])
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

    turn_player(cur, session["user_id"], turn)
    surroundings = get_surroundings(cur, session["user_id"])

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "surroundings": surroundings
    })

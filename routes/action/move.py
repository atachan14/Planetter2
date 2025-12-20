from flask import Blueprint, request, session, jsonify
from db import get_db
from services.action.move import walk_user, turn_user
from psycopg2.extras import RealDictCursor

move_bp = Blueprint("move", __name__, url_prefix="/move")

@move_bp.route("/walk", methods=["POST"])
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


@move_bp.route("/turn", methods=["POST"])
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
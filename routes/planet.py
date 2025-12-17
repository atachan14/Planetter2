from flask import Blueprint, request, session, jsonify
from db import get_db
from services.planet import walk_user, turn_user, fetch_surround_data,fetch_planet_data
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

@planet_bp.route("/surround")
def surround():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        data = fetch_surround_data(cur, session["user_id"])
        return jsonify(data)
    finally:
        cur.close()
        conn.close()

@planet_bp.route("/just-pos")
def just_pos():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401








# ========================
# --------action-----------
# ====================

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

    turn_user(cur, session["user_id"], turn)
    surroundings = fetch_surround_data(cur, session["user_id"])

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "surroundings": surroundings
    })

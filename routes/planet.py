from flask import Blueprint, request, session, jsonify
from db import get_db
from services.planet import walk_player, turn_player, get_surroundings

planet_bp = Blueprint("planet", __name__)

@planet_bp.route("/walk", methods=["POST"])
def walk():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor()

    walk_player(cur, session["user_id"])
    surroundings = get_surroundings(cur, session["user_id"])

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "surroundings": surroundings
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
    cur = conn.cursor()

    turn_player(cur, session["user_id"], turn)
    surroundings = get_surroundings(cur, session["user_id"])

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "surroundings": surroundings
    })

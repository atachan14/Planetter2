from flask import Blueprint, session, jsonify
from services.user_state import get_user_state
from db import get_db

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/user_state")
def user_state():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor()
    try:
        state = get_user_state(cur, session["user_id"])
        return jsonify(state)
    finally:
        cur.close()
        conn.close()
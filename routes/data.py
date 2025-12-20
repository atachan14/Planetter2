from flask import Blueprint, session, jsonify
from db import get_db
from services.data import fetch_self_data,fetch_planet_data,fetch_here_data
from psycopg2.extras import RealDictCursor

data_bp = Blueprint("data", __name__, url_prefix="/data")


@data_bp.route("/user")
def user():
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        state = fetch_self_data(cur, session["user_id"])
        return jsonify(state)
    finally:
        cur.close()
        conn.close()

@data_bp.route("/planet")
def planet():
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


@data_bp.route("/here")
def here():
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
from flask import Blueprint, render_template, request, redirect, session
from db import get_db
from services.user_state import get_user_state

index_bp = Blueprint("index", __name__)

@index_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return render_template("top.jinja")

    conn = get_db()
    cur = conn.cursor()
    state = get_user_state(cur, session["user_id"])
    if state is None:
        session.clear()
        return redirect("/")
    cur.close()
    conn.close()

    if session.pop("show_landing", False):
        return render_template("landing.jinja", state=state)

    return render_template("planet.jinja", state=state)

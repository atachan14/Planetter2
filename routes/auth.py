from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from services.action.move import land_on_planet
from psycopg2.extras import RealDictCursor


from db import get_db

auth_bp = Blueprint("auth", __name__)
BEGINNERS_PLANET_ID = 1

@auth_bp.route("/login", methods=["POST"])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("top.jinja", error="未入力")

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT id, password_hash FROM users WHERE username = %s",
        (username,)
    )
    user = cur.fetchone()

    if user is None:
        # 新規作成
        password_hash = generate_password_hash(password)

        cur.execute(
            """
            INSERT INTO users (username, password_hash, planet_id)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (username, password_hash, BEGINNERS_PLANET_ID)
        )
        user_id = cur.fetchone()["id"]

        # 着陸
        land_on_planet(cur, user_id, BEGINNERS_PLANET_ID)
        conn.commit()

    else:
        user_id = user["id"]
        stored_hash = user["password_hash"]

        if not check_password_hash(stored_hash, password):
            return render_template("top.jinja", error="パスワードが違います")

    cur.close()
    conn.close()

    session["user_id"] = user_id
    return redirect("/")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")
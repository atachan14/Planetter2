from flask import Blueprint, render_template, request, redirect, session, Flask
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        # 未ログイン → top
        return render_template("top.jinja")

    # ログイン済み → main
    return render_template("main.jinja")


@auth_bp.route("/", methods=["POST"])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, password_hash FROM users WHERE username = %s",
        (username,)
    )
    user = cur.fetchone()

    if user is None:
        # 新規作成
        password_hash = generate_password_hash(password)
        
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
            (username, password_hash)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
    else:
        user_id, stored_hash = user

        if not check_password_hash(stored_hash, password):
            # パスワード間違い
            return render_template("top.jinja", error="パスワードが違います")

    cur.close()
    conn.close()

    # ★ ログイン成立
    session["user_id"] = user_id

    # ★ 入口に戻す
    return redirect("/")

from flask import Blueprint, render_template, request, redirect, session

index_bp = Blueprint("index", __name__)

@index_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return render_template("top.jinja")

    return render_template("main.jinja")

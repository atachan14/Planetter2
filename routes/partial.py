from flask import Blueprint, render_template, session, abort

partial_bp = Blueprint("partial", __name__, url_prefix="/partial")


@partial_bp.route("/landing")
def landing():
    if "user_id" not in session:
        abort(403)
    return render_template("landing.jinja")


@partial_bp.route("/planet")
def planet():
    if "user_id" not in session:
        abort(403)
    return render_template("planet.jinja")
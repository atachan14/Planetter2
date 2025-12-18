from flask import Blueprint, render_template, session, abort

partial_bp = Blueprint("partial", __name__, url_prefix="/partial")


@partial_bp.route("/landing")
def landing():
    return render_template("landing.jinja")

@partial_bp.route("/planet")
def planet():
    return render_template("planet.jinja")

# here
@partial_bp.route("/here/none")
def here_none():
    return render_template("here/none.jinja")

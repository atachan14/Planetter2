from flask import Blueprint
from routes.action.create import create_bp
from routes.action.move import move_bp
action_bp = Blueprint(
    "action",
    __name__,
    url_prefix="/action"   # ここは空でOK
)
action_bp.register_blueprint(create_bp)
action_bp.register_blueprint(move_bp)
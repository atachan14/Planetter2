from flask import Blueprint
from routes.action.create.post import post_bp

create_bp = Blueprint(
    "action_create",
    __name__,
    url_prefix="/create"
)

create_bp.register_blueprint(post_bp)
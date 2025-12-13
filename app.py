from flask import Flask
from routes.auth import auth_bp

app = Flask(__name__)
app.secret_key = "dev-secret-key"

app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

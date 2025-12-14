from flask import Flask
from routes.auth import auth_bp
from routes.index import index_bp
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "dev-secret-key"

app.register_blueprint(index_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

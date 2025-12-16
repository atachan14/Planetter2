from flask import Flask
from routes.auth import auth_bp
from routes.index import index_bp
from routes.partial import partial_bp
from routes.planet import planet_bp
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "dev-secret-key"

app.register_blueprint(index_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(planet_bp)

app.register_blueprint(partial_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

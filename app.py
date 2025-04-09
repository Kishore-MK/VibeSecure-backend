# app.py
from flask import Flask
from routes import scan, auth
from config import Config
from extensions import db
from models import Run, Issue  
from flask_migrate import Migrate
from flask_cors import CORS
import os

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get("SECRET_KEY")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = False

    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(scan.bp)
    app.register_blueprint(auth.bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200
    
    return app

def create_tables(app):
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app = create_app()
    create_tables(app)
    app.run(debug=True)
    

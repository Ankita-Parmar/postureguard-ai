# ============================================================
# backend/app.py
# Main Flask application entry point
# Run with: python app.py
# ============================================================

import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import route blueprints
from routes.auth    import auth_bp
from routes.posture import posture_bp
from routes.video   import video_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False   # tokens don't expire (for demo)

    # ── Extensions ─────────────────────────────────────────────────────────────
    # Allow React frontend (localhost:3000) to call Flask (localhost:5000)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    JWTManager(app)

    # ── Register Blueprints (route groups) ─────────────────────────────────────
    app.register_blueprint(auth_bp,    url_prefix="/api/auth")
    app.register_blueprint(posture_bp, url_prefix="/api/posture")
    app.register_blueprint(video_bp,   url_prefix="/api/video")

    # ── Health check route ─────────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "PostureGuard AI backend is running!"}

    return app

app = create_app()


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("  PostureGuard AI Backend Running")
    print("  URL: http://localhost:5000")
    print("  Health: http://localhost:5000/api/health")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

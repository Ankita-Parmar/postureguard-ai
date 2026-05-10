# ============================================================
# backend/routes/auth.py
# Authentication routes: Register & Login
#
# Routes:
#   POST /api/auth/register  → create new account
#   POST /api/auth/login     → login and get JWT token
# ============================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt
from utils.db import get_db_connection

# Create a Blueprint (a group of related routes)
auth_bp = Blueprint("auth", __name__)


# ── REGISTER ──────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    Expects JSON body: { "username": "...", "email": "...", "password": "..." }
    Returns: success message or error
    """
    data = request.get_json()

    # Validate required fields
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "username, email, and password are required"}), 400

    username = data["username"].strip()
    email    = data["email"].strip().lower()
    password = data["password"]

    # Basic validation
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Hash the password (bcrypt adds salt automatically)
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Save to database
    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pw.decode("utf-8"))
        )
        conn.commit()
        return jsonify({"message": "Account created successfully! Please log in."}), 201

    except Exception as e:
        # Likely a duplicate username/email (UNIQUE constraint)
        conn.rollback()
        error_msg = str(e)
        if "Duplicate entry" in error_msg:
            if "username" in error_msg:
                return jsonify({"error": "Username already taken"}), 409
            if "email" in error_msg:
                return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": "Registration failed. Please try again."}), 500

    finally:
        cursor.close()
        conn.close()


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login with username and password.
    Expects JSON body: { "username": "...", "password": "..." }
    Returns: JWT access token + user info
    """
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"error": "username and password are required"}), 400

    username = data["username"].strip()
    password = data["password"]

    # Look up user in database
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)   # returns dicts instead of tuples
    try:
        cursor.execute(
            "SELECT id, username, email, password FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        # Check user exists and password matches
        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return jsonify({"error": "Invalid username or password"}), 401

        # Create JWT token (identity = user id as string)
        token = create_access_token(identity=str(user["id"]))

        return jsonify({
            "message"     : "Login successful!",
            "access_token": token,
            "user": {
                "id"      : user["id"],
                "username": user["username"],
                "email"   : user["email"]
            }
        }), 200

    finally:
        cursor.close()
        conn.close()

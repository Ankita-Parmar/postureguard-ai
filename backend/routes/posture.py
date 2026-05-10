# ============================================================
# backend/routes/posture.py
# Posture data routes
#
# Routes:
#   POST /api/posture/save       → save a posture record
#   GET  /api/posture/history    → get user's posture history
#   GET  /api/posture/stats      → get risk level counts (for chart)
#   POST /api/posture/session/start  → start a session
#   POST /api/posture/session/end    → end a session
# ============================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import get_db_connection

posture_bp = Blueprint("posture", __name__)


# ── SAVE POSTURE RECORD ───────────────────────────────────────────────────────
@posture_bp.route("/save", methods=["POST"])
@jwt_required()        # user must be logged in (valid JWT token)
def save_posture():
    """
    Save a single posture snapshot to the database.
    Called every ~30 seconds from the frontend while monitoring.
    Expects JSON: { risk_level, neck_angle, shoulder_diff, nose_y, session_id (optional) }
    """
    user_id = int(get_jwt_identity())   # get user id from JWT token
    data    = request.get_json()

    if not data or "risk_level" not in data:
        return jsonify({"error": "risk_level is required"}), 400

    risk_level   = data.get("risk_level", "low")
    neck_angle   = data.get("neck_angle", 0.0)
    shoulder_diff= data.get("shoulder_diff", 0.0)
    nose_y       = data.get("nose_y", 0.0)
    session_id   = data.get("session_id")   # optional

    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO posture_records
               (user_id, session_id, risk_level, neck_angle, shoulder_diff, nose_y)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, session_id, risk_level, neck_angle, shoulder_diff, nose_y)
        )
        conn.commit()
        return jsonify({"message": "Posture record saved", "id": cursor.lastrowid}), 201
    finally:
        cursor.close()
        conn.close()


# ── GET POSTURE HISTORY ───────────────────────────────────────────────────────
@posture_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    """
    Get the last 50 posture records for the logged-in user.
    Used for the dashboard history table.
    """
    user_id = int(get_jwt_identity())
    limit   = int(request.args.get("limit", 50))

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id, risk_level, neck_angle, shoulder_diff, recorded_at
               FROM posture_records
               WHERE user_id = %s
               ORDER BY recorded_at DESC
               LIMIT %s""",
            (user_id, limit)
        )
        records = cursor.fetchall()
        # Convert datetime objects to strings for JSON
        for r in records:
            r["recorded_at"] = r["recorded_at"].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"history": records}), 200
    finally:
        cursor.close()
        conn.close()


# ── GET STATS (for pie/bar chart) ─────────────────────────────────────────────
@posture_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """
    Get risk level counts for the last 7 days.
    Returns: { low: N, medium: N, high: N }
    Used for the dashboard donut chart.
    """
    user_id = int(get_jwt_identity())

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT risk_level, COUNT(*) as count
               FROM posture_records
               WHERE user_id = %s
                 AND recorded_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
               GROUP BY risk_level""",
            (user_id,)
        )
        rows = cursor.fetchall()

        # Build a complete dict (fill 0 for missing levels)
        stats = {"low": 0, "medium": 0, "high": 0}
        for row in rows:
            stats[row["risk_level"]] = row["count"]

        return jsonify({"stats": stats}), 200
    finally:
        cursor.close()
        conn.close()


# ── START SESSION ─────────────────────────────────────────────────────────────
@posture_bp.route("/session/start", methods=["POST"])
@jwt_required()
def start_session():
    """Start a new monitoring session. Returns session_id."""
    user_id = int(get_jwt_identity())
    conn    = get_db_connection()
    cursor  = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO posture_sessions (user_id) VALUES (%s)", (user_id,)
        )
        conn.commit()
        return jsonify({"message": "Session started", "session_id": cursor.lastrowid}), 201
    finally:
        cursor.close()
        conn.close()


# ── END SESSION ───────────────────────────────────────────────────────────────
@posture_bp.route("/session/end", methods=["POST"])
@jwt_required()
def end_session():
    """
    End a monitoring session.
    Expects JSON: { session_id, total_minutes }
    """
    user_id    = int(get_jwt_identity())
    data       = request.get_json()
    session_id = data.get("session_id")
    total_min  = data.get("total_minutes", 0)

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE posture_sessions
               SET session_end = NOW(), total_minutes = %s
               WHERE id = %s AND user_id = %s""",
            (total_min, session_id, user_id)
        )
        conn.commit()
        return jsonify({"message": "Session ended"}), 200
    finally:
        cursor.close()
        conn.close()


# ── LOG ALERT ─────────────────────────────────────────────────────────────────
@posture_bp.route("/alert", methods=["POST"])
@jwt_required()
def log_alert():
    """
    Log an alert that was shown to the user.
    Expects JSON: { alert_type: "posture"|"stretch"|"walk", message: "..." }
    """
    user_id    = int(get_jwt_identity())
    data       = request.get_json()
    alert_type = data.get("alert_type", "posture")
    message    = data.get("message", "")

    conn   = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO alerts (user_id, alert_type, message) VALUES (%s, %s, %s)",
            (user_id, alert_type, message)
        )
        conn.commit()
        return jsonify({"message": "Alert logged"}), 201
    finally:
        cursor.close()
        conn.close()

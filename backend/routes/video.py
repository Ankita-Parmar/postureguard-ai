# ============================================================
# backend/routes/video.py
# Live webcam posture video stream route
#
# Route:
#   GET /api/video/stream  → MJPEG video stream with pose overlay
#   GET /api/video/analyze → analyze single frame, return JSON data
#
# HOW STREAMING WORKS:
#   Browser receives a multipart/x-mixed-replace response.
#   Each "part" is a JPEG frame. Browser displays them like a video.
# ============================================================

from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
import cv2
from utils.posture_analyzer import analyze_posture

video_bp = Blueprint("video", __name__)

# Global webcam capture object (shared across requests)
_camera = None

def get_camera():
    """Get or create the webcam capture object."""
    global _camera
    if _camera is None or not _camera.isOpened():
        _camera = cv2.VideoCapture(0)   # 0 = default webcam
        _camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        _camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return _camera


def generate_frames():
    """
    Generator function: yields JPEG frames continuously.
    Each frame has pose landmarks drawn and risk badge.
    This is what powers the live video in the browser.
    """
    camera = get_camera()

    while True:
        # Read one frame from webcam
        success, frame = camera.read()
        if not success:
            break

        # Flip horizontally (mirror effect, more natural for user)
        frame = cv2.flip(frame, 1)

        # Analyze posture and get annotated frame
        result = analyze_posture(frame)
        annotated = result["annotated_frame"]

        # Encode frame as JPEG
        ret, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue

        # Yield as multipart HTTP response part
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


# ── VIDEO STREAM ROUTE ────────────────────────────────────────────────────────
@video_bp.route("/stream")
def video_stream():
    """
    Returns a live MJPEG stream.
    The React frontend shows this in an <img src="/api/video/stream"> tag.
    No JWT required here (stream is shown on the monitoring page directly).
    """
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ── SINGLE FRAME ANALYSIS ─────────────────────────────────────────────────────
@video_bp.route("/analyze")
@jwt_required()
def analyze_frame():
    """
    Capture one frame from webcam, analyze it, return JSON data.
    Called by the frontend every 30 seconds to save posture data.
    Returns: risk_level, neck_angle, shoulder_diff, nose_y, message
    """
    camera = get_camera()
    success, frame = camera.read()

    if not success:
        return jsonify({"error": "Could not access webcam"}), 500

    frame  = cv2.flip(frame, 1)
    result = analyze_posture(frame)

    # Don't include the annotated_frame (not JSON serializable)
    return jsonify({
        "risk_level"   : result["risk_level"],
        "neck_angle"   : result["neck_angle"],
        "shoulder_diff": result["shoulder_diff"],
        "nose_y"       : result["nose_y"],
        "message"      : result["message"]
    }), 200


# ── RELEASE CAMERA ────────────────────────────────────────────────────────────
@video_bp.route("/stop", methods=["POST"])
def stop_camera():
    """Release the webcam when user stops monitoring."""
    global _camera
    if _camera and _camera.isOpened():
        _camera.release()
        _camera = None
    return jsonify({"message": "Camera released"}), 200

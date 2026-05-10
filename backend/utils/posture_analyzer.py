# ============================================================
# backend/utils/posture_analyzer.py
# Core posture analysis logic using MediaPipe Pose
#
# HOW IT WORKS:
#   1. Receive a video frame (from webcam via OpenCV)
#   2. Run MediaPipe to find 33 body landmarks
#   3. Calculate neck angle and shoulder asymmetry
#   4. Return risk level: "low", "medium", or "high"
# ============================================================

import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Pose detector
mp_pose     = mp.solutions.pose
mp_drawing  = mp.solutions.drawing_utils

# Create a Pose instance (static_image_mode=False for video)
pose_detector = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,           # 0=fast, 1=balanced, 2=accurate
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

def calculate_angle(point_a, point_b, point_c):
    """
    Calculate the angle at point_b formed by points a-b-c.
    Used to find neck tilt angle.
    Returns angle in degrees (0–180).
    """
    ax, ay = point_a
    bx, by = point_b
    cx, cy = point_c

    # Vector from B to A and B to C
    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)

    # Dot product and magnitudes
    dot    = ba[0]*bc[0] + ba[1]*bc[1]
    mag_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    mag_bc = math.sqrt(bc[0]**2 + bc[1]**2)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cos_angle = dot / (mag_ba * mag_bc)
    cos_angle = max(-1.0, min(1.0, cos_angle))   # clamp to [-1, 1]
    angle_deg = math.degrees(math.acos(cos_angle))
    return angle_deg


def analyze_posture(frame):
    """
    Main function: analyze a single video frame for posture.

    Args:
        frame: OpenCV BGR image (numpy array from webcam)

    Returns:
        dict with keys:
            risk_level    : "low" | "medium" | "high"
            neck_angle    : float (forward-head angle in degrees)
            shoulder_diff : float (shoulder height difference in px)
            nose_y        : float (nose y-coordinate, normalized 0–1)
            annotated_frame : frame with landmarks drawn on it
            message       : human-readable feedback string
    """

    # Convert BGR (OpenCV) to RGB (MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _   = frame.shape

    # Run pose detection
    results = pose_detector.process(rgb_frame)

    # Default return if no pose detected
    if not results.pose_landmarks:
        return {
            "risk_level"     : "low",
            "neck_angle"     : 0.0,
            "shoulder_diff"  : 0.0,
            "nose_y"         : 0.0,
            "annotated_frame": frame,
            "message"        : "No pose detected. Please sit in front of the camera."
        }

    landmarks = results.pose_landmarks.landmark

    # ── Extract key landmarks ──────────────────────────────────────────────────
    # MediaPipe landmark indices:
    #   0  = nose
    #   11 = left shoulder
    #   12 = right shoulder
    #   23 = left hip
    #   24 = right hip

    nose          = landmarks[mp_pose.PoseLandmark.NOSE]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder= landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip      = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip     = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

    # Convert normalized coords (0–1) to pixel coords
    nose_px           = (int(nose.x * w),           int(nose.y * h))
    left_shoulder_px  = (int(left_shoulder.x * w),  int(left_shoulder.y * h))
    right_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))
    left_hip_px       = (int(left_hip.x * w),       int(left_hip.y * h))

    # ── Metric 1: Neck Angle ───────────────────────────────────────────────────
    # Angle at shoulder between nose, shoulder, hip
    # Good posture = ~160–180° (upright)
    # Poor posture = <140°    (head forward / hunched)
    neck_angle = calculate_angle(nose_px, left_shoulder_px, left_hip_px)

    # ── Metric 2: Shoulder Asymmetry ──────────────────────────────────────────
    # Difference in y-pixel between left and right shoulders
    # Large difference = leaning/slouching sideways
    shoulder_diff = abs(left_shoulder_px[1] - right_shoulder_px[1])

    # ── Metric 3: Nose Y Position ─────────────────────────────────────────────
    # Normalized y position of the nose (0=top, 1=bottom)
    # If nose dips low in frame → user is leaning forward
    nose_y = nose.y

    # ── Risk Level Classification ─────────────────────────────────────────────
    # Thresholds (tuned for typical webcam setup):
    #   neck_angle < 140  → bad forward-head posture
    #   shoulder_diff > 30 → significant shoulder drop (sideways lean)
    #   neck_angle < 120  → severe forward head
    if neck_angle < 120 or shoulder_diff > 50:
        risk_level = "high"
        message    = "Poor posture detected! Sit upright and align your head over your shoulders."
        color      = (0, 0, 255)    # Red

    elif neck_angle < 145 or shoulder_diff > 25:
        risk_level = "medium"
        message    = "Moderate posture issue. Try straightening your back."
        color      = (0, 165, 255)  # Orange

    else:
        risk_level = "low"
        message    = "Good posture! Keep it up."
        color      = (0, 200, 0)    # Green

    # ── Draw landmarks on frame ───────────────────────────────────────────────
    annotated = frame.copy()

    # Draw pose skeleton
    mp_drawing.draw_landmarks(
        annotated,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
        connection_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,0), thickness=2)
    )

    # Draw risk level badge on frame
    cv2.rectangle(annotated, (10, 10), (350, 55), color, -1)
    cv2.putText(annotated, f"Risk: {risk_level.upper()}  |  Neck: {neck_angle:.1f} deg",
                (15, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    return {
        "risk_level"     : risk_level,
        "neck_angle"     : round(neck_angle, 2),
        "shoulder_diff"  : round(shoulder_diff, 2),
        "nose_y"         : round(nose_y, 4),
        "annotated_frame": annotated,
        "message"        : message
    }

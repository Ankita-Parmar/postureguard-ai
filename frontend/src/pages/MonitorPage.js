// src/pages/MonitorPage.js
// Live posture monitoring page
// Shows: webcam stream, risk badge, timer, stretch reminders, alerts

import React, { useState, useEffect, useRef, useCallback } from "react";
import API from "../utils/api";
import RiskBadge    from "../components/RiskBadge";
import AlertBanner  from "../components/AlertBanner";
import "./MonitorPage.css";

// How often (ms) to fetch posture analysis from backend and save to DB
const ANALYZE_INTERVAL  = 30000;   // 30 seconds
// How often to remind user to stretch (ms)
const STRETCH_INTERVAL  = 1800000; // 30 minutes
// How often to remind user to walk (ms)
const WALK_INTERVAL     = 3600000; // 60 minutes

export default function MonitorPage() {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [riskLevel,    setRiskLevel]    = useState("low");
  const [message,      setMessage]      = useState("Click Start to begin monitoring.");
  const [alerts,       setAlerts]       = useState([]);
  const [sessionId,    setSessionId]    = useState(null);
  const [elapsedSec,   setElapsedSec]   = useState(0);  // seconds since session start
  const [neckAngle,    setNeckAngle]    = useState(0);
  const [shoulderDiff, setShoulderDiff] = useState(0);

  // Refs for intervals (so we can clear them on stop)
  const analyzeTimerRef = useRef(null);
  const sessionTimerRef = useRef(null);
  const stretchTimerRef = useRef(null);
  const walkTimerRef    = useRef(null);

  // ── Format elapsed seconds as MM:SS ─────────────────────────────────────────
  function formatTime(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  // ── Add an alert to the banner (auto-removes after 8 seconds) ───────────────
  const pushAlert = useCallback((type, msg) => {
    const id = Date.now();
    setAlerts(prev => [...prev, { id, type, message: msg }]);
    // Log alert to backend
    API.post("/posture/alert", { alert_type: type, message: msg }).catch(() => {});
    // Auto remove after 8s
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.id !== id));
    }, 8000);
  }, []);

  // ── Fetch posture analysis from backend & save record ───────────────────────
  const analyzeAndSave = useCallback(async (sid) => {
    try {
      // Get current posture data from backend (it reads one webcam frame)
      const res = await API.get("/video/analyze");
      const { risk_level, neck_angle, shoulder_diff, nose_y, message: msg } = res.data;

      setRiskLevel(risk_level);
      setMessage(msg);
      setNeckAngle(neck_angle);
      setShoulderDiff(shoulder_diff);

      // Show alert if posture is bad
      if (risk_level === "high") {
        pushAlert("posture", msg);
      }

      // Save this posture record to the database
      await API.post("/posture/save", {
        risk_level, neck_angle, shoulder_diff, nose_y, session_id: sid,
      });
    } catch (err) {
      console.error("Posture analysis error:", err);
    }
  }, [pushAlert]);

  // ── START monitoring ─────────────────────────────────────────────────────────
  async function startMonitoring() {
    try {
      // Start a new session in DB
      const res = await API.post("/posture/session/start");
      const sid = res.data.session_id;
      setSessionId(sid);
      setElapsedSec(0);
      setAlerts([]);
      setIsMonitoring(true);

      // Analyze posture immediately, then every 30 seconds
      analyzeAndSave(sid);
      analyzeTimerRef.current = setInterval(() => analyzeAndSave(sid), ANALYZE_INTERVAL);

      // Count up elapsed seconds
      sessionTimerRef.current = setInterval(() => {
        setElapsedSec(prev => prev + 1);
      }, 1000);

      // Stretch reminder every 30 minutes
      stretchTimerRef.current = setInterval(() => {
        pushAlert("stretch", "🤸 Time to stretch! Stand up and do a 2-minute stretch.");
      }, STRETCH_INTERVAL);

      // Walk reminder every 60 minutes
      walkTimerRef.current = setInterval(() => {
        pushAlert("walk", "🚶 You've been sitting for a long time. Take a short walk!");
      }, WALK_INTERVAL);

    } catch (err) {
      alert("Could not start session. Is the backend running?");
    }
  }

  // ── STOP monitoring ──────────────────────────────────────────────────────────
  async function stopMonitoring() {
    // Clear all intervals
    clearInterval(analyzeTimerRef.current);
    clearInterval(sessionTimerRef.current);
    clearInterval(stretchTimerRef.current);
    clearInterval(walkTimerRef.current);
    setIsMonitoring(false);

    // End the session in DB, tell backend to release camera
    if (sessionId) {
      await API.post("/posture/session/end", {
        session_id: sessionId,
        total_minutes: Math.floor(elapsedSec / 60),
      });
    }
    await API.post("/video/stop").catch(() => {});
    setMessage("Session ended. Check Dashboard for your history.");
    setSessionId(null);
  }

  // Cleanup intervals when component unmounts
  useEffect(() => {
    return () => {
      clearInterval(analyzeTimerRef.current);
      clearInterval(sessionTimerRef.current);
      clearInterval(stretchTimerRef.current);
      clearInterval(walkTimerRef.current);
    };
  }, []);

  return (
    <div className="monitor-page">
      <h2 className="page-title">📷 Live Posture Monitor</h2>

      {/* Alerts */}
      <AlertBanner alerts={alerts} />

      <div className="monitor-layout">
        {/* Left: video feed */}
        <div className="video-section">
          <div className="video-wrapper">
            {isMonitoring ? (
              /* MediaPipe-annotated stream from Flask */
              <img
                src="http://localhost:5000/api/video/stream"
                alt="Posture live feed"
                className="video-feed"
              />
            ) : (
              <div className="video-placeholder">
                <span>📷</span>
                <p>Camera will start when you click <b>Start Monitoring</b></p>
              </div>
            )}
          </div>

          <div className="video-controls">
            {!isMonitoring ? (
              <button className="btn-start" onClick={startMonitoring}>▶ Start Monitoring</button>
            ) : (
              <button className="btn-stop" onClick={stopMonitoring}>⏹ Stop Monitoring</button>
            )}
          </div>
        </div>

        {/* Right: status panel */}
        <div className="status-section">
          {/* Timer */}
          <div className="stat-card">
            <div className="stat-label">⏱ Session Time</div>
            <div className="stat-value timer">{formatTime(elapsedSec)}</div>
          </div>

          {/* Risk badge */}
          <div className="stat-card">
            <div className="stat-label">Risk Level</div>
            <div className="stat-value"><RiskBadge level={riskLevel} /></div>
          </div>

          {/* Posture message */}
          <div className="stat-card message-card">
            <div className="stat-label">💬 Feedback</div>
            <p className="posture-msg">{message}</p>
          </div>

          {/* Metrics */}
          <div className="stat-card">
            <div className="stat-label">📐 Neck Angle</div>
            <div className="stat-value metric">{neckAngle}°</div>
            <div className="metric-hint">Ideal: &gt;145°</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">⬍ Shoulder Diff</div>
            <div className="stat-value metric">{shoulderDiff} px</div>
            <div className="metric-hint">Ideal: &lt;25 px</div>
          </div>

          {/* Tips */}
          <div className="tips-card">
            <div className="tips-title">💡 Posture Tips</div>
            <ul className="tips-list">
              <li>Keep your back straight against the chair</li>
              <li>Screen at eye level, ~50–70 cm away</li>
              <li>Feet flat on the floor</li>
              <li>Shoulders relaxed, not hunched</li>
              <li>Take a break every 30 minutes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

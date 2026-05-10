// src/components/AlertBanner.js
// Shows posture/stretch/walk alert messages at the top of the monitor page

import React from "react";
import "./AlertBanner.css";

export default function AlertBanner({ alerts }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="alert-banner">
      {alerts.map((alert, i) => (
        <div key={i} className={`alert-item alert-${alert.type}`}>
          <span className="alert-icon">
            {alert.type === "posture" ? "🪑" : alert.type === "stretch" ? "🤸" : "🚶"}
          </span>
          <span className="alert-msg">{alert.message}</span>
        </div>
      ))}
    </div>
  );
}

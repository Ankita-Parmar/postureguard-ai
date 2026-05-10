// src/components/RiskBadge.js
// Shows a coloured badge for risk level: LOW / MEDIUM / HIGH

import React from "react";
import "./RiskBadge.css";

const CONFIG = {
  low:    { label: "✅ LOW RISK",    cls: "badge-low"    },
  medium: { label: "⚠️ MEDIUM RISK", cls: "badge-medium" },
  high:   { label: "🚨 HIGH RISK",   cls: "badge-high"   },
};

export default function RiskBadge({ level }) {
  const cfg = CONFIG[level] || CONFIG.low;
  return <span className={`risk-badge ${cfg.cls}`}>{cfg.label}</span>;
}

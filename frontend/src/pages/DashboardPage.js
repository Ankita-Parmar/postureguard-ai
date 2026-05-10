// src/pages/DashboardPage.js
// Shows posture stats, donut chart, and history table

import React, { useState, useEffect } from "react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import API       from "../utils/api";
import RiskBadge from "../components/RiskBadge";
import "./DashboardPage.css";

// Register Chart.js components we need
ChartJS.register(ArcElement, Tooltip, Legend);

export default function DashboardPage() {
  const [stats,   setStats]   = useState({ low: 0, medium: 0, high: 0 });
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const username = localStorage.getItem("username");

  // Fetch data when page loads
  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, histRes] = await Promise.all([
          API.get("/posture/stats"),
          API.get("/posture/history?limit=20"),
        ]);
        setStats(statsRes.data.stats);
        setHistory(histRes.data.history);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Total records for summary
  const total = stats.low + stats.medium + stats.high;
  const goodPct = total > 0 ? Math.round((stats.low / total) * 100) : 0;

  // Chart.js donut data
  const chartData = {
    labels: ["Low Risk ✅", "Medium Risk ⚠️", "High Risk 🚨"],
    datasets: [{
      data: [stats.low, stats.medium, stats.high],
      backgroundColor: ["#34d399", "#fbbf24", "#f87171"],
      borderColor:     ["#059669", "#d97706", "#dc2626"],
      borderWidth: 2,
    }],
  };

  const chartOptions = {
    responsive: true,
    cutout: "68%",
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: "#94a3b8", padding: 16, font: { size: 13 } },
      },
    },
  };

  if (loading) return <div className="loading">⏳ Loading dashboard...</div>;

  return (
    <div className="dashboard-page">
      <div className="dash-header">
        <div>
          <h2>📊 Dashboard</h2>
          <p>Welcome back, <b>{username}</b> — here's your posture summary</p>
        </div>
      </div>

      {/* Summary cards */}
      <div className="summary-cards">
        <div className="sum-card">
          <div className="sum-icon">📋</div>
          <div className="sum-info">
            <div className="sum-value">{total}</div>
            <div className="sum-label">Total Records (7 days)</div>
          </div>
        </div>
        <div className="sum-card">
          <div className="sum-icon">✅</div>
          <div className="sum-info">
            <div className="sum-value" style={{color:"#34d399"}}>{stats.low}</div>
            <div className="sum-label">Good Posture Snapshots</div>
          </div>
        </div>
        <div className="sum-card">
          <div className="sum-icon">⚠️</div>
          <div className="sum-info">
            <div className="sum-value" style={{color:"#fbbf24"}}>{stats.medium}</div>
            <div className="sum-label">Medium Risk Snapshots</div>
          </div>
        </div>
        <div className="sum-card">
          <div className="sum-icon">🚨</div>
          <div className="sum-info">
            <div className="sum-value" style={{color:"#f87171"}}>{stats.high}</div>
            <div className="sum-label">High Risk Snapshots</div>
          </div>
        </div>
      </div>

      <div className="dash-body">
        {/* Donut chart */}
        <div className="chart-card">
          <h3>Risk Distribution (Last 7 Days)</h3>
          {total > 0 ? (
            <>
              <div className="chart-wrapper">
                <Doughnut data={chartData} options={chartOptions} />
              </div>
              <div className="good-pct">
                <span className="pct-value">{goodPct}%</span>
                <span className="pct-label">Good Posture</span>
              </div>
            </>
          ) : (
            <div className="no-data">
              <span>📷</span>
              <p>No data yet. Start monitoring to see your stats!</p>
            </div>
          )}
        </div>

        {/* History table */}
        <div className="history-card">
          <h3>Recent Posture History</h3>
          {history.length > 0 ? (
            <div className="table-wrapper">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Risk Level</th>
                    <th>Neck Angle</th>
                    <th>Shoulder Diff</th>
                    <th>Recorded At</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((rec, i) => (
                    <tr key={rec.id}>
                      <td>{i + 1}</td>
                      <td><RiskBadge level={rec.risk_level} /></td>
                      <td>{rec.neck_angle}°</td>
                      <td>{rec.shoulder_diff} px</td>
                      <td className="timestamp">{rec.recorded_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-data">
              <span>📋</span>
              <p>No history yet. Run a monitoring session first!</p>
            </div>
          )}
        </div>
      </div>

      {/* Advice panel */}
      <div className="advice-panel">
        <h3>🩺 Preventive Health Advice</h3>
        <div className="advice-grid">
          {[
            { icon:"🤸", title:"Stretch Every 30 Min", desc:"Stand, reach overhead, and roll your neck gently." },
            { icon:"💧", title:"Stay Hydrated",        desc:"Drink water regularly — dehydration causes muscle tension." },
            { icon:"🖥️", title:"Eye-Level Screen",     desc:"Top of your monitor should be at or slightly below eye level." },
            { icon:"🪑", title:"Lumbar Support",       desc:"Use a cushion or roll a towel for lower-back support." },
            { icon:"🚶", title:"Walk Every Hour",      desc:"A 5-minute walk improves circulation and reduces spinal load." },
            { icon:"😴", title:"Sleep Well",           desc:"7–8 hours of good sleep helps muscle recovery." },
          ].map(item => (
            <div className="advice-card" key={item.title}>
              <div className="advice-icon">{item.icon}</div>
              <div className="advice-title">{item.title}</div>
              <div className="advice-desc">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

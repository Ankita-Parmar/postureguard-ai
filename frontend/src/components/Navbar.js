// src/components/Navbar.js
import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const token     = localStorage.getItem("token");
  const username  = localStorage.getItem("username");

  // Hide navbar on login/register pages
  if (["/login", "/register"].includes(location.pathname)) return null;

  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="brand-icon">🧘</span>
        <span className="brand-name">PostureGuard AI</span>
      </div>

      <div className="navbar-links">
        <Link to="/monitor"   className={location.pathname === "/monitor"   ? "active" : ""}>📷 Monitor</Link>
        <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : ""}>📊 Dashboard</Link>
      </div>

      <div className="navbar-user">
        {token && <span className="username">👤 {username}</span>}
        <button className="btn-logout" onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  );
}

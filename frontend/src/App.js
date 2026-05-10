// src/App.js
// Root component — sets up React Router routes
// Pages: Login, Register, Monitor (posture cam), Dashboard

import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage     from "./pages/LoginPage";
import RegisterPage  from "./pages/RegisterPage";
import MonitorPage   from "./pages/MonitorPage";
import DashboardPage from "./pages/DashboardPage";
import Navbar        from "./components/Navbar";

// PrivateRoute: redirect to /login if user is not logged in
function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        {/* Public routes */}
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes (require login) */}
        <Route path="/monitor" element={
          <PrivateRoute><MonitorPage /></PrivateRoute>
        } />
        <Route path="/dashboard" element={
          <PrivateRoute><DashboardPage /></PrivateRoute>
        } />

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

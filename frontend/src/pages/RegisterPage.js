// src/pages/RegisterPage.js
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../utils/api";
import "./AuthPage.css";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form,    setForm]    = useState({ username: "", email: "", password: "", confirm: "" });
  const [error,   setError]   = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (form.password !== form.confirm) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await API.post("/auth/register", {
        username: form.username,
        email:    form.email,
        password: form.password,
      });
      setSuccess("Account created! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-logo">🧘</span>
          <h1>PostureGuard AI</h1>
          <p>Create your account</p>
        </div>

        {error   && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Username</label>
            <input type="text" name="username" placeholder="Choose a username"
              value={form.username} onChange={handleChange} required minLength={3} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" placeholder="your@email.com"
              value={form.email} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Min 6 characters"
              value={form.password} onChange={handleChange} required minLength={6} />
          </div>
          <div className="form-group">
            <label>Confirm Password</label>
            <input type="password" name="confirm" placeholder="Re-enter password"
              value={form.confirm} onChange={handleChange} required />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

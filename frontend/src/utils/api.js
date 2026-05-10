// src/utils/api.js
// Axios instance that automatically attaches JWT token to every request

import axios from "axios";

// Base URL of your Flask backend
const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

// Intercept every request → add Authorization header if token exists
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

export default API;

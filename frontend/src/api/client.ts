import axios from "axios";

// Base URL is configurable via VITE_API_URL so the app can point at a local
// backend during development; falls back to the hosted deployment.
export const API_BASE_URL =
  import.meta.env.VITE_API_URL ??
  "https://enterpriserag-production.up.railway.app";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

// Automatically attach token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

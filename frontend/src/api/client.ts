import axios from "axios";
import { clearStoredToken, getStoredToken } from "../utils/auth";

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
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearStoredToken();

      const publicPaths = ["/", "/login", "/signup"];
      if (!publicPaths.includes(window.location.pathname)) {
        const next = encodeURIComponent(
          `${window.location.pathname}${window.location.search}`,
        );
        window.location.assign(`/login?next=${next}`);
      }
    }

    return Promise.reject(error);
  },
);

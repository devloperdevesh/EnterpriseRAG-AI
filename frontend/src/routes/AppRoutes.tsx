import { BrowserRouter, Routes, Route } from "react-router-dom";

/* =========================================================
   LANDING
========================================================= */

import Landing from "../pages/Landing";

/* =========================================================
   AUTH
========================================================= */

import Login from "../auth/Login";
import Signup from "../auth/Signup";

/* =========================================================
   APPLICATION PAGES
========================================================= */

import Dashboard from "../pages/Dashboard";

import Chat from "../app/pages/Chat";
import Documents from "../app/pages/Documents";
import Analytics from "../app/pages/Analytics";
import Billing from "../app/pages/Billing";
import Settings from "../app/pages/Settings";

/* =========================================================
   LAYOUT
========================================================= */

import AppLayout from "../app/layout/AppLayout";
import ProtectedRoute from "./ProtectedRoute";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* =========================================================
            PUBLIC ROUTES
        ========================================================= */}

        <Route path="/" element={<Landing />} />

        <Route path="/login" element={<Login />} />

        <Route path="/signup" element={<Signup />} />

        {/* =========================================================
            APPLICATION ROUTES
        ========================================================= */}

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />

            <Route path="/chat" element={<Chat />} />

            <Route path="/documents" element={<Documents />} />

            <Route path="/analytics" element={<Analytics />} />

            <Route path="/billing" element={<Billing />} />

            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

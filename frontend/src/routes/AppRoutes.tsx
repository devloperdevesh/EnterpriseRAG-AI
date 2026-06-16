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
import ChunkVisualizer from "../app/pages/ChunkVisualizer";
import Documents from "../app/pages/Documents";
import Analytics from "../app/pages/Analytics";
import Settings from "../app/pages/Settings";

/* =========================================================
   LAYOUT
========================================================= */

import AppLayout from "../app/layout/AppLayout";

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

        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />

          <Route path="/chat" element={<Chat />} />

          <Route path="/chunks" element={<ChunkVisualizer />} />

          <Route path="/documents" element={<Documents />} />

          <Route path="/analytics" element={<Analytics />} />

          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

import { BrowserRouter, Routes, Route } from "react-router-dom";

/* PUBLIC PAGES */
import Home from "../marketing/pages/Home";
import Features from "../marketing/pages/Features";
import Pricing from "../marketing/pages/Pricing";
import About from "../marketing/pages/About";

/* APP PAGES */
import Dashboard from "../pages/Dashboard";
import Chat from "../app/pages/Chat";
import Documents from "../app/pages/Documents";

/* LAYOUTS */
import PublicLayout from "../marketing/layout/PublicLayout";
import AppLayout from "../app/layout/AppLayout";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* PUBLIC ROUTES */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/features" element={<Features />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/about" element={<About />} />
        </Route>

        {/* APP ROUTES */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/documents" element={<Documents />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;
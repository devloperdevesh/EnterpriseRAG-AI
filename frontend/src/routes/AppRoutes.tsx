import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "../marketing/pages/Home";
import Features from "../marketing/pages/Features";
import Pricing from "../marketing/pages/Pricing";
import About from "../marketing/pages/About";

import Dashboard from "../pages/Dashboard";
import Chat from "../app/pages/Chat";
import Documents from "../app/pages/Documents";

import Navbar from "../marketing/components/Navbar";
import Footer from "../marketing/components/Footer";
import AppLayout from "../app/layout/AppLayout";

function AppRoutes() {
  return (
    <BrowserRouter>

      <Navbar />

      <Routes>
        {/* Public */}
        <Route path="/" element={<Home />} />
        <Route path="/features" element={<Features />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/about" element={<About />} />

        {/* App */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/documents" element={<Documents />} />
          
        </Route>
        <Route path="/profile" element={<Profile />} />
<Route path="/settings" element={<Settings />} />
<Route path="/billing" element={<Billing />} />
<Route path="/team" element={<Team />} />
      </Routes>

      <Footer />

    </BrowserRouter>
  );
}

export default AppRoutes;
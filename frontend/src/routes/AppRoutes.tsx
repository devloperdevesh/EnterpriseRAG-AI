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
import Navbar from "../marketing/components/Navbar";
import Footer from "../marketing/components/Footer";
import AppLayout from "../app/layout/AppLayout";

/* OPTIONAL (ADD IF YOU USE THEM) */
// import Profile from "../app/pages/Profile";
// import Settings from "../app/pages/Settings";
// import Billing from "../app/pages/Billing";
// import Team from "../app/pages/Team";

function AppRoutes() {
  return (
    <BrowserRouter>

      {/* PUBLIC LAYOUT */}
      <Routes>

        {/* MARKETING PAGES (WITH NAVBAR + FOOTER) */}
        <Route
          path="/"
          element={
            <>
              <Navbar />
              <Home />
              <Footer />
            </>
          }
        />

        <Route
          path="/features"
          element={
            <>
              <Navbar />
              <Features />
              <Footer />
            </>
          }
        />

        <Route
          path="/pricing"
          element={
            <>
              <Navbar />
              <Pricing />
              <Footer />
            </>
          }
        />

        <Route
          path="/about"
          element={
            <>
              <Navbar />
              <About />
              <Footer />
            </>
          }
        />

        {/* APP ROUTES (NO NAVBAR/FOOTER) */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/documents" element={<Documents />} />

          {/* OPTIONAL */}
          {/* <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/team" element={<Team />} /> */}
        </Route>

      </Routes>

    </BrowserRouter>
  );
}

export default AppRoutes;
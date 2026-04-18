import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";

/* STYLES */
import "./styles/base/reset.css";
import "./styles/base/typography.css";

import "./styles/themes/colors.css";
import "./styles/themes/variables.css";

import "./styles/layout/container.css";
import "./styles/layout/navbar.css";

import "./styles/components/button.css";
import "./styles/components/card.css";

import "./styles/pages/home.css";
import "./styles/pages/dashboard.css";

import "./styles/utils/spacing.css";
import "./styles/utils/animations.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
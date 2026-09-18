/**
 * Browser entry point for the FileSentinel AI dashboard.
 * Author: Leslie Raya
 * GitHub: https://github.com/leslieraya555
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./App.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
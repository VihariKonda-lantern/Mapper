import React from "react";
import ReactDOM from "react-dom/client";
import StreamlitComponent from "./StreamlitComponent";

// Get args from Streamlit
function getArgs(): any {
  const args = new URLSearchParams(window.location.search).get("args");
  if (args) {
    try {
      return JSON.parse(decodeURIComponent(args));
    } catch (e) {
      return {};
    }
  }
  return {};
}

// Store args globally for component access
(window as any).streamlitComponentValue = getArgs();

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <StreamlitComponent />
  </React.StrictMode>
);

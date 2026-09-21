"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "bidsight_cookie_consent";

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    try {
      if (!localStorage.getItem(STORAGE_KEY)) {
        setVisible(true);
      }
    } catch {
      // localStorage unavailable (private mode, blocked storage) — skip the banner
    }
  }, []);

  function dismiss() {
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // ignore — nothing to opt into anyway, this just avoids re-showing the banner
    }
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <div
      role="dialog"
      aria-label="Cookie notice"
      style={{
        position: "fixed",
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1000,
        padding: "1rem 1.25rem",
        paddingBottom: "calc(1rem + env(safe-area-inset-bottom, 0px))",
        background: "#0D1117",
        color: "#F5F4F0",
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        justifyContent: "center",
        gap: "1rem",
        fontFamily: "'DM Sans', -apple-system, sans-serif",
      }}
    >
      <p style={{ fontSize: 13, lineHeight: 1.6, margin: 0, maxWidth: 640, color: "#D8D9DB" }}>
        We only use strictly-necessary cookies for login and payments — no
        analytics or ad tracking.{" "}
        <a href="/legal/cookies" style={{ color: "#5FD3A6", textDecoration: "underline" }}>
          Cookie Policy
        </a>
      </p>
      <button
        onClick={dismiss}
        style={{
          fontSize: 13,
          fontWeight: 500,
          background: "#1D9E75",
          color: "#04140F",
          border: "none",
          borderRadius: 6,
          padding: "0.5rem 1.1rem",
          cursor: "pointer",
          flexShrink: 0,
        }}
      >
        Got it
      </button>
    </div>
  );
}

import { useState } from "react";
import { AuditPage } from "./pages/AuditPage";
import { OraclePage } from "./pages/OraclePage";

type Tab = "oracle" | "audit";

export default function App() {
  const [tab, setTab] = useState<Tab>("oracle");

  return (
    <>
      <nav className="tab-nav">
        <button
          className={`tab-nav__item ${tab === "oracle" ? "tab-nav__item--active" : ""}`}
          onClick={() => setTab("oracle")}
        >
          🔮 Oracle
        </button>
        <button
          className={`tab-nav__item ${tab === "audit" ? "tab-nav__item--active" : ""}`}
          onClick={() => setTab("audit")}
        >
          📜 Audit Log
        </button>
      </nav>

      {tab === "oracle" ? <OraclePage /> : <AuditPage />}
    </>
  );
}

/**
 * Operational dashboard for FileSentinel AI.
 *
 * Presents service health, explainable alerts, anomaly evidence, aggregate
 * statistics, and recent file-system telemetry.
 *
 * Author: Leslie Raya
 * GitHub: https://github.com/leslieraya555
 */

import { useCallback, useEffect, useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const REFRESH_INTERVAL_MS = 5000;

const EMPTY_STATS = {
  total_events: 0,
  create_events: 0,
  modify_events: 0,
  delete_events: 0,
  rename_events: 0,
  access_events: 0,
};

function riskTone(score) {
  if (score >= 80) return "critical";
  if (score >= 50) return "warning";
  return "safe";
}

function formatTimestamp(value) {
  if (!value) return "Not available";
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? value : timestamp.toLocaleString();
}

function StatCard({ label, value, tone = "neutral" }) {
  return (
    <article className={`stat-card ${tone}`}>
      <span>{label}</span>
      <strong>{value.toLocaleString()}</strong>
    </article>
  );
}

function App() {
  const [overview, setOverview] = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // One overview request keeps statistics and alerts aligned to the same snapshot.
  const fetchOverview = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/overview?limit=100`, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      setOverview(await response.json());
      setBackendStatus("healthy");
      setError("");
    } catch (requestError) {
      setBackendStatus("offline");
      setError(`Dashboard refresh failed: ${requestError.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview();
    const interval = window.setInterval(fetchOverview, REFRESH_INTERVAL_MS);
    return () => window.clearInterval(interval);
  }, [fetchOverview]);

  const stats = overview?.stats ?? EMPTY_STATS;
  const events = overview?.events ?? [];
  const alerts = overview?.rule_alerts ?? [];
  const mlAlert = overview?.ml_alert ?? {
    status: "WAITING",
    risk_score: 0,
    message: "Waiting for an assessment.",
    features: null,
  };
  const riskClass = riskTone(mlAlert.risk_score);

  const sortedEvents = useMemo(
    () => [...events].sort((left, right) => right.timestamp.localeCompare(left.timestamp)),
    [events],
  );

  return (
    <main className="page-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Linux endpoint defense</p>
          <h1>FileSentinel <span>AI</span></h1>
          <p className="subtitle">
            Explainable file-system monitoring with behavioral rules and anomaly detection.
          </p>
        </div>
        <div className="hero-actions">
          <div className={`service-status ${backendStatus}`}>
            <span className="status-dot" aria-hidden="true" />
            API {backendStatus}
          </div>
          <button type="button" onClick={fetchOverview} disabled={loading}>
            {loading ? "Refreshing…" : "Refresh now"}
          </button>
        </div>
      </header>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <section className="stats-grid" aria-label="Event totals">
        <StatCard label="Total events" value={stats.total_events} />
        <StatCard label="Created" value={stats.create_events} tone="info" />
        <StatCard label="Modified" value={stats.modify_events} tone="warning" />
        <StatCard label="Deleted" value={stats.delete_events} tone="critical" />
        <StatCard label="Renamed" value={stats.rename_events} tone="purple" />
        <StatCard label="Accessed" value={stats.access_events} tone="safe" />
      </section>

      <section className="analysis-grid">
        <article className="panel risk-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Machine-learning assessment</p>
              <h2>{mlAlert.status.replaceAll("_", " ")}</h2>
            </div>
            <div className={`risk-ring ${riskClass}`} aria-label={`Risk score ${mlAlert.risk_score} out of 100`}>
              <strong>{mlAlert.risk_score}</strong>
              <span>/ 100</span>
            </div>
          </div>
          <p>{mlAlert.message}</p>
          {mlAlert.features && (
            <dl className="feature-grid">
              {Object.entries(mlAlert.features).map(([name, value]) => (
                <div key={name}>
                  <dt>{name.replaceAll("_", " ")}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Explainable detections</p>
              <h2>Rule alerts</h2>
            </div>
            <span className={`alert-count ${alerts.length ? "active" : ""}`}>{alerts.length}</span>
          </div>
          {alerts.length === 0 ? (
            <div className="empty-state">
              <strong>No thresholds exceeded</strong>
              <span>Recent activity does not match a configured bulk-operation rule.</span>
            </div>
          ) : (
            <div className="alert-list">
              {alerts.map((alert) => (
                <div className={`alert-item ${alert.severity.toLowerCase()}`} key={alert.type}>
                  <div>
                    <span>{alert.severity}</span>
                    <strong>{alert.type.replaceAll("_", " ")}</strong>
                  </div>
                  <p>{alert.message}</p>
                  <small>Recommended: {alert.recommended_action}</small>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>

      <section className="panel telemetry-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Latest validated records</p>
            <h2>Event telemetry</h2>
          </div>
          <span className="updated-at">Updated {formatTimestamp(overview?.generated_at)}</span>
        </div>

        {sortedEvents.length === 0 ? (
          <div className="empty-state">
            <strong>No telemetry available</strong>
            <span>Start the Linux agent or run the safe simulation script.</span>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event</th>
                  <th>File</th>
                  <th>Path</th>
                </tr>
              </thead>
              <tbody>
                {sortedEvents.map((event, index) => (
                  <tr key={`${event.timestamp}-${event.event_type}-${event.file_path}-${index}`}>
                    <td>{formatTimestamp(event.timestamp)}</td>
                    <td><span className={`event-badge ${event.event_type.toLowerCase()}`}>{event.event_type}</span></td>
                    <td>{event.file_name}</td>
                    <td className="path-cell" title={event.file_path}>{event.file_path}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer>
        <span>FileSentinel AI v2.0</span>
        <span>Designed and engineered by Leslie Raya</span>
      </footer>
    </main>
  );
}

export default App;

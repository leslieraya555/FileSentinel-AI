import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [ruleAlerts, setRuleAlerts] = useState([]);
  const [mlAlert, setMlAlert] = useState(null);
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const fetchData = async () => {
    try {
      const healthResponse = await axios.get(`${API_BASE_URL}/health`);
      setBackendStatus(healthResponse.data.status);

      const eventsResponse = await axios.get(`${API_BASE_URL}/events`);
      const statsResponse = await axios.get(`${API_BASE_URL}/stats`);
      const ruleResponse = await axios.get(`${API_BASE_URL}/alerts/rules`);
      const mlResponse = await axios.get(`${API_BASE_URL}/alerts/ml`);

      setEvents(eventsResponse.data);
      setStats(statsResponse.data);
      setRuleAlerts(ruleResponse.data);
      setMlAlert(mlResponse.data);
    } catch (error) {
      setBackendStatus("offline");
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();

    const interval = setInterval(fetchData, 3000);

    return () => clearInterval(interval);
  }, []);

  const getRiskClass = (score) => {
    if (score >= 80) return "risk-high";
    if (score >= 50) return "risk-medium";
    return "risk-low";
  };

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>FileSentinel AI</h1>
          <p>AI-Powered Linux File-System Security Monitor</p>
        </div>

        <div className={`status ${backendStatus === "healthy" ? "online" : "offline"}`}>
          Backend: {backendStatus}
        </div>
      </header>

      <section className="grid">
        <div className="card">
          <h2>ML Risk Status</h2>

          {mlAlert ? (
            <>
              <p className="label">Status</p>
              <h3>{mlAlert.status}</h3>

              <p className="label">Risk Score</p>
              <div className={`risk-score ${getRiskClass(mlAlert.risk_score)}`}>
                {mlAlert.risk_score}/100
              </div>

              <p>{mlAlert.message}</p>
            </>
          ) : (
            <p>No ML status available.</p>
          )}
        </div>

        <div className="card">
          <h2>Event Stats</h2>

          {stats ? (
            <div className="stats">
              <p>Total Events: <strong>{stats.total_events}</strong></p>
              <p>Create: <strong>{stats.create_events}</strong></p>
              <p>Modify: <strong>{stats.modify_events}</strong></p>
              <p>Delete: <strong>{stats.delete_events}</strong></p>
              <p>Rename: <strong>{stats.rename_events}</strong></p>
              <p>Access: <strong>{stats.access_events}</strong></p>
            </div>
          ) : (
            <p>No stats available.</p>
          )}
        </div>
      </section>

      <section className="card">
        <h2>Rule-Based Alerts</h2>

        {ruleAlerts.length === 0 ? (
          <p className="safe">No rule-based alerts detected.</p>
        ) : (
          <div className="alerts">
            {ruleAlerts.map((alert, index) => (
              <div className="alert" key={index}>
                <div>
                  <strong>{alert.severity}</strong> — {alert.type}
                </div>
                <p>{alert.message}</p>
                <p>Risk Score: {alert.risk_score}/100</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="card">
        <h2>Recent File Events</h2>

        {events.length === 0 ? (
          <p>No file events yet. Start the C monitor and modify files in your watch folder.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event Type</th>
                  <th>File Name</th>
                  <th>File Path</th>
                </tr>
              </thead>

              <tbody>
                {events.slice().reverse().map((event, index) => (
                  <tr key={index}>
                    <td>{event.timestamp}</td>
                    <td>{event.event_type}</td>
                    <td>{event.file_name}</td>
                    <td>{event.file_path}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
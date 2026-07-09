import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [mlAlert, setMlAlert] = useState(null);

  const fetchData = async () => {
    try {
      const health = await axios.get(`${API_BASE_URL}/health`);
      const eventsRes = await axios.get(`${API_BASE_URL}/events`);
      const statsRes = await axios.get(`${API_BASE_URL}/stats`);
      const mlRes = await axios.get(`${API_BASE_URL}/alerts/ml`);

      setBackendStatus(health.data.status);
      setEvents(eventsRes.data);
      setStats(statsRes.data);
      setMlAlert(mlRes.data);
    } catch (error) {
      setBackendStatus("offline");
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>FileSentinel AI</h1>
          <p>AI-Powered Linux File-System Security Monitor</p>
        </div>
        <div className={backendStatus === "healthy" ? "online" : "offline"}>
          Backend: {backendStatus}
        </div>
      </header>

      <section className="grid">
        <div className="card">
          <h2>ML Risk Status</h2>
          {mlAlert ? (
            <>
              <h3>{mlAlert.status}</h3>
              <p className="risk">Risk Score: {mlAlert.risk_score}/100</p>
              <p>{mlAlert.message}</p>
            </>
          ) : (
            <p>No ML status yet.</p>
          )}
        </div>

        <div className="card">
          <h2>Event Stats</h2>
          {stats ? (
            <>
              <p>Total Events: {stats.total_events}</p>
              <p>Create: {stats.create_events}</p>
              <p>Modify: {stats.modify_events}</p>
              <p>Delete: {stats.delete_events}</p>
              <p>Rename: {stats.rename_events}</p>
              <p>Access: {stats.access_events}</p>
            </>
          ) : (
            <p>No stats yet.</p>
          )}
        </div>
      </section>

      <section className="card">
        <h2>Recent File Events</h2>
        {events.length === 0 ? (
          <p>No file events yet. Add test events to data/events.csv.</p>
        ) : (
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
              {events.map((event, index) => (
                <tr key={index}>
                  <td>{event.timestamp}</td>
                  <td>{event.event_type}</td>
                  <td>{event.file_name}</td>
                  <td>{event.file_path}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}

export default App;

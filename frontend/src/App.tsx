import './App.css';
import ChatPanel from './components/ChatPanel';
import UploadSidebar from './components/UploadSidebar';

function App() {
  return (
    <div className="app-shell">
      {/* ── Left Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="app-logo">
            <div className="logo-icon">⚡</div>
            <span className="app-name gradient-text">MultimodRAG</span>
          </div>
          <p className="app-tagline">Intelligent Document Intelligence</p>
        </div>

        <div className="sidebar-body">
          <UploadSidebar />
        </div>

        <div className="sidebar-footer">
          <div className="status-row">
            <div className="status-dot" />
            <span>Services online · localhost:8006</span>
          </div>
        </div>
      </aside>

      {/* ── Main Chat Panel ── */}
      <main className="main-panel">
        <ChatPanel />
      </main>
    </div>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import EventDashboard from './pages/EventDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/events" element={<EventDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import EventDashboard from './pages/EventDashboard';
import DesignDashboard from './pages/DesignDashboard';
import Pricing from './pages/Pricing';
import Signup from './pages/Signup';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/events" element={<EventDashboard />} />
        <Route path="/design" element={<DesignDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

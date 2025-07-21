import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from '@/pages/Home';
import Dashboard from '@/pages/Dashboard';
import EventDashboard from '@/pages/EventDashboard';
import DesignDashboard from '@/pages/DesignDashboard';
import AdminDashboard from '@/pages/AdminDashboard';
import ProjectView from '@/pages/ProjectView';
import QADashboard from '@/pages/QADashboard';
import OpsDashboard from '@/pages/OpsDashboard';
import TechStackDashboard from '@/pages/TechStackDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/events" element={<EventDashboard />} />
        <Route path="/design" element={<DesignDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/project/:projectId" element={<ProjectView />} />
        <Route path="/qa" element={<QADashboard />} />
        <Route path="/ops" element={<OpsDashboard />} />
        <Route path="/techstack" element={<TechStackDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from '@/pages/Home';
import Dashboard from '@/pages/Dashboard';
import EventDashboard from '@/pages/EventDashboard';
import DesignDashboard from '@/pages/DesignDashboard';
import AdminDashboard from '@/pages/AdminDashboard';
import Pricing from '@/pages/Pricing';
import Signup from '@/pages/Signup';
import SubmitIdea from '@/pages/SubmitIdea';
import ChatWidget from './components/ChatWidget';
import FAQPage from './pages/FAQ';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navigation />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/submit-idea" element={<SubmitIdea />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/signin" element={<Signup />} />
            <Route path="/faq" element={<FAQPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/events" element={<EventDashboard />} />
            <Route path="/design" element={<DesignDashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </main>
        <ChatWidget />
      </div>
    </Router>
  );
}

export default App;

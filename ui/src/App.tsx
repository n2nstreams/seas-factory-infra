import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Home from '@/pages/Home';
import Dashboard from '@/pages/Dashboard';
import EventDashboard from '@/pages/EventDashboard';
import DesignDashboard from '@/pages/DesignDashboard';
import AdminDashboard from '@/pages/AdminDashboard';
import Pricing from '@/pages/Pricing';
import Signup from '@/pages/Signup';
import SignIn from '@/pages/SignIn';
import SubmitIdea from '@/pages/SubmitIdea';
import ChatWidget from './components/ChatWidget';
import FAQPage from './pages/FAQ';
import PrivacyPolicy from '@/pages/PrivacyPolicy';
import DPA from '@/pages/DPA';
import Navigation from './components/Navigation';
import './App.css';

function AppContent() {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <div className="flex flex-col min-h-screen">
      {!isHomePage && <Navigation />}
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/submit-idea" element={<SubmitIdea />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/faq" element={<FAQPage />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/dpa" element={<DPA />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/events" element={<EventDashboard />} />
          <Route path="/design" element={<DesignDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </main>
      <ChatWidget />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;

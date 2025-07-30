import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { useState, useEffect, createContext, useContext } from 'react';
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
import TermsOfService from '@/pages/TermsOfService';
import DPA from '@/pages/DPA';
import Navigation from './components/Navigation';
import './App.css';

// User Context for authentication state
interface User {
  id: string;
  name: string;
  email: string;
  plan: 'starter' | 'pro' | 'growth';
  buildHours: {
    used: number;
    total: number | 'unlimited';
  };
}

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // Load user from localStorage on app start
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleSetUser = (newUser: User | null) => {
    setUser(newUser);
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser));
    } else {
      localStorage.removeItem('user');
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, setUser: handleSetUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function AppContent() {
  const location = useLocation();
  const isHomePage = location.pathname === '/';
  const { user, logout } = useAuth();

  return (
    <div className="flex flex-col min-h-screen">
      {!isHomePage && <Navigation user={user || undefined} onSignOut={logout} />}
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/submit-idea" element={<SubmitIdea />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/faq" element={<FAQPage />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
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
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;

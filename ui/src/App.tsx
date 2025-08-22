import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
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
import Marketplace from './pages/Marketplace';
import Billing from './pages/Billing';
import Settings from './pages/Settings';
import PrivacyPolicy from '@/pages/PrivacyPolicy';
import TermsOfService from '@/pages/TermsOfService';
import DPA from '@/pages/DPA';
import Navigation from './components/Navigation';
import './App.css';
import { tenantUtils } from '@/lib/api';
import { sessionUtils } from '@/lib/userPreferences';

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

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

function ProtectedRoute({ children, redirectTo = '/signin' }: ProtectedRouteProps) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  // Load user from localStorage on app start
  useEffect(() => {
    const savedUser = sessionUtils.getCurrentUser();
    if (savedUser) {
      setUser(savedUser);
      // Sync tenant context with loaded user
      tenantUtils.syncWithUser(savedUser);
    }
  }, []);

  const handleSetUser = (newUser: User | null) => {
    setUser(newUser);
    if (newUser) {
      sessionUtils.initializeSession(newUser);
      // Sync tenant context with user authentication
      tenantUtils.syncWithUser(newUser);
    } else {
      sessionUtils.clearSession();
      // Clear tenant context when user logs out
      tenantUtils.clearTenantContext();
    }
  };

  const logout = () => {
    setUser(null);
    sessionUtils.clearSession();
    // Clear tenant context when user logs out
    tenantUtils.clearTenantContext();
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
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/dpa" element={<DPA />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/billing" element={
            <ProtectedRoute>
              <Billing />
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
          <Route path="/events" element={
            <ProtectedRoute>
              <EventDashboard />
            </ProtectedRoute>
          } />
          <Route path="/design" element={
            <ProtectedRoute>
              <DesignDashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          } />
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

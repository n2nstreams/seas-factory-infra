import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Menu, X, User, Settings, LogOut, ChevronDown, Home, Package, Activity, CreditCard, Clock, Lightbulb } from 'lucide-react';
import { Link } from 'react-router-dom';

interface NavigationProps {
  currentPage?: string;
  user?: {
    name: string;
    email: string;
    plan: 'starter' | 'pro' | 'growth';
    buildHours: {
      used: number;
      total: number | 'unlimited';
    };
  };
  onSignOut?: () => void;
}

export default function Navigation({ currentPage, user, onSignOut }: NavigationProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const navItems = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Submit Idea', href: '/submit-idea', icon: Lightbulb },
    { name: 'Pricing', href: '/pricing', icon: Package },
    { name: 'Dashboard', href: '/dashboard', icon: Activity, requiresAuth: true },
  ];

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'starter':
        return 'bg-blue-600 text-white';
      case 'pro':
        return 'bg-accent text-white';
      case 'growth':
        return 'bg-purple-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  const getPlanDisplayName = (plan: string) => {
    switch (plan) {
      case 'starter':
        return 'Starter';
      case 'pro':
        return 'Pro';
      case 'growth':
        return 'Growth';
      default:
        return 'Free';
    }
  };

  const getBuildHoursColor = (used: number, total: number | 'unlimited') => {
    if (total === 'unlimited') return 'text-green-600';
    const percentage = (used / total) * 100;
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <nav className="glass-nav sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H9V3H7V1H5V7L1 9V11L7 13V21H9V19H11V21H13V19H15V21H17V13L23 11V9H21ZM19 10.5L17 11.5V17H15V15H13V17H11V15H9V17H7V11.5L5 10.5V9.5L7 8.5V7H9V9H11V7H13V9H15V7H17V8.5L19 9.5V10.5Z"/>
              </svg>
            </div>
            <span className="text-xl font-bold text-heading">Forge95</span>
          </div>

          {/* Desktop Navigation */}
          <div className="ml-6 hidden md:flex items-center space-x-6 text-sm">
            <Link to="/" className="text-muted-foreground transition-colors hover:text-primary">
              Home
            </Link>
            <Link to="/submit-idea" className="text-muted-foreground transition-colors hover:text-primary">
              Submit Idea
            </Link>
            <Link to="/marketplace" className="text-muted-foreground transition-colors hover:text-primary font-medium">
              🏪 Marketplace
            </Link>
            <Link to="/pricing" className="text-muted-foreground transition-colors hover:text-primary">
              Pricing
            </Link>
            <Link to="/faq" className="text-muted-foreground transition-colors hover:text-primary">
              FAQ
            </Link>
          </div>

          {/* User Section */}
          {user ? (
            <div className="flex items-center space-x-4">
              {/* Plan Badge */}
              <Badge className={`text-xs ${getPlanColor(user.plan)}`}>
                {getPlanDisplayName(user.plan)}
              </Badge>

              {/* Build Hours Indicator */}
              <div className="hidden lg:flex items-center space-x-2 glass-card px-3 py-1">
                <Clock className="w-4 h-4 text-accent" />
                <span className={`text-sm font-medium ${getBuildHoursColor(user.buildHours.used, user.buildHours.total)}`}>
                  {user.buildHours.used}
                  {user.buildHours.total !== 'unlimited' && `/${user.buildHours.total}`}
                </span>
              </div>

              {/* User Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 btn-ghost p-2 rounded-xl"
                  aria-label="Toggle user menu"
                >
                  <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <ChevronDown className="w-4 h-4 text-body" />
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-64 card-glass py-2 shadow-lg">
                    <div className="px-4 py-3 border-b border-stone-200/50">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                          <User className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="font-medium text-heading">{user.name}</p>
                          <p className="text-sm text-body">{user.email}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="px-4 py-3 border-b border-stone-200/50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-body">Plan</span>
                        <Badge className={`text-xs ${getPlanColor(user.plan)}`}>
                          {getPlanDisplayName(user.plan)}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-body">Build Hours</span>
                        <span className={`text-sm font-medium ${getBuildHoursColor(user.buildHours.used, user.buildHours.total)}`}>
                          {user.buildHours.used}
                          {user.buildHours.total !== 'unlimited' && `/${user.buildHours.total}`}
                        </span>
                      </div>
                    </div>

                    <div className="py-2">
                      <Link
                        to="/dashboard"
                        className="flex items-center space-x-3 px-4 py-2 text-sm text-body hover:bg-stone-100/50 hover:text-heading transition-colors"
                      >
                        <Activity className="w-4 h-4" />
                        <span>Dashboard</span>
                      </Link>
                      <Link
                        to="/profile"
                        className="flex items-center space-x-3 px-4 py-2 text-sm text-body hover:bg-stone-100/50 hover:text-heading transition-colors"
                      >
                        <User className="w-4 h-4" />
                        <span>Profile</span>
                      </Link>
                      <Link
                        to="/billing"
                        className="flex items-center space-x-3 px-4 py-2 text-sm text-body hover:bg-stone-100/50 hover:text-heading transition-colors"
                      >
                        <CreditCard className="w-4 h-4" />
                        <span>Billing</span>
                      </Link>
                      <Link
                        to="/settings"
                        className="flex items-center space-x-3 px-4 py-2 text-sm text-body hover:bg-stone-100/50 hover:text-heading transition-colors"
                      >
                        <Settings className="w-4 h-4" />
                        <span>Settings</span>
                      </Link>
                    </div>

                    <div className="border-t border-stone-200/50 pt-2">
                      <button
                        onClick={onSignOut}
                        className="flex items-center space-x-3 px-4 py-2 text-sm text-body hover:bg-stone-100/50 hover:text-heading transition-colors w-full text-left"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-4">
              <Link
                to="/signin"
                className="text-body hover:text-heading transition-colors font-medium"
              >
                Sign In
              </Link>
              <Button asChild className="btn-primary">
                <Link to="/signup">Get Started</Link>
              </Button>
            </div>
          )}

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="btn-ghost p-2"
              aria-label="Toggle navigation menu"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden pb-4">
            <div className="glass-card p-4 space-y-4">
              <Link to="/" className="flex items-center space-x-3 p-3 rounded-lg transition-colors text-body hover:bg-stone-100/50 hover:text-heading">
                <Home className="w-5 h-5" />
                <span className="font-medium">Home</span>
              </Link>
              <Link to="/submit-idea" className="flex items-center space-x-3 p-3 rounded-lg transition-colors text-body hover:bg-stone-100/50 hover:text-heading">
                <Lightbulb className="w-5 h-5" />
                <span className="font-medium">Submit Idea</span>
              </Link>
              <Link to="/marketplace" className="flex items-center space-x-3 p-3 rounded-lg transition-colors text-body hover:bg-stone-100/50 hover:text-heading">
                <Package className="w-5 h-5" />
                <span className="font-medium">Marketplace</span>
              </Link>
              {navItems.map((item) => {
                if (item.requiresAuth && !user) return null;
                
                const isActive = currentPage === item.href || 
                               (item.href === '/' && currentPage === '/') ||
                               (item.href !== '/' && currentPage?.startsWith(item.href));
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-stone-100/50 text-heading' 
                        : 'text-body hover:bg-stone-100/50 hover:text-heading'
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                );
              })}
              <Link to="/faq" className="flex items-center space-x-3 p-3 rounded-lg transition-colors text-body hover:bg-stone-100/50 hover:text-heading">
                <Lightbulb className="w-5 h-5" />
                <span className="font-medium">FAQ</span>
              </Link>

              {user ? (
                <div className="pt-4 border-t border-stone-200/50 space-y-4">
                  <div className="flex items-center space-x-3 p-3 glass-card">
                    <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center">
                      <User className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-heading">{user.name}</p>
                      <p className="text-sm text-body">{user.email}</p>
                    </div>
                    <Badge className={`text-xs ${getPlanColor(user.plan)}`}>
                      {getPlanDisplayName(user.plan)}
                    </Badge>
                  </div>

                  <div className="glass-card p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-body">Build Hours</span>
                      <span className={`text-sm font-medium ${getBuildHoursColor(user.buildHours.used, user.buildHours.total)}`}>
                        {user.buildHours.used}
                        {user.buildHours.total !== 'unlimited' && `/${user.buildHours.total}`}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Link
                      to="/billing"
                      className="flex items-center space-x-3 p-3 text-body hover:bg-stone-100/50 hover:text-heading transition-colors rounded-lg"
                      onClick={() => setIsOpen(false)}
                    >
                      <CreditCard className="w-5 h-5" />
                      <span>Billing</span>
                    </Link>
                    <Link
                      to="/settings"
                      className="flex items-center space-x-3 p-3 rounded-lg transition-colors text-body hover:bg-stone-100/50 hover:text-heading"
                      onClick={() => setIsOpen(false)}
                    >
                      <Settings className="w-5 h-5" />
                      <span>Settings</span>
                    </Link>
                    <button
                      onClick={() => {
                        onSignOut?.();
                        setIsOpen(false);
                      }}
                      className="flex items-center space-x-3 p-3 text-body hover:bg-stone-100/50 hover:text-heading transition-colors rounded-lg w-full text-left"
                    >
                      <LogOut className="w-5 h-5" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="pt-4 border-t border-stone-200/50 space-y-2">
                  <Link
                    to="/signin"
                    className="flex items-center justify-center p-3 text-body hover:bg-stone-100/50 hover:text-heading transition-colors rounded-lg"
                    onClick={() => setIsOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Button asChild className="btn-primary w-full">
                    <Link to="/signup" onClick={() => setIsOpen(false)}>
                      Get Started
                    </Link>
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
} 
import { useState, useEffect } from 'react';
import { useAuth } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  User, 
  Mail, 
  Building, 
  Globe, 
  Phone, 
  MapPin, 
  Calendar,
  Shield,
  Key,
  Save,
  Edit,
  Eye,
  EyeOff,
  RefreshCw
} from 'lucide-react';

interface ProfileData {
  firstName: string;
  lastName: string;
  email: string;
  company: string;
  website: string;
  phone: string;
  location: string;
  bio: string;
}

interface SecuritySettings {
  twoFactorEnabled: boolean;
  sessionTimeout: number;
  passwordLastChanged: string;
  loginHistory: Array<{
    date: string;
    location: string;
    device: string;
    ip: string;
  }>;
}

export default function Profile() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [profileData, setProfileData] = useState<ProfileData>({
    firstName: user?.name?.split(' ')[0] || '',
    lastName: user?.name?.split(' ').slice(1).join(' ') || '',
    email: user?.email || '',
    company: '',
    website: '',
    phone: '',
    location: '',
    bio: ''
  });

  const [securitySettings, setSecuritySettings] = useState<SecuritySettings>({
    twoFactorEnabled: false,
    sessionTimeout: 24,
    passwordLastChanged: new Date().toISOString().split('T')[0],
    loginHistory: [
      {
        date: new Date().toISOString(),
        location: 'San Francisco, CA',
        device: 'Chrome on MacOS',
        ip: '192.168.1.1'
      }
    ]
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  useEffect(() => {
    // Load profile data from API or localStorage
    const loadProfileData = async () => {
      try {
        // TODO: Replace with actual API call
        const savedData = localStorage.getItem('userProfile');
        if (savedData) {
          setProfileData(JSON.parse(savedData));
        }
      } catch (error) {
        console.error('Error loading profile data:', error);
      }
    };

    loadProfileData();
  }, []);

  const handleProfileChange = (field: keyof ProfileData, value: string) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
  };

  const handlePasswordChange = (field: keyof typeof passwordData, value: string) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveProfile = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      localStorage.setItem('userProfile', JSON.stringify(profileData));
      setIsEditing(false);
      // Show success message
    } catch (error) {
      console.error('Error saving profile:', error);
      // Show error message
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      alert('New password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      // Show success message
    } catch (error) {
      console.error('Error changing password:', error);
      // Show error message
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTwoFactor = () => {
    setSecuritySettings(prev => ({
      ...prev,
      twoFactorEnabled: !prev.twoFactorEnabled
    }));
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-homepage flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-heading" />
          <p className="text-heading">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Glassmorphism Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-20 w-72 h-72 bg-gradient-to-tl from-green-800/20 to-stone-700/25 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 py-8 relative z-10">
        <div className="space-y-8">
          {/* Header */}
          <div className="glass-card p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
              <div>
                <h1 className="text-3xl xl:text-4xl font-bold text-heading">Profile Settings</h1>
                <p className="text-body mt-1">Manage your account information and preferences</p>
              </div>
              <div className="flex items-center space-x-4">
                {isEditing ? (
                  <>
                    <Button 
                      variant="outline" 
                      className="btn-secondary"
                      onClick={() => setIsEditing(false)}
                      disabled={isLoading}
                    >
                      Cancel
                    </Button>
                    <Button 
                      className="btn-primary"
                      onClick={handleSaveProfile}
                      disabled={isLoading}
                    >
                      {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                      Save Changes
                    </Button>
                  </>
                ) : (
                  <Button 
                    className="btn-primary"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Profile
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Main Content Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="glass-card p-1 w-full">
              <TabsTrigger value="profile" className="btn-ghost">
                <User className="w-4 h-4 mr-2" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="security" className="btn-ghost">
                <Shield className="w-4 h-4 mr-2" />
                Security
              </TabsTrigger>
              <TabsTrigger value="preferences" className="btn-ghost">
                <Key className="w-4 h-4 mr-2" />
                Preferences
              </TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="space-y-6">
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Basic Information */}
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <User className="w-5 h-5 mr-2" />
                      Basic Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="firstName">First Name</Label>
                        <Input
                          id="firstName"
                          value={profileData.firstName}
                          onChange={(e) => handleProfileChange('firstName', e.target.value)}
                          disabled={!isEditing}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="lastName">Last Name</Label>
                        <Input
                          id="lastName"
                          value={profileData.lastName}
                          onChange={(e) => handleProfileChange('lastName', e.target.value)}
                          disabled={!isEditing}
                          className="mt-1"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profileData.email}
                        disabled
                        className="mt-1 bg-gray-50"
                      />
                      <p className="text-xs text-body mt-1">Email cannot be changed</p>
                    </div>

                    <div>
                      <Label htmlFor="bio">Bio</Label>
                      <textarea
                        id="bio"
                        value={profileData.bio}
                        onChange={(e) => handleProfileChange('bio', e.target.value)}
                        disabled={!isEditing}
                        rows={3}
                        className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-50"
                        placeholder="Tell us about yourself..."
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Contact Information */}
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <Mail className="w-5 h-5 mr-2" />
                      Contact Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="company">Company</Label>
                      <Input
                        id="company"
                        value={profileData.company}
                        onChange={(e) => handleProfileChange('company', e.target.value)}
                        disabled={!isEditing}
                        className="mt-1"
                        placeholder="Your company name"
                      />
                    </div>

                    <div>
                      <Label htmlFor="website">Website</Label>
                      <Input
                        id="website"
                        value={profileData.website}
                        onChange={(e) => handleProfileChange('website', e.target.value)}
                        disabled={!isEditing}
                        className="mt-1"
                        placeholder="https://yourwebsite.com"
                      />
                    </div>

                    <div>
                      <Label htmlFor="phone">Phone</Label>
                      <Input
                        id="phone"
                        value={profileData.phone}
                        onChange={(e) => handleProfileChange('phone', e.target.value)}
                        disabled={!isEditing}
                        className="mt-1"
                        placeholder="+1 (555) 123-4567"
                      />
                    </div>

                    <div>
                      <Label htmlFor="location">Location</Label>
                      <Input
                        id="location"
                        value={profileData.location}
                        onChange={(e) => handleProfileChange('location', e.target.value)}
                        disabled={!isEditing}
                        className="mt-1"
                        placeholder="City, State, Country"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Account Information */}
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Building className="w-5 h-5 mr-2" />
                    Account Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center p-4 glass-card">
                      <div className="w-12 h-12 bg-accent-icon rounded-xl flex items-center justify-center mx-auto mb-3">
                        <User className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-heading mb-1">Plan</h3>
                      <Badge className="bg-accent text-white capitalize">{user.plan}</Badge>
                    </div>
                    
                    <div className="text-center p-4 glass-card">
                      <div className="w-12 h-12 bg-accent-secondary rounded-xl flex items-center justify-center mx-auto mb-3">
                        <Calendar className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-heading mb-1">Member Since</h3>
                      <p className="text-body text-sm">January 2025</p>
                    </div>
                    
                    <div className="text-center p-4 glass-card">
                      <div className="w-12 h-12 bg-accent-tertiary rounded-xl flex items-center justify-center mx-auto mb-3">
                        <Key className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-heading mb-1">User ID</h3>
                      <p className="text-body text-sm font-mono text-xs">{user.id}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="security" className="space-y-6">
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Password Change */}
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <Key className="w-5 h-5 mr-2" />
                      Change Password
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="currentPassword">Current Password</Label>
                      <div className="relative mt-1">
                        <Input
                          id="currentPassword"
                          type={showPassword ? "text" : "password"}
                          value={passwordData.currentPassword}
                          onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                          className="pr-10"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </Button>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="newPassword">New Password</Label>
                      <Input
                        id="newPassword"
                        type={showPassword ? "text" : "password"}
                        value={passwordData.newPassword}
                        onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="confirmPassword">Confirm New Password</Label>
                      <Input
                        id="confirmPassword"
                        type={showPassword ? "text" : "password"}
                        value={passwordData.confirmPassword}
                        onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                        className="mt-1"
                      />
                    </div>

                    <Button 
                      className="btn-primary w-full"
                      onClick={handleChangePassword}
                      disabled={isLoading}
                    >
                      {isLoading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                      Change Password
                    </Button>
                  </CardContent>
                </Card>

                {/* Security Settings */}
                <Card className="card-glass">
                  <CardHeader>
                    <CardTitle className="text-heading flex items-center">
                      <Shield className="w-5 h-5 mr-2" />
                      Security Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between p-4 glass-card">
                      <div>
                        <h3 className="font-medium text-heading">Two-Factor Authentication</h3>
                        <p className="text-sm text-body">Add an extra layer of security</p>
                      </div>
                      <Button
                        variant={securitySettings.twoFactorEnabled ? "default" : "outline"}
                        onClick={toggleTwoFactor}
                        className={securitySettings.twoFactorEnabled ? "bg-green-600 hover:bg-green-700" : ""}
                      >
                        {securitySettings.twoFactorEnabled ? "Enabled" : "Enable"}
                      </Button>
                    </div>

                    <div className="p-4 glass-card">
                      <h3 className="font-medium text-heading mb-2">Session Timeout</h3>
                      <select
                        aria-label="Session timeout"
                        value={securitySettings.sessionTimeout}
                        onChange={(e) => setSecuritySettings(prev => ({
                          ...prev,
                          sessionTimeout: parseInt(e.target.value)
                        }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      >
                        <option value={1}>1 hour</option>
                        <option value={8}>8 hours</option>
                        <option value={24}>24 hours</option>
                        <option value={168}>1 week</option>
                      </select>
                    </div>

                    <div className="p-4 glass-card">
                      <h3 className="font-medium text-heading mb-2">Password Last Changed</h3>
                      <p className="text-body">{new Date(securitySettings.passwordLastChanged).toLocaleDateString()}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Login History */}
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Calendar className="w-5 h-5 mr-2" />
                    Recent Login Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {securitySettings.loginHistory.map((login, index) => (
                      <div key={index} className="flex items-center justify-between p-4 glass-card">
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <div>
                            <p className="font-medium text-heading">{login.location}</p>
                            <p className="text-sm text-body">{login.device}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-heading">{new Date(login.date).toLocaleDateString()}</p>
                          <p className="text-xs text-body">{login.ip}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="preferences" className="space-y-6">
              <Card className="card-glass">
                <CardHeader>
                  <CardTitle className="text-heading flex items-center">
                    <Key className="w-5 h-5 mr-2" />
                    Account Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-body">Preferences settings will be available soon.</p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

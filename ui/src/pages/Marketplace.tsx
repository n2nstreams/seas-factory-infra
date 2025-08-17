import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { 
  Search, 
  Star, 
  Users, 
  Zap, 
  TrendingUp,
  Globe,
  Code2,
  ShoppingCart,
  Eye
} from 'lucide-react';

interface SaaSProduct {
  id: string;
  name: string;
  description: string;
  category: string;
  price: string;
  rating: number;
  users: number;
  status: 'live' | 'beta' | 'coming-soon';
  image: string;
  features: string[];
  techStack: string[];
}

const mockProducts: SaaSProduct[] = [
  {
    id: '1',
    name: 'TaskFlow Pro',
    description: 'AI-powered project management with automated task prioritization and team collaboration.',
    category: 'Productivity',
    price: '$29/month',
    rating: 4.8,
    users: 1250,
    status: 'live',
    image: '/api/placeholder/300/200',
    features: ['AI Task Prioritization', 'Team Collaboration', 'Time Tracking', 'Analytics Dashboard'],
    techStack: ['React', 'Node.js', 'PostgreSQL', 'OpenAI API']
  },
  {
    id: '2',
    name: 'LeadGen AI',
    description: 'Automated lead generation and qualification using machine learning algorithms.',
    category: 'Sales',
    price: '$49/month',
    rating: 4.6,
    users: 890,
    status: 'live',
    image: '/api/placeholder/300/200',
    features: ['Lead Scoring', 'Email Automation', 'CRM Integration', 'Analytics'],
    techStack: ['Vue.js', 'Python', 'MongoDB', 'TensorFlow']
  },
  {
    id: '3',
    name: 'ContentCraft',
    description: 'AI content creation platform for blogs, social media, and marketing campaigns.',
    category: 'Marketing',
    price: '$39/month',
    rating: 4.7,
    users: 2100,
    status: 'live',
    image: '/api/placeholder/300/200',
    features: ['AI Writing Assistant', 'SEO Optimization', 'Content Calendar', 'Performance Analytics'],
    techStack: ['Next.js', 'TypeScript', 'Supabase', 'GPT-4']
  },
  {
    id: '4',
    name: 'DataViz Studio',
    description: 'Interactive data visualization and business intelligence platform.',
    category: 'Analytics',
    price: '$79/month',
    rating: 4.9,
    users: 650,
    status: 'beta',
    image: '/api/placeholder/300/200',
    features: ['Interactive Charts', 'Real-time Data', 'Custom Dashboards', 'Export Options'],
    techStack: ['React', 'D3.js', 'FastAPI', 'ClickHouse']
  },
  {
    id: '5',
    name: 'SecureChat',
    description: 'End-to-end encrypted messaging platform for enterprise teams.',
    category: 'Communication',
    price: '$19/month',
    rating: 4.5,
    users: 3200,
    status: 'live',
    image: '/api/placeholder/300/200',
    features: ['End-to-End Encryption', 'File Sharing', 'Video Calls', 'Admin Controls'],
    techStack: ['React Native', 'WebRTC', 'Signal Protocol', 'Redis']
  },
  {
    id: '6',
    name: 'InvoiceFlow',
    description: 'Automated invoicing and payment processing for small businesses.',
    category: 'Finance',
    price: '$25/month',
    rating: 4.4,
    users: 1800,
    status: 'live',
    image: '/api/placeholder/300/200',
    features: ['Auto-Invoicing', 'Payment Processing', 'Expense Tracking', 'Tax Calculations'],
    techStack: ['Angular', 'Java', 'MySQL', 'Stripe API']
  }
];

const categories = ['All', 'Productivity', 'Sales', 'Marketing', 'Analytics', 'Communication', 'Finance'];

export default function Marketplace() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sortBy, setSortBy] = useState<'rating' | 'users' | 'name'>('rating');

  const filteredProducts = mockProducts
    .filter(product => 
      (selectedCategory === 'All' || product.category === selectedCategory) &&
      (product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
       product.description.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'users':
          return b.users - a.users;
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live':
        return 'bg-green-100 text-green-800';
      case 'beta':
        return 'bg-blue-100 text-blue-800';
      case 'coming-soon':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 to-green-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-stone-900 mb-4">
            SaaS Marketplace
          </h1>
          <p className="text-xl text-stone-600 max-w-3xl mx-auto">
            Discover AI-powered SaaS solutions built by our platform. From productivity tools to enterprise solutions, 
            find the perfect software for your business needs.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-stone-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search SaaS products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-stone-300 rounded-md bg-white text-stone-900 focus:outline-none focus:ring-2 focus:ring-green-600"
                aria-label="Filter by category"
              >
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'rating' | 'users' | 'name')}
                className="px-4 py-2 border border-stone-300 rounded-md bg-white text-stone-900 focus:outline-none focus:ring-2 focus:ring-green-600"
                aria-label="Sort products by"
              >
                <option value="rating">Sort by Rating</option>
                <option value="users">Sort by Users</option>
                <option value="name">Sort by Name</option>
              </select>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
              <div className="relative">
                <div className="h-48 bg-gradient-to-br from-green-100 to-stone-100 flex items-center justify-center">
                  <Code2 className="w-16 h-16 text-green-600" />
                </div>
                <Badge className={`absolute top-3 right-3 ${getStatusColor(product.status)}`}>
                  {product.status === 'live' ? 'Live' : product.status === 'beta' ? 'Beta' : 'Coming Soon'}
                </Badge>
              </div>
              
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg text-stone-900">{product.name}</CardTitle>
                  <span className="text-lg font-bold text-green-600">{product.price}</span>
                </div>
                <p className="text-sm text-stone-600 line-clamp-2">{product.description}</p>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Stats */}
                <div className="flex items-center justify-between text-sm text-stone-600">
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span>{product.rating}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4 text-blue-500" />
                    <span>{product.users.toLocaleString()}</span>
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-stone-900">Key Features</h4>
                  <div className="flex flex-wrap gap-1">
                    {product.features.slice(0, 3).map((feature, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Tech Stack */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-stone-900">Tech Stack</h4>
                  <div className="flex flex-wrap gap-1">
                    {product.techStack.slice(0, 3).map((tech, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>

              <div className="px-6 pb-6 space-y-3">
                <Button className="w-full btn-primary">
                  <Eye className="w-4 h-4 mr-2" />
                  View Demo
                </Button>
                <Button variant="outline" className="w-full">
                  <ShoppingCart className="w-4 h-4 mr-2" />
                  Get Started
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {filteredProducts.length === 0 && (
          <div className="text-center py-12">
            <Code2 className="w-16 h-16 text-stone-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-stone-900 mb-2">No products found</h3>
            <p className="text-stone-600">Try adjusting your search or filters to find what you're looking for.</p>
          </div>
        )}

        {/* Stats Section */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm border border-stone-200">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-stone-900 mb-2">Platform Statistics</h2>
            <p className="text-stone-600">See the impact of our AI-powered SaaS factory</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">50+</div>
              <div className="text-stone-600">SaaS Products Built</div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">48h</div>
              <div className="text-stone-600">Average Build Time</div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">10K+</div>
              <div className="text-stone-600">Active Users</div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="w-8 h-8 text-yellow-600" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">15+</div>
              <div className="text-stone-600">Countries Served</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

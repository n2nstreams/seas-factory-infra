import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Star,
  Users,
  Zap,
  TrendingUp,
  Globe,
  Code2,
  ShoppingCart,
  Eye,
  ExternalLink,
  Check,
  X
} from 'lucide-react';
import { marketplaceApi, tenantUtils } from '@/lib/api';

interface SaaSProduct {
  id: string;
  name: string;
  description: string;
  category: string;
  price: string;
  rating: number;
  users: number;
  status: string;
  image: string;
  features: string[];
  techStack: string[];
  demo_available: boolean;
  demo_url?: string;
  screenshots: string[];
  pricing_plans: Array<{
    name: string;
    price: string;
    features: string[];
  }>;
}

interface ProductDemo {
  product_id: string;
  product_name: string;
  demo_url: string;
  screenshots: string[];
  features: string[];
  pricing_plans: Array<{
    name: string;
    price: string;
    features: string[];
  }>;
  description: string;
}

export default function Marketplace() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('rating');
  const [isLoading, setIsLoading] = useState(false);
  const [products, setProducts] = useState<SaaSProduct[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<SaaSProduct | null>(null);
  const [productDemo, setProductDemo] = useState<ProductDemo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  // Initialize tenant context
  useEffect(() => {
    tenantUtils.initializeTenantContext();
  }, []);

  // Load products and categories
  useEffect(() => {
    loadProducts();
    loadCategories();
  }, [searchTerm, selectedCategory, sortBy]);

  const loadProducts = async () => {
    try {
      setIsLoading(true);
      const filters: any = {};

      if (searchTerm) filters.search = searchTerm;
      if (selectedCategory && selectedCategory !== 'All') filters.category = selectedCategory;
      if (sortBy) filters.sortBy = sortBy;

      const productsData = await marketplaceApi.getProducts(filters);
      setProducts(productsData);
    } catch (error) {
      console.error('Error loading products:', error);
      // Fallback to empty array
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const categoriesData = await marketplaceApi.getCategories();
      setCategories(categoriesData.categories);
    } catch (error) {
      console.error('Error loading categories:', error);
      setCategories(['All']);
    }
  };

  const handleViewDemo = async (product: SaaSProduct) => {
    if (!product.demo_available) {
      alert(`Demo for ${product.name} is not available yet. Please check back soon!`);
      return;
    }

    setSelectedProduct(product);
    setIsModalOpen(true);
    setIsDemoLoading(true);

    try {
      const demoData = await marketplaceApi.getProductDemo(product.id);
      setProductDemo(demoData);
    } catch (error) {
      console.error('Error loading demo:', error);
      alert(`Demo for ${product.name} is not available yet. Please check back soon!`);
      setIsModalOpen(false);
    } finally {
      setIsDemoLoading(false);
    }
  };

  const handleGetStarted = async (product: SaaSProduct) => {
    try {
      setIsLoading(true);

      const onboardingData = await marketplaceApi.startProductOnboarding(product.id);
      console.log('Onboarding started:', onboardingData);

      // Redirect to signup with product pre-selected
      window.location.href = onboardingData.redirect_url;

    } catch (error) {
      console.error('Error starting onboarding:', error);
      // Fallback to regular signup
      window.location.href = '/signup';
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live':
        return 'bg-green-800/20 text-green-800 border-green-700/40';
      case 'beta':
        return 'bg-stone-700/20 text-stone-700 border-stone-600/40';
      case 'coming-soon':
        return 'bg-stone-600/20 text-stone-700 border-stone-500/40';
      default:
        return 'bg-stone-100 text-stone-800 border-stone-200';
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
          <p className="text-xl text-stone-600 max-w-3xl mx-auto mb-8">
            Discover AI-powered SaaS solutions built by our platform. From productivity tools to enterprise solutions,
            find the perfect software for your business needs.
          </p>

          {/* Marketplace CTA */}
          <div className="bg-gradient-to-r from-green-800/10 to-green-900/10 backdrop-blur-lg border border-green-800/20 rounded-2xl p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-stone-900 mb-3">
              🚀 Ready to Build Your Own SaaS?
            </h3>
            <p className="text-stone-700 mb-4">
              Submit your idea and join the founders who've already launched profitable businesses
            </p>
            <Button
              size="lg"
              className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800"
              onClick={() => window.location.href = '/submit-idea'}
            >
              Submit Your Idea
            </Button>
          </div>
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
                className="px-4 py-2 border border-stone-300 rounded-md bg-white text-stone-900 focus:outline-none focus:ring-2 focus:ring-green-800"
                aria-label="Filter by category"
              >
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'rating' | 'users' | 'name')}
                className="px-4 py-2 border border-stone-300 rounded-md bg-white text-stone-900 focus:outline-none focus:ring-2 focus:ring-green-800"
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
          {isLoading ? (
            // Loading state
            Array.from({ length: 6 }).map((_, index) => (
              <Card key={index} className="overflow-hidden border border-stone-200">
                <div className="h-48 bg-gradient-to-br from-stone-100 to-stone-200 animate-pulse" />
                <CardHeader className="pb-3">
                  <div className="h-6 bg-stone-200 rounded animate-pulse mb-2" />
                  <div className="h-4 bg-stone-200 rounded animate-pulse" />
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="h-4 bg-stone-200 rounded animate-pulse" />
                  <div className="h-4 bg-stone-200 rounded animate-pulse" />
                </CardContent>
              </Card>
            ))
          ) : (
            products.map((product) => (
              <Card key={product.id} className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:scale-[1.02] border border-stone-200 hover:border-green-800">
                <div className="relative">
                  <div className="h-48 bg-gradient-to-br from-green-800/10 to-stone-700/10 flex items-center justify-center group-hover:from-green-800/20 group-hover:to-stone-700/20 transition-colors">
                    <div className="text-center">
                      <Code2 className="w-16 h-16 text-green-800 mx-auto mb-2" />
                      <p className="text-sm text-green-800 font-medium">{product.category}</p>
                    </div>
                  </div>
                  <Badge className={`absolute top-3 right-3 ${getStatusColor(product.status)}`}>
                    {product.status === 'live' ? 'Live' : product.status === 'beta' ? 'Beta' : 'Coming Soon'}
                  </Badge>
                  {/* Price Badge */}
                  <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full border border-stone-200">
                    <span className="text-sm font-bold text-green-800">{product.price}</span>
                  </div>
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
                      <Users className="w-4 h-4 text-stone-600" />
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
                  <Button
                    className={`w-full text-white ${product.demo_available
                      ? 'bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800'
                      : 'bg-stone-400 cursor-not-allowed'
                    }`}
                    onClick={() => handleViewDemo(product)}
                    disabled={isLoading || !product.demo_available}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    {isLoading ? 'Loading...' : product.demo_available ? 'View Demo' : 'Demo Not Available'}
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full border-green-800 text-green-800 hover:bg-green-800/10 hover:border-green-700"
                    onClick={() => handleGetStarted(product)}
                    disabled={isLoading}
                  >
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    {isLoading ? 'Loading...' : 'Get Started'}
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>

        {/* Empty State */}
        {products.length === 0 && (
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
              <div className="w-16 h-16 bg-green-800/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-green-800" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">50+</div>
              <div className="text-stone-600">SaaS Products Built</div>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-stone-700/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-stone-700" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">48h</div>
              <div className="text-stone-600">Average Build Time</div>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-stone-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-stone-700" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">10K+</div>
              <div className="text-stone-600">Active Users</div>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-stone-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="w-8 h-8 text-stone-600" />
              </div>
              <div className="text-3xl font-bold text-stone-900 mb-2">15+</div>
              <div className="text-stone-600">Countries Served</div>
            </div>
          </div>
        </div>
      </div>

      {/* Product Detail Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {selectedProduct && (
            <>
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold text-stone-900">
                  {selectedProduct.name}
                </DialogTitle>
                <DialogDescription className="text-stone-600">
                  {selectedProduct.description}
                </DialogDescription>
              </DialogHeader>

              {isDemoLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-800 mx-auto mb-4"></div>
                    <p className="text-stone-600">Loading demo...</p>
                  </div>
                </div>
              ) : productDemo ? (
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="demo">Live Demo</TabsTrigger>
                    <TabsTrigger value="features">Features</TabsTrigger>
                    <TabsTrigger value="pricing">Pricing</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-3xl font-bold text-green-800">{selectedProduct.price}</span>
                          <Badge className={getStatusColor(selectedProduct.status)}>
                            {selectedProduct.status === 'live' ? 'Live' : selectedProduct.status === 'beta' ? 'Beta' : 'Coming Soon'}
                          </Badge>
                        </div>

                        <div className="flex items-center space-x-4 text-sm text-stone-600">
                          <div className="flex items-center space-x-1">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span>{selectedProduct.rating}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Users className="w-4 h-4 text-stone-600" />
                            <span>{selectedProduct.users.toLocaleString()} users</span>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <h4 className="font-medium text-stone-900">Category</h4>
                          <Badge variant="outline">{selectedProduct.category}</Badge>
                        </div>

                        <div className="space-y-2">
                          <h4 className="font-medium text-stone-900">Tech Stack</h4>
                          <div className="flex flex-wrap gap-1">
                            {selectedProduct.techStack.map((tech, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {tech}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="font-medium text-stone-900">Key Features</h4>
                        <div className="space-y-2">
                          {selectedProduct.features.map((feature, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <Check className="w-4 h-4 text-green-600" />
                              <span className="text-sm text-stone-700">{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="demo" className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-stone-900">Live Demo</h3>
                      <div className="bg-stone-50 border border-stone-200 rounded-lg p-6 text-center">
                        <ExternalLink className="w-12 h-12 text-stone-400 mx-auto mb-4" />
                        <p className="text-stone-600 mb-4">
                          Click below to open the live demo in a new tab
                        </p>
                        <Button
                          className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-white"
                          onClick={() => window.open(productDemo.demo_url, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4 mr-2" />
                          Open Live Demo
                        </Button>
                      </div>

                      {productDemo.screenshots.length > 0 && (
                        <div className="space-y-4">
                          <h4 className="font-medium text-stone-900">Screenshots</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {productDemo.screenshots.map((screenshot, index) => (
                              <div key={index} className="bg-stone-100 rounded-lg p-4">
                                <img
                                  src={screenshot}
                                  alt={`Screenshot ${index + 1}`}
                                  className="w-full h-48 object-cover rounded"
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="features" className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-stone-900">All Features</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {selectedProduct.features.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-3 p-3 bg-stone-50 rounded-lg">
                            <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                            <span className="text-stone-700">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="pricing" className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-stone-900">Pricing Plans</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {productDemo.pricing_plans.map((plan, index) => (
                          <Card key={index} className="border border-stone-200">
                            <CardHeader>
                              <CardTitle className="text-lg">{plan.name}</CardTitle>
                              <div className="text-2xl font-bold text-green-800">{plan.price}</div>
                            </CardHeader>
                            <CardContent>
                              <ul className="space-y-2">
                                {plan.features.map((feature, featureIndex) => (
                                  <li key={featureIndex} className="flex items-center space-x-2 text-sm">
                                    <Check className="w-4 h-4 text-green-600" />
                                    <span>{feature}</span>
                                  </li>
                                ))}
                              </ul>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="text-center py-12">
                  <X className="w-12 h-12 text-red-400 mx-auto mb-4" />
                  <p className="text-stone-600">Unable to load demo details. Please try again later.</p>
                </div>
              )}

              <div className="flex justify-end space-x-4 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setIsModalOpen(false)}
                >
                  Close
                </Button>
                <Button
                  className="bg-gradient-to-r from-green-800 to-green-900 hover:from-green-900 hover:to-stone-800 text-white"
                  onClick={() => {
                    setIsModalOpen(false);
                    handleGetStarted(selectedProduct);
                  }}
                >
                  <ShoppingCart className="w-4 h-4 mr-2" />
                  Get Started
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

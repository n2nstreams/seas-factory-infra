import { useState, useEffect } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../../components/ui/accordion';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '../../components/ui/tabs';

interface FAQItem {
  question: string;
  answer: string;
  category: string;
  source: string;
}

interface FAQStats {
  total_items: number;
  categories: Record<string, number>;
  sources: Record<string, number>;
  last_generation: string;
}

// Default FAQs about Forge95
const defaultFAQs: FAQItem[] = [
  {
    question: "What is Forge95?",
    answer: "Forge95 is an automated platform that transforms your ideas into production-ready SaaS applications. Our AI agents handle design, development, testing, and deployment, turning concepts into customer-ready products in record time.",
    category: "Getting Started",
    source: "fallback"
  },
  {
    question: "How does the AI development process work?",
    answer: "Our process involves multiple specialized AI agents: the Idea Validation Agent analyzes your concept, the Design Agent creates beautiful UIs, the Development Agent writes scalable code, the QA Agent ensures quality, and the Operations Agent handles deployment. Each agent is an expert in their domain, working together seamlessly.",
    category: "Features",
    source: "fallback"
  },
  {
    question: "How long does it take to build a SaaS application?",
    answer: "Most applications are completed within 24-48 hours, depending on complexity. Simple applications like landing pages or basic CRMs can be ready in under 24 hours, while more complex applications with custom integrations may take up to 48 hours.",
    category: "Features",
    source: "fallback"
  },
  {
    question: "What types of SaaS applications can you build?",
    answer: "We can build a wide variety of SaaS applications including CRM systems, task management tools, subscription billing dashboards, blog/CMS platforms, survey builders, e-commerce platforms, and much more. If you can describe it, our AI agents can likely build it.",
    category: "Features",
    source: "fallback"
  },
  {
    question: "Do I need technical knowledge to use the platform?",
    answer: "Not at all! Our platform is designed for entrepreneurs and business owners without technical backgrounds. Simply describe your idea in plain language, and our AI agents handle all the technical implementation, deployment, and infrastructure setup.",
    category: "Getting Started",
    source: "fallback"
  },
  {
    question: "How secure are the applications built by AI agents?",
    answer: "Security is a top priority. Our AI agents follow security best practices, implement proper authentication, use encrypted connections, and include automated security scanning. All applications are deployed with industry-standard security measures.",
    category: "Technical",
    source: "fallback"
  },
  {
    question: "Can I customize the generated application?",
    answer: "Yes! While our AI agents create production-ready applications, you can request modifications or enhancements. Our agents can iterate on the design, add new features, or adjust functionality based on your feedback.",
    category: "Features",
    source: "fallback"
  },
  {
    question: "What happens after my SaaS application is deployed?",
    answer: "After deployment, you get a live URL to your application, admin access, and ongoing monitoring. Our Operations Agent continuously monitors performance and can handle scaling, updates, and maintenance as needed.",
    category: "Technical",
    source: "fallback"
  },
  {
    question: "How much does it cost to build a SaaS application?",
    answer: "We offer different pricing tiers starting with a Free plan, then $30/month for the Starter plan. The cost depends on complexity, features, and ongoing support requirements. Check our pricing page for detailed information on each tier.",
    category: "Getting Started",
    source: "fallback"
  },
  {
    question: "Can I integrate with external services like Stripe or SendGrid?",
    answer: "Absolutely! Our AI agents can integrate with popular services like Stripe for payments, SendGrid for emails, various APIs for data, and many other third-party services. Just specify your integration requirements when submitting your idea.",
    category: "Technical",
    source: "fallback"
  }
];

const categoryColors = {
  "Getting Started": "bg-emerald-100/80 text-emerald-800 border-emerald-200",
  "Features": "bg-olive-100/80 text-olive-800 border-olive-200",
  "Technical": "bg-sage-100/80 text-sage-800 border-sage-200",
  "Troubleshooting": "bg-amber-100/80 text-amber-800 border-amber-200",
  "Best Practices": "bg-stone-700/20 text-stone-700 border-stone-600/40",
  "Development Status": "bg-stone-600/20 text-stone-700 border-stone-500/40",
  "Known Issues": "bg-stone-500/20 text-stone-700 border-stone-400/40",
  "Planned Features": "bg-indigo-100/80 text-indigo-800 border-indigo-200",
  "General": "bg-gray-100/80 text-gray-800 border-gray-200"
};

const sourceIcons = {
  docs: "📚",
  code: "💻", 
  fallback: "🔧",
  consolidated: "🎯"
};

export default function FAQPage() {
  const [faq, setFaq] = useState<FAQItem[]>(defaultFAQs);
  const [isLoading, setIsLoading] = useState(true);
  const [, setError] = useState<string | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);
  const [stats, setStats] = useState<FAQStats | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  useEffect(() => {
    const fetchFaq = async () => {
      try {
        setIsLoading(true);
        
        // Fetch FAQ items
        const faqResponse = await fetch('http://localhost:8089/faq');
        if (!faqResponse.ok) {
          throw new Error('Failed to fetch FAQ from support agent');
        }
        const faqData = await faqResponse.json();
        
        // Fetch FAQ stats
        const statsResponse = await fetch('http://localhost:8089/faq/stats');
        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          setStats(statsData);
        }
        
        setFaq(faqData);
        setUsingFallback(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
        console.log('Using default FAQs as fallback:', errorMessage);
        setFaq(defaultFAQs);
        setUsingFallback(true);
        setError(null); // Don't show error since we have fallback
      } finally {
        setIsLoading(false);
      }
    };

    fetchFaq();
  }, []);

  const regenerateFaq = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8089/faq/regenerate', {
        method: 'POST'
      });
      if (response.ok) {
        // Wait a moment then refetch
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch (err) {
      console.error('Failed to regenerate FAQ:', err);
    }
  };

  const categories = Array.from(new Set(faq.map(item => item.category))).sort();
  const filteredFaq = selectedCategory === "all" ? faq : faq.filter(item => item.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-emerald-50/30 to-sage-50/20">
      {/* Header */}
      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 pt-20 pb-16">
        <div className="text-center space-y-6 max-w-4xl mx-auto">
          <h1 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-stone-900">
            Frequently Asked Questions
          </h1>
          <p className="text-xl lg:text-2xl text-stone-700 leading-relaxed">
            Everything you need to know about our AI-powered SaaS development platform
          </p>
          
          {/* FAQ Stats */}
          {stats && (
            <div className="glass-card p-6 max-w-2xl mx-auto">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-olive-700">{stats.total_items}</div>
                  <div className="text-sm text-stone-600">Total FAQs</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-olive-700">{Object.keys(stats.categories).length}</div>
                  <div className="text-sm text-stone-600">Categories</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-olive-700">{Object.keys(stats.sources).length}</div>
                  <div className="text-sm text-stone-600">Sources</div>
                </div>
                <div>
                  <button 
                    onClick={regenerateFaq}
                    className="btn-secondary text-sm px-3 py-1 hover:bg-olive-100"
                    disabled={isLoading}
                  >
                    🔄 Refresh
                  </button>
                </div>
              </div>
              {stats.last_generation && (
                <p className="text-xs text-stone-500 mt-3">
                  Last updated: {new Date(stats.last_generation).toLocaleString()}
                </p>
              )}
            </div>
          )}

          {usingFallback && (
            <div className="glass-card p-4 max-w-2xl mx-auto border-amber-200 bg-amber-50/50">
              <p className="text-amber-800">
                <span className="font-semibold">Note:</span> Using default FAQs. The enhanced FAQ service may be starting up.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* FAQ Content */}
      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12 2xl:px-16 pb-20">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="glass-card p-8 text-center max-w-md mx-auto">
              <div className="animate-spin h-8 w-8 border-4 border-olive-600 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-stone-600">Generating comprehensive FAQ from documentation and code insights...</p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            {/* Category Filter */}
            <div className="mb-8">
              <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="w-full">
                <TabsList className="glass-card p-2 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 h-auto">
                  <TabsTrigger value="all" className="data-[state=active]:bg-olive-600 data-[state=active]:text-white">
                    All ({faq.length})
                  </TabsTrigger>
                  {categories.map(category => (
                    <TabsTrigger 
                      key={category} 
                      value={category}
                      className="data-[state=active]:bg-olive-600 data-[state=active]:text-white text-center text-xs"
                    >
                      {category} ({faq.filter(item => item.category === category).length})
                    </TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </div>

            {/* FAQ Items */}
            <Accordion type="single" collapsible className="w-full space-y-4">
              {filteredFaq.map((item, index) => (
                <AccordionItem 
                  value={`item-${index}`} 
                  key={index}
                  className="glass-card border-none"
                >
                  <AccordionTrigger className="text-lg font-semibold text-heading px-6 py-4 hover:no-underline hover:bg-stone-100/20 transition-colors">
                    <div className="flex items-start gap-3 text-left w-full">
                      <span className="flex-1">{item.question}</span>
                      <div className="flex gap-2 ml-4 flex-shrink-0">
                        <Badge className={`text-xs ${categoryColors[item.category as keyof typeof categoryColors] || categoryColors.General}`}>
                          {item.category}
                        </Badge>
                        <span className="text-lg" title={`Source: ${item.source}`}>
                          {sourceIcons[item.source as keyof typeof sourceIcons] || "📄"}
                        </span>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="text-base text-body px-6 pb-6 leading-relaxed">
                    {item.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
            
            {filteredFaq.length === 0 && (
              <div className="text-center py-12 glass-card">
                <p className="text-stone-600">No FAQ items found for the selected category.</p>
              </div>
            )}
          </div>
        )}

        {/* Contact Section */}
        <div className="mt-16 text-center">
          <div className="glass-card p-8 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-heading mb-4">Still have questions?</h2>
            <p className="text-body mb-6">
              Can't find the answer you're looking for? Our support team is here to help you succeed.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="btn-primary px-6 py-3">
                Contact Support
              </button>
              <button className="btn-secondary px-6 py-3">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-stone-200/50 bg-stone-50/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-stone-600">
            <p>&copy; 2025 Forge95. Built with intelligent automation.</p>
            {stats && (
              <p className="text-xs mt-2">
                FAQ powered by {Object.keys(stats.sources).join(", ")} • 
                {stats.total_items} answers across {Object.keys(stats.categories).length} categories
              </p>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
} 
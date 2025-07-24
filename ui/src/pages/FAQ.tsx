import { useEffect, useState } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Loader2, AlertCircle, Sparkles, Code2 } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
}

// Default FAQs about the AI SaaS Factory
const defaultFAQs: FAQItem[] = [
  {
    question: "What is the AI SaaS Factory?",
    answer: "The AI SaaS Factory is an automated platform that transforms your ideas into production-ready SaaS applications. Our AI agents handle design, development, testing, and deployment, turning concepts into customer-ready products in record time."
  },
  {
    question: "How does the AI development process work?",
    answer: "Our process involves multiple specialized AI agents: the Idea Validation Agent analyzes your concept, the Design Agent creates beautiful UIs, the Development Agent writes scalable code, the QA Agent ensures quality, and the Operations Agent handles deployment. Each agent is an expert in their domain, working together seamlessly."
  },
  {
    question: "How long does it take to build a SaaS application?",
    answer: "Most applications are completed within 24-48 hours, depending on complexity. Simple applications like landing pages or basic CRMs can be ready in under 24 hours, while more complex applications with custom integrations may take up to 48 hours."
  },
  {
    question: "What types of SaaS applications can you build?",
    answer: "We can build a wide variety of SaaS applications including CRM systems, task management tools, subscription billing dashboards, blog/CMS platforms, survey builders, e-commerce platforms, and much more. If you can describe it, our AI agents can likely build it."
  },
  {
    question: "Do I need technical knowledge to use the platform?",
    answer: "Not at all! Our platform is designed for entrepreneurs and business owners without technical backgrounds. Simply describe your idea in plain language, and our AI agents handle all the technical implementation, deployment, and infrastructure setup."
  },
  {
    question: "What's included in each pricing plan?",
    answer: "Starter ($29/mo): 1 project, 15 build hours, shared infrastructure. Pro ($99/mo): 3 projects, 60 build hours, priority support. Growth ($299/mo): 5 projects, unlimited build hours, dedicated infrastructure option, and premium support with 24h SLA."
  },
  {
    question: "What are 'build hours' and how are they calculated?",
    answer: "Build hours represent the cumulative time our AI agents spend actively working on your project (analyzing, designing, coding, testing). Most simple applications use 8-15 build hours, while complex applications may use 20-40 hours. Time spent on deployment and infrastructure setup doesn't count toward your quota."
  },
  {
    question: "Can I customize my application after it's built?",
    answer: "Yes! You can request modifications and new features through our platform. Additional changes will consume build hours from your plan. For major customizations, we recommend upgrading to a higher tier or considering our dedicated infrastructure option."
  },
  {
    question: "What technology stack do you use?",
    answer: "We use modern, scalable technologies including React/TypeScript for frontends, Python/FastAPI for backends, PostgreSQL for databases, and deploy everything on Google Cloud Platform. All applications follow industry best practices for security, performance, and maintainability."
  },
  {
    question: "Do I own the code and can I export it?",
    answer: "Yes, you retain full ownership of your application and its source code. Pro and Growth plan customers can request code exports and have the option to migrate to their own infrastructure if needed."
  },
  {
    question: "How secure are the applications you build?",
    answer: "Security is our top priority. All applications include authentication, data encryption, secure API endpoints, and follow OWASP security guidelines. We also run automated security scans and penetration tests on all deployed applications."
  },
  {
    question: "What kind of support do you provide?",
    answer: "Starter plan includes community forum support. Pro plan includes email support with 48h SLA. Growth plan includes priority Slack support with 24h SLA, dedicated success manager, and optional video consultations."
  },
  {
    question: "Can I integrate my application with other services?",
    answer: "Absolutely! Our AI agents can integrate with popular services like Stripe for payments, SendGrid for emails, various APIs, webhooks, and third-party platforms. Just mention your integration needs when submitting your idea."
  },
  {
    question: "What happens if I'm not satisfied with the result?",
    answer: "We offer a satisfaction guarantee. If you're not happy with the initial build, we'll work with you to make revisions within your build hour allocation. For major issues, we provide refunds on a case-by-case basis."
  },
  {
    question: "How do you handle scaling and performance?",
    answer: "All applications are built with scalability in mind, using cloud-native architectures, auto-scaling infrastructure, CDNs, and optimized databases. Growth plan customers get access to dedicated infrastructure and performance monitoring."
  }
];

export default function FAQPage() {
  const [faq, setFaq] = useState<FAQItem[]>(defaultFAQs);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);

  useEffect(() => {
    const fetchFaq = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('http://localhost:8089/faq'); // Assuming support agent runs on 8089
        if (!response.ok) {
          throw new Error('Failed to fetch FAQ from support agent');
        }
        const data = await response.json();
        setFaq(data);
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

  return (
    <div className="min-h-screen bg-homepage relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-green-800/20 to-green-900/25 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-80 h-80 bg-gradient-to-bl from-slate-700/20 to-green-800/25 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-gradient-to-tr from-stone-600/20 to-green-700/25 rounded-full blur-3xl animate-pulse delay-2000"></div>
      </div>

      <div className="container mx-auto py-12 px-4 relative z-10">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-accent-icon mr-3" />
            <h1 className="text-4xl font-bold text-heading">Frequently Asked Questions</h1>
          </div>
          <p className="text-lg text-body max-w-2xl mx-auto">
            Everything you need to know about the AI SaaS Factory and how we transform your ideas into production-ready applications.
          </p>
          {usingFallback && (
            <p className="text-sm text-body/70 mt-2 italic">
              (Showing default FAQs - Support agent not connected)
            </p>
          )}
        </div>
        
        {isLoading && (
          <div className="flex justify-center items-center h-64">
            <Loader2 className="h-12 w-12 animate-spin text-accent-icon" />
          </div>
        )}

        {error && !usingFallback && (
          <div className="flex flex-col items-center text-red-500">
            <AlertCircle className="h-12 w-12 mb-4" />
            <p className="text-xl">Could not load FAQ</p>
            <p>{error}</p>
          </div>
        )}

        {!isLoading && (
          <div className="max-w-4xl mx-auto">
            <Accordion type="single" collapsible className="w-full space-y-4">
              {faq.map((item, index) => (
                <AccordionItem 
                  value={`item-${index}`} 
                  key={index}
                  className="glass-card border-none"
                >
                  <AccordionTrigger className="text-lg font-semibold text-heading px-6 py-4 hover:no-underline hover:bg-stone-100/20 transition-colors">
                    {item.question}
                  </AccordionTrigger>
                  <AccordionContent className="text-base text-body px-6 pb-6 leading-relaxed">
                    {item.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
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
      <footer className="bg-stone-900/95 backdrop-blur-lg text-white py-12 border-t border-stone-400/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-green-800 to-green-900 rounded-xl flex items-center justify-center shadow-lg">
                  <Code2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold">AI SaaS Factory</span>
              </div>
              <p className="text-stone-300">
                Turn any idea into a live SaaS business - no code required.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Product</h4>
              <div className="space-y-2 text-stone-400">
                <a href="/" className="block hover:text-white transition-colors">Features</a>
                <a href="/pricing" className="block hover:text-white transition-colors">Pricing</a>
                <a href="/dashboard" className="block hover:text-white transition-colors">Dashboard</a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Company</h4>
              <div className="space-y-2 text-stone-400">
                <a href="#" className="block hover:text-white transition-colors">About</a>
                <a href="#" className="block hover:text-white transition-colors">Blog</a>
                <a href="#" className="block hover:text-white transition-colors">Contact</a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-stone-200">Support</h4>
              <div className="space-y-2 text-stone-400">
                <a href="#" className="block hover:text-white transition-colors">Documentation</a>
                <a href="#" className="block hover:text-white transition-colors">Community</a>
                <a href="#" className="block hover:text-white transition-colors">Help Center</a>
              </div>
            </div>
          </div>
          <div className="border-t border-stone-700/50 mt-8 pt-8 text-center text-stone-300">
            <p>&copy; 2024 AI SaaS Factory. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 
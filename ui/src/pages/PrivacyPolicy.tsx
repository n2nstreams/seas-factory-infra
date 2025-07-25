import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Shield, FileText, Calendar, Mail, Eye, Lock, Database, Globe } from "lucide-react";

export default function PrivacyPolicy() {
  const lastUpdated = "January 15, 2025";
  const effectiveDate = "January 15, 2025";

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-green-50/30">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Eye className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-heading mb-4">
            Privacy Policy
          </h1>
          <p className="text-lg text-body max-w-2xl mx-auto">
            How we collect, use, and protect your personal information
          </p>
          <div className="flex items-center justify-center gap-6 mt-6 text-sm text-body">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>Effective: {effectiveDate}</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              <span>Last Updated: {lastUpdated}</span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <Card className="card-glass">
          <CardHeader className="space-y-6">
            <CardTitle className="text-2xl text-heading flex items-center gap-3">
              <Shield className="w-6 h-6 text-accent" />
              Privacy Policy
            </CardTitle>
            <p className="text-body leading-relaxed">
              At AI SaaS Factory, we are committed to protecting your privacy and ensuring transparency 
              about how we handle your personal information. This Privacy Policy explains our practices 
              regarding the collection, use, and disclosure of information when you use our Services.
            </p>
          </CardHeader>

          <CardContent className="space-y-8">
            {/* Section 1: Information We Collect */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4 flex items-center gap-2">
                <Database className="w-5 h-5 text-accent" />
                1. Information We Collect
              </h2>
              <div className="space-y-4 text-body">
                <div>
                  <h3 className="font-semibold text-heading mb-2">1.1 Information You Provide</h3>
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    <li>Account information (name, email address, password)</li>
                    <li>Business information (company name, project details)</li>
                    <li>Payment information (processed by Stripe, not stored by us)</li>
                    <li>Content you create through our Services (project data, code, designs)</li>
                    <li>Communications with our support team</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-heading mb-2">1.2 Information We Collect Automatically</h3>
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    <li>Usage data (how you interact with our Services)</li>
                    <li>Device information (browser type, operating system)</li>
                    <li>IP address and location data (approximate geographic location)</li>
                    <li>Cookies and similar tracking technologies</li>
                    <li>Log files and analytics data</li>
                  </ul>
                </div>
              </div>
            </section>

            <Separator />

            {/* Section 2: How We Use Information */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">2. How We Use Your Information</h2>
              <div className="space-y-4 text-body">
                <p>We use the information we collect for the following purposes:</p>
                <ul className="list-disc list-inside ml-4 space-y-2">
                  <li><strong>Service Provision:</strong> To provide, maintain, and improve our AI SaaS development platform</li>
                  <li><strong>Account Management:</strong> To create and manage your account, authenticate users</li>
                  <li><strong>Communication:</strong> To send service updates, security alerts, and support messages</li>
                  <li><strong>Personalization:</strong> To customize your experience and provide relevant recommendations</li>
                  <li><strong>Analytics:</strong> To understand usage patterns and improve our Services</li>
                  <li><strong>Security:</strong> To detect, prevent, and address fraud, security issues, and technical problems</li>
                  <li><strong>Legal Compliance:</strong> To comply with applicable laws and regulations</li>
                </ul>
              </div>
            </section>

            <Separator />

            {/* Section 3: Legal Basis for Processing */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">3. Legal Basis for Processing (GDPR)</h2>
              <div className="space-y-4 text-body">
                <p>For users in the European Union, we process your personal data based on:</p>
                <ul className="list-disc list-inside ml-4 space-y-2">
                  <li><strong>Contract:</strong> To perform our contract with you (providing the Services)</li>
                  <li><strong>Consent:</strong> Where you have given specific consent (e.g., marketing communications)</li>
                  <li><strong>Legitimate Interest:</strong> For improving our Services, security, and analytics</li>
                  <li><strong>Legal Obligation:</strong> To comply with applicable laws and regulations</li>
                </ul>
              </div>
            </section>

            <Separator />

            {/* Section 4: Information Sharing */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">4. How We Share Your Information</h2>
              <div className="space-y-4 text-body">
                <p>We do not sell your personal information. We may share your information in these situations:</p>
                <div className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-heading mb-2">4.1 Service Providers</h3>
                    <p>We share data with trusted third-party service providers:</p>
                    <ul className="list-disc list-inside ml-4 space-y-1">
                      <li>Google Cloud Platform (hosting and infrastructure)</li>
                      <li>OpenAI (AI model processing)</li>
                      <li>Stripe (payment processing)</li>
                      <li>SendGrid (email delivery)</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-heading mb-2">4.2 Legal Requirements</h3>
                    <p>We may disclose information if required by law or to protect our rights and safety.</p>
                  </div>
                  <div>
                    <h3 className="font-semibold text-heading mb-2">4.3 Business Transfers</h3>
                    <p>In case of merger, acquisition, or sale of assets, your information may be transferred.</p>
                  </div>
                </div>
              </div>
            </section>

            <Separator />

            {/* Section 5: Your Rights */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4 flex items-center gap-2">
                <Lock className="w-5 h-5 text-accent" />
                5. Your Privacy Rights
              </h2>
              <div className="space-y-4 text-body">
                <p>You have the following rights regarding your personal data:</p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-semibold text-heading">Access</h4>
                      <p className="text-sm">Request a copy of your personal data</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-heading">Rectification</h4>
                      <p className="text-sm">Correct inaccurate or incomplete data</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-heading">Erasure</h4>
                      <p className="text-sm">Request deletion of your personal data</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-semibold text-heading">Portability</h4>
                      <p className="text-sm">Receive your data in a structured format</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-heading">Restriction</h4>
                      <p className="text-sm">Limit how we process your data</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-heading">Objection</h4>
                      <p className="text-sm">Object to certain processing activities</p>
                    </div>
                  </div>
                </div>
                <p className="mt-4 p-4 bg-green-50 rounded-lg">
                  <strong>How to Exercise Your Rights:</strong> Contact us at privacy@saas-factory.com 
                  or use the privacy controls in your account dashboard.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 6: Data Security */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">6. Data Security</h2>
              <div className="space-y-4 text-body">
                <p>We implement industry-standard security measures to protect your data:</p>
                <ul className="list-disc list-inside ml-4 space-y-2">
                  <li>End-to-end encryption for data in transit and at rest</li>
                  <li>Regular security audits and vulnerability assessments</li>
                  <li>Access controls and multi-factor authentication</li>
                  <li>Employee training on data protection and security</li>
                  <li>Incident response procedures for data breaches</li>
                </ul>
              </div>
            </section>

            <Separator />

            {/* Section 7: International Transfers */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-accent" />
                7. International Data Transfers
              </h2>
              <div className="space-y-4 text-body">
                <p>
                  Your information may be transferred to and processed in countries outside your region. 
                  We ensure adequate protection through:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li>Standard Contractual Clauses approved by the European Commission</li>
                  <li>Adequacy decisions for certain countries</li>
                  <li>Other appropriate safeguards as required by law</li>
                </ul>
              </div>
            </section>

            <Separator />

            {/* Section 8: Cookies */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">8. Cookies and Tracking</h2>
              <div className="space-y-4 text-body">
                <p>We use cookies and similar technologies to:</p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li>Remember your preferences and login status</li>
                  <li>Analyze usage patterns and improve our Services</li>
                  <li>Provide personalized content and features</li>
                </ul>
                <p className="mt-3">
                  You can control cookies through your browser settings. Some features may not work 
                  properly if you disable cookies.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 9: Data Retention */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">9. Data Retention</h2>
              <div className="space-y-4 text-body">
                <p>We retain your personal data for as long as necessary to:</p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li>Provide our Services to you</li>
                  <li>Comply with legal obligations</li>
                  <li>Resolve disputes and enforce agreements</li>
                </ul>
                <p className="mt-3">
                  When you delete your account, we will delete your personal data within 30 days, 
                  except where retention is required by law.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 10: Children's Privacy */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">10. Children's Privacy</h2>
              <div className="space-y-4 text-body">
                <p>
                  Our Services are not intended for children under 16 years of age. We do not 
                  knowingly collect personal information from children under 16.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 11: Changes to Policy */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">11. Changes to This Policy</h2>
              <div className="space-y-4 text-body">
                <p>
                  We may update this Privacy Policy from time to time. We will notify you of 
                  significant changes by email or through our Services.
                </p>
              </div>
            </section>

            <Separator />

            {/* Contact Information */}
            <section className="bg-stone-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-heading mb-4 flex items-center gap-3">
                <Mail className="w-5 h-5 text-accent" />
                Contact Us
              </h2>
              <div className="space-y-3 text-body">
                <p>
                  If you have any questions about this Privacy Policy or our privacy practices:
                </p>
                <div className="space-y-2">
                  <p><strong>Email:</strong> privacy@saas-factory.com</p>
                  <p><strong>Data Protection Officer:</strong> dpo@saas-factory.com</p>
                  <p><strong>Address:</strong> [Company Address]</p>
                </div>
                <p className="mt-4 text-sm">
                  For EU residents: You also have the right to lodge a complaint with your 
                  local supervisory authority.
                </p>
              </div>
            </section>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-12 text-sm text-body">
          <p>
            This Privacy Policy is effective as of {effectiveDate} and was last updated on {lastUpdated}.
          </p>
          <p className="mt-2">
            You can always find the most current version at:{" "}
            <span className="font-mono text-accent">saas-factory.com/privacy</span>
          </p>
        </div>
      </div>
    </div>
  );
} 
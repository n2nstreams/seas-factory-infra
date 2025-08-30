import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";

export default function TermsOfService() {
  const effectiveDate = "January 1, 2025";
  const lastUpdated = "January 1, 2025";

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => window.history.back()}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-center mb-4">
              Terms of Service
            </CardTitle>
            <p className="text-body leading-relaxed">
              These Terms of Service ("Terms") govern your use of Forge95's 
              AI-powered SaaS development platform services ("Services") operated by 
              Forge95 ("Company", "we", "us"). By accessing or using our Services, 
              you agree to be bound by these Terms.
            </p>
          </CardHeader>
          
          <CardContent className="space-y-8">
            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">1. Acceptance of Terms</h2>
              <p className="text-body leading-relaxed">
                By accessing and using our Services, you accept and agree to be bound by the terms 
                and provision of this agreement. If you do not agree to abide by the above, please 
                do not use this service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">2. Description of Service</h2>
              <p className="text-body leading-relaxed">
                Forge95 provides an AI-powered platform that automates the development of SaaS 
                applications. Our AI agents handle design, development, testing, and deployment 
                processes to transform your ideas into production-ready applications.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">3. User Accounts</h2>
              <div className="space-y-4">
                <p className="text-body leading-relaxed">
                  To access certain features of our Services, you may be required to create an account. 
                  You are responsible for:
                </p>
                <ul className="list-disc list-inside space-y-2 text-body ml-4">
                  <li>Maintaining the confidentiality of your account credentials</li>
                  <li>All activities that occur under your account</li>
                  <li>Notifying us immediately of any unauthorized use</li>
                  <li>Providing accurate and complete registration information</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">4. Acceptable Use</h2>
              <div className="space-y-4">
                <p className="text-body leading-relaxed">
                  You agree not to use our Services to:
                </p>
                <ul className="list-disc list-inside space-y-2 text-body ml-4">
                  <li>Develop applications that violate laws or regulations</li>
                  <li>Create harmful, abusive, or malicious software</li>
                  <li>Infringe on intellectual property rights</li>
                  <li>Attempt to gain unauthorized access to our systems</li>
                  <li>Distribute spam, malware, or other harmful content</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">5. Intellectual Property</h2>
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-heading">Your Content</h3>
                <p className="text-body leading-relaxed">
                  You retain all rights to the applications and content created using our Services. 
                  We claim no ownership over your generated code, designs, or applications.
                </p>
                
                <h3 className="text-lg font-medium text-heading">Our Platform</h3>
                <p className="text-body leading-relaxed">
                  The Forge95 platform, including our AI models, algorithms, and underlying 
                  technology, remains our exclusive property and is protected by intellectual 
                  property laws.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">6. Payment Terms</h2>
              <div className="space-y-4">
                <p className="text-body leading-relaxed">
                  Subscription fees are billed in advance on a monthly or annual basis. You agree to:
                </p>
                <ul className="list-disc list-inside space-y-2 text-body ml-4">
                  <li>Pay all fees when due</li>
                  <li>Provide accurate billing information</li>
                  <li>Notify us of any billing disputes within 30 days</li>
                  <li>Accept that fees are non-refundable except as required by law</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">7. Service Availability</h2>
              <p className="text-body leading-relaxed">
                While we strive for 99.9% uptime, we do not guarantee uninterrupted access to our 
                Services. We may perform maintenance, updates, or experience technical difficulties 
                that temporarily affect service availability.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">8. Limitation of Liability</h2>
              <p className="text-body leading-relaxed">
                To the maximum extent permitted by law, Forge95 shall not be liable for any 
                indirect, incidental, special, consequential, or punitive damages, including but 
                not limited to loss of profits, data, or business opportunities.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">9. Termination</h2>
              <div className="space-y-4">
                <p className="text-body leading-relaxed">
                  Either party may terminate this agreement at any time. Upon termination:
                </p>
                <ul className="list-disc list-inside space-y-2 text-body ml-4">
                  <li>Your access to the Services will cease</li>
                  <li>You retain rights to applications already created</li>
                  <li>We may delete your account data after 30 days</li>
                  <li>Outstanding fees remain due and payable</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">10. Changes to Terms</h2>
              <p className="text-body leading-relaxed">
                We may update these Terms from time to time. We will notify you of significant 
                changes by email or through our platform. Continued use of our Services after 
                changes constitutes acceptance of the new Terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">11. Governing Law</h2>
              <p className="text-body leading-relaxed">
                These Terms shall be governed by and construed in accordance with the laws of 
                the jurisdiction where Forge95 is incorporated, without regard to its conflict 
                of law provisions.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4 text-heading">12. Contact Information</h2>
              <p className="text-body leading-relaxed">
                If you have any questions about these Terms of Service:
              </p>
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-body">
                  <strong>Email:</strong> legal@forge95.com<br />
                  <strong>Address:</strong> [Company Address]<br />
                  <strong>Phone:</strong> [Company Phone]
                </p>
              </div>
            </section>

            <div className="border-t border-gray-200 pt-8 mt-8">
              <p className="text-sm text-muted-foreground text-center">
                These Terms of Service are effective as of {effectiveDate} and were last updated on {lastUpdated}.
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-12 text-center">
          <Button onClick={() => window.history.back()}>
            Return to Previous Page
          </Button>
        </div>
      </div>
    </div>
  );
} 
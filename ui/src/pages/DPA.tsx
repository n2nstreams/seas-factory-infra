import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Shield, FileText, Calendar, Mail, Building } from "lucide-react";

export default function DPA() {
  const lastUpdated = "January 15, 2025";
  const effectiveDate = "January 15, 2025";

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-green-50/30">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-accent-icon rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-heading mb-4">
            Data Processing Agreement (DPA)
          </h1>
          <p className="text-lg text-body max-w-2xl mx-auto">
            Our commitment to protecting your data and ensuring GDPR compliance
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
              <Building className="w-6 h-6 text-accent" />
              Data Processing Agreement
            </CardTitle>
            <p className="text-body leading-relaxed">
              This Data Processing Agreement ("DPA") forms part of the Service Agreement between 
              AI SaaS Factory ("Company", "we", "us") and you ("Customer", "you") for the use 
              of our AI-powered SaaS development platform services ("Services").
            </p>
          </CardHeader>

          <CardContent className="space-y-8">
            {/* Section 1: Definitions */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">1. Definitions</h2>
              <div className="space-y-3 text-body">
                <p><strong>"Personal Data"</strong> means any information relating to an identified or identifiable natural person.</p>
                <p><strong>"Processing"</strong> means any operation performed on Personal Data, including collection, use, storage, and deletion.</p>
                <p><strong>"Data Subject"</strong> means the identified or identifiable natural person to whom Personal Data relates.</p>
                <p><strong>"GDPR"</strong> means the General Data Protection Regulation (EU) 2016/679.</p>
              </div>
            </section>

            <Separator />

            {/* Section 2: Scope and Roles */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">2. Scope and Data Protection Roles</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>2.1 Data Controller:</strong> Customer acts as the Data Controller for Personal Data 
                  processed through the Services.
                </p>
                <p>
                  <strong>2.2 Data Processor:</strong> Company acts as a Data Processor, processing Personal Data 
                  on behalf of and in accordance with Customer's documented instructions.
                </p>
                <p>
                  <strong>2.3 Scope:</strong> This DPA applies to the processing of Personal Data by Company 
                  in the course of providing the Services.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 3: Processing Instructions */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">3. Processing Instructions</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>3.1</strong> Company will process Personal Data only on documented instructions from Customer, 
                  including those set forth in this DPA and the Service Agreement.
                </p>
                <p>
                  <strong>3.2</strong> Additional instructions may be given by Customer through the Services interface 
                  or by contacting our support team.
                </p>
                <p>
                  <strong>3.3</strong> Company will immediately inform Customer if instructions appear to violate 
                  applicable data protection laws.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 4: Security Measures */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">4. Technical and Organizational Measures</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>4.1</strong> Company implements appropriate technical and organizational measures to ensure 
                  a level of security appropriate to the risk, including:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-2">
                  <li>Encryption of Personal Data in transit and at rest</li>
                  <li>Regular security assessments and vulnerability testing</li>
                  <li>Access controls and authentication mechanisms</li>
                  <li>Regular backup and disaster recovery procedures</li>
                  <li>Employee training on data protection requirements</li>
                </ul>
                <p>
                  <strong>4.2</strong> Company will review and update these measures regularly to maintain 
                  their effectiveness.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 5: Sub-processors */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">5. Sub-processors</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>5.1</strong> Customer authorizes Company to engage sub-processors to process Personal Data, 
                  subject to the conditions in this section.
                </p>
                <p>
                  <strong>5.2</strong> Current sub-processors include:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li>Google Cloud Platform (infrastructure hosting)</li>
                  <li>OpenAI (AI model processing)</li>
                  <li>Stripe (payment processing)</li>
                </ul>
                <p>
                  <strong>5.3</strong> Company will notify Customer of any intended changes to sub-processors 
                  and provide opportunity to object.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 6: Data Subject Rights */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">6. Data Subject Rights</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>6.1</strong> Company will assist Customer in responding to requests from Data Subjects 
                  to exercise their rights under GDPR.
                </p>
                <p>
                  <strong>6.2</strong> Company will implement appropriate technical measures to enable Customer 
                  to comply with requests for:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li>Access to Personal Data</li>
                  <li>Rectification or erasure of Personal Data</li>
                  <li>Restriction of processing</li>
                  <li>Data portability</li>
                </ul>
              </div>
            </section>

            <Separator />

            {/* Section 7: Data Transfers */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">7. International Data Transfers</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>7.1</strong> Personal Data may be transferred to and processed in countries outside 
                  the European Economic Area.
                </p>
                <p>
                  <strong>7.2</strong> Company ensures adequate protection through appropriate safeguards, 
                  including Standard Contractual Clauses approved by the European Commission.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 8: Data Breach Notification */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">8. Personal Data Breach</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>8.1</strong> Company will notify Customer without undue delay upon becoming aware 
                  of a Personal Data breach affecting Customer's data.
                </p>
                <p>
                  <strong>8.2</strong> Company will provide reasonable assistance to Customer in meeting 
                  its obligations to notify supervisory authorities and Data Subjects.
                </p>
              </div>
            </section>

            <Separator />

            {/* Section 9: Data Retention and Deletion */}
            <section>
              <h2 className="text-xl font-semibold text-heading mb-4">9. Data Retention and Deletion</h2>
              <div className="space-y-4 text-body">
                <p>
                  <strong>9.1</strong> Company will delete or return Personal Data to Customer upon termination 
                  of the Service Agreement, unless legally required to retain it.
                </p>
                <p>
                  <strong>9.2</strong> Customer may request deletion of specific Personal Data at any time 
                  through the Services interface.
                </p>
              </div>
            </section>

            <Separator />

            {/* Contact Information */}
            <section className="bg-stone-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-heading mb-4 flex items-center gap-3">
                <Mail className="w-5 h-5 text-accent" />
                Contact Information
              </h2>
              <div className="space-y-3 text-body">
                <p>
                  <strong>Data Protection Officer:</strong><br />
                  Email: dpo@saas-factory.com<br />
                  Address: [Company Address]
                </p>
                <p>
                  <strong>For questions about this DPA:</strong><br />
                  Email: privacy@saas-factory.com<br />
                  Support Portal: Available in your dashboard
                </p>
              </div>
            </section>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-12 text-sm text-body">
          <p>
            This DPA is effective as of {effectiveDate} and was last updated on {lastUpdated}.
          </p>
          <p className="mt-2">
            You can always find the most current version at:{" "}
            <span className="font-mono text-accent">saas-factory.com/dpa</span>
          </p>
        </div>
      </div>
    </div>
  );
} 
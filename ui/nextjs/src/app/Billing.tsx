import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  CreditCard, 
  Receipt, 
  Download, 
  Plus,
  Calendar,
  DollarSign,
  AlertCircle
} from 'lucide-react';

interface BillingHistory {
  id: string;
  date: string;
  amount: number;
  description: string;
  status: 'paid' | 'pending' | 'failed';
  invoiceUrl?: string;
}

const mockBillingHistory: BillingHistory[] = [
  {
    id: '1',
    date: '2024-01-15',
    amount: 99.00,
    description: 'Pro Plan - Monthly',
    status: 'paid',
    invoiceUrl: '#'
  },
  {
    id: '2',
    date: '2024-01-01',
    amount: 99.00,
    description: 'Pro Plan - Monthly',
    status: 'paid',
    invoiceUrl: '#'
  },
  {
    id: '3',
    date: '2023-12-15',
    amount: 99.00,
    description: 'Pro Plan - Monthly',
    status: 'paid',
    invoiceUrl: '#'
  }
];

export default function Billing() {
  const [currentPlan] = useState({
    name: 'Pro Plan',
    price: '$99/month',
    nextBilling: '2024-02-15',
    buildHours: {
      used: 15,
      total: 50
    }
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-800/20 text-green-800';
      case 'pending':
        return 'bg-stone-600/20 text-stone-700';
      case 'failed':
        return 'bg-red-700/20 text-red-800';
      default:
        return 'bg-stone-100 text-stone-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 to-green-50 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-stone-900">Billing & Subscription</h1>
            <p className="text-stone-600 mt-2">Manage your subscription and view billing history</p>
          </div>
          <Button className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Payment Method
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Plan */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CreditCard className="w-5 h-5 mr-2" />
                  Current Plan
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-stone-50 rounded-lg">
                  <div>
                    <h3 className="font-semibold text-stone-900">{currentPlan.name}</h3>
                    <p className="text-stone-600">{currentPlan.price}</p>
                  </div>
                  <Badge variant="outline">Active</Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-stone-50 rounded-lg">
                    <div className="flex items-center mb-2">
                      <Calendar className="w-4 h-4 text-stone-500 mr-2" />
                      <span className="text-sm font-medium text-stone-700">Next Billing</span>
                    </div>
                    <p className="text-lg font-semibold text-stone-900">{currentPlan.nextBilling}</p>
                  </div>

                  <div className="p-4 bg-stone-50 rounded-lg">
                    <div className="flex items-center mb-2">
                      <DollarSign className="w-4 h-4 text-stone-500 mr-2" />
                      <span className="text-sm font-medium text-stone-700">Build Hours</span>
                    </div>
                    <p className="text-lg font-semibold text-stone-900">
                      {currentPlan.buildHours.used} / {currentPlan.buildHours.total}
                    </p>
                    <div className="w-full bg-stone-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-green-800 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(currentPlan.buildHours.used / currentPlan.buildHours.total) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <Button variant="outline" className="flex-1">
                    Change Plan
                  </Button>
                  <Button variant="outline" className="flex-1">
                    Cancel Subscription
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Payment Methods */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Payment Methods</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 border border-stone-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <CreditCard className="w-5 h-5 text-stone-500 mr-3" />
                      <div>
                        <p className="font-medium text-stone-900">•••• •••• •••• 4242</p>
                        <p className="text-sm text-stone-600">Expires 12/25</p>
                      </div>
                    </div>
                    <Badge variant="outline">Default</Badge>
                  </div>
                </div>

                <Button variant="outline" className="w-full">
                  <Plus className="w-4 h-4 mr-2" />
                  Add New Card
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Billing History */}
        <Card>
          <CardHeader>
            <CardTitle>Billing History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockBillingHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 border border-stone-200 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <Receipt className="w-5 h-5 text-stone-500" />
                    <div>
                      <p className="font-medium text-stone-900">{item.description}</p>
                      <p className="text-sm text-stone-600">{item.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="font-semibold text-stone-900">${item.amount.toFixed(2)}</span>
                    <Badge className={getStatusColor(item.status)}>
                      {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </Badge>
                    {item.invoiceUrl && (
                      <Button variant="ghost" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Invoice
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Usage Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-yellow-500" />
              Usage Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="font-medium text-yellow-800">Build Hours Warning</h4>
                  <p className="text-yellow-700 mt-1">
                    You've used {currentPlan.buildHours.used} out of {currentPlan.buildHours.total} build hours this month. 
                    Consider upgrading your plan to avoid interruptions.
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    Upgrade Plan
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, AlertCircle } from 'lucide-react';

interface AnalyticsData {
  variation_id: string;
  users: number;
  conversions: number;
}

export default function AnalyticsPanel({ experimentKey }: { experimentKey: string }) {
  const [data, setData] = useState<AnalyticsData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`/api/admin/analytics/experiment/${experimentKey}`);
        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    if (experimentKey) {
      fetchAnalytics();
    }
  }, [experimentKey]);

  const chartData = data.map(item => ({
    name: item.variation_id,
    conversionRate: item.users > 0 ? (item.conversions / item.users) * 100 : 0,
    users: item.users
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Experiment: {experimentKey}</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="flex justify-center items-center h-64">
            <Loader2 className="h-12 w-12 animate-spin" />
          </div>
        )}
        {error && (
          <div className="flex flex-col items-center text-red-500">
            <AlertCircle className="h-12 w-12 mb-4" />
            <p className="text-xl">Could not load analytics</p>
            <p>{error}</p>
          </div>
        )}
        {!isLoading && !error && (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis yAxisId="left" orientation="left" stroke="#8884d8" label={{ value: 'Conversion Rate (%)', angle: -90, position: 'insideLeft' }} />
              <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" label={{ value: 'Users', angle: -90, position: 'insideRight' }} />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="conversionRate" fill="#8884d8" name="Conversion Rate (%)" />
              <Bar yAxisId="right" dataKey="users" fill="#82ca9d" name="Users" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
} 
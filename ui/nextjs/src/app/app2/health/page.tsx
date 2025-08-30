import HealthDashboard from '@/components/health-monitoring/HealthDashboard'

export default function HealthPage() {
  return (
    <div className="container mx-auto py-6 px-4">
      <HealthDashboard />
    </div>
  )
}

export const metadata = {
  title: 'Health Monitoring - AI SaaS Factory',
  description: 'Real-time system health and performance monitoring dashboard',
}

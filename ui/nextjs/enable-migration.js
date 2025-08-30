// Enable Migration Feature Flags
// Run this in your browser console to enable the new UI shell

console.log('🚀 Enabling AI SaaS Factory Migration Features...')

// Enable UI Shell Migration (Module 1)
localStorage.setItem('saas-factory-feature-flags', JSON.stringify({
  ui_shell_v2: true,           // Enable new Next.js UI shell
  auth_supabase: true,         // Enable Supabase authentication
  db_dual_write: true,         // Enable database dual-write
  storage_supabase: true,      // Enable Supabase storage
  jobs_pg: true,               // Enable Supabase jobs
  billing_v2: true,            // Enable new billing system
  emails_v2: true,             // Enable new email system
  observability_v2: true,      // Enable observability
  sentry_enabled: true,        // Enable Sentry error tracking
  vercel_analytics_enabled: true, // Enable Vercel Analytics
  health_monitoring_enabled: true // Enable health monitoring
}))

console.log('✅ Migration features enabled!')
console.log('🔄 Refreshing page to apply changes...')

// Refresh the page to apply the new feature flags
setTimeout(() => {
  window.location.reload()
}, 1000)

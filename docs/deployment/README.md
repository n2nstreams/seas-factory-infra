# SaaS Factory Deployment Guide

## Overview

This guide covers deploying the SaaS Factory application to production using modern cloud infrastructure and best practices.

## 🚀 **Quick Start**

### **1. Prerequisites**
```bash
# Install required tools
npm install -g @supabase/cli
npm install -g vercel

# Verify installations
supabase --version
vercel --version
```

### **2. Environment Setup**
```bash
# Clone and setup
git clone <your-repo>
cd saas-factory
npm run install-all

# Copy environment template
cp ui/env.example ui/.env.local
```

### **3. Deploy to Production**
```bash
# Deploy Supabase backend
npm run supabase:deploy

# Deploy frontend
npm run deploy:frontend

# Deploy Edge Functions
npm run edge:deploy
```

## 🏗️ **Infrastructure Setup**

### **Supabase Project**

#### **1. Create Project**
```bash
# Login to Supabase
supabase login

# Create new project
supabase projects create saas-factory-prod
```

#### **2. Configure Environment**
```bash
# Get project credentials
supabase projects api-keys saas-factory-prod

# Update .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

#### **3. Deploy Database Schema**
```bash
# Link to your project
supabase link --project-ref your-project-ref

# Deploy migrations
supabase db push

# Generate types
npm run db:generate-types
```

### **Frontend Deployment**

#### **1. Vercel Setup**
```bash
# Login to Vercel
vercel login

# Deploy to Vercel
vercel --prod
```

#### **2. Environment Variables**
Set these in your Vercel dashboard:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-key
```

#### **3. Custom Domain**
```bash
# Add custom domain
vercel domains add yourdomain.com

# Configure DNS records
# A record: 76.76.19.0
# CNAME record: cname.vercel-dns.com
```

## 🔧 **Edge Functions Deployment**

### **1. Deploy AI Agent Function**
```bash
# Deploy specific function
supabase functions deploy ai-agent

# Deploy all functions
supabase functions deploy
```

### **2. Function Configuration**
```bash
# Set function secrets
supabase secrets set OPENAI_API_KEY=your-key
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=your-key

# Verify deployment
supabase functions list
```

### **3. Test Functions**
```bash
# Test locally
supabase functions serve ai-agent

# Test deployed function
curl -X POST https://your-project.supabase.co/functions/v1/ai-agent \
  -H "Authorization: Bearer your-anon-key" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## 🗄️ **Database Management**

### **1. Schema Migrations**
```bash
# Create new migration
supabase migration new add_new_feature

# Apply migrations
supabase db push

# Reset database (development only)
supabase db reset
```

### **2. Data Seeding**
```bash
# Create seed file
supabase db seed

# Run seed
supabase db reset --seed
```

### **3. Backup and Restore**
```bash
# Create backup
supabase db dump --data-only

# Restore from backup
supabase db restore backup.sql
```

## 🔒 **Security Configuration**

### **1. Row Level Security**
```sql
-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.code_modules ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);
```

### **2. API Security**
```bash
# Set CORS policies
supabase functions deploy ai-agent --no-verify-jwt

# Configure rate limiting
# Add to Edge Function
const rateLimit = {
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
};
```

### **3. Environment Security**
```bash
# Rotate keys regularly
supabase projects api-keys rotate saas-factory-prod

# Use service role key only in Edge Functions
# Never expose in frontend code
```

## 📊 **Monitoring and Logging**

### **1. Supabase Dashboard**
- **Database**: Monitor query performance
- **Auth**: Track user signups and logins
- **Edge Functions**: View function logs and metrics
- **Storage**: Monitor file uploads and usage

### **2. Vercel Analytics**
```bash
# Enable analytics
vercel analytics enable

# View performance metrics
vercel analytics
```

### **3. Custom Monitoring**
```typescript
// Add to Edge Functions
const logActivity = async (userId: string, action: string) => {
  await supabase
    .from('user_activity')
    .insert({
      user_id: userId,
      action,
      details: { timestamp: new Date().toISOString() }
    });
};
```

## 🚀 **CI/CD Pipeline**

### **1. GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - run: npm ci
      - run: npm run build
      - run: npm run test
      
      - run: npm run supabase:deploy
      - run: npm run edge:deploy
      - run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

### **2. Automated Testing**
```bash
# Run tests before deployment
npm run test:all

# Type checking
npm run type-check

# Linting
npm run lint
```

### **3. Deployment Validation**
```bash
# Health checks
curl https://yourdomain.com/api/health

# Function tests
curl https://your-project.supabase.co/functions/v1/ai-agent/health
```

## 🔄 **Rollback Strategy**

### **1. Database Rollback**
```bash
# Revert to previous migration
supabase migration down

# Restore from backup
supabase db restore backup.sql
```

### **2. Frontend Rollback**
```bash
# Revert Vercel deployment
vercel rollback

# Deploy specific version
vercel --prod --force
```

### **3. Function Rollback**
```bash
# Deploy previous version
supabase functions deploy ai-agent --version previous

# Check function versions
supabase functions list --include-versions
```

## 📈 **Performance Optimization**

### **1. Database Optimization**
```sql
-- Add indexes for common queries
CREATE INDEX idx_code_modules_project_language ON public.code_modules(project_id, language);
CREATE INDEX idx_ai_sessions_user_created ON public.ai_sessions(user_id, created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM public.code_modules WHERE project_id = 'uuid';
```

### **2. Frontend Optimization**
```bash
# Bundle analysis
npm run build:analyze

# Optimize images
npm run optimize:images

# Enable compression
# Configure in Vercel dashboard
```

### **3. Edge Function Optimization**
```typescript
// Use connection pooling
const supabase = createClient(url, key, {
  db: {
    pool: { min: 2, max: 10 }
  }
});

// Implement caching
const cache = new Map();
const getCachedResult = (key: string) => cache.get(key);
```

## 🧪 **Testing in Production**

### **1. Staging Environment**
```bash
# Deploy to staging
vercel --env staging

# Test with staging Supabase
supabase link --project-ref staging-project-ref
```

### **2. Feature Flags**
```typescript
// Implement feature flags
const isFeatureEnabled = (feature: string) => {
  return process.env[`FEATURE_${feature.toUpperCase()}`] === 'true';
};

// Use in components
{isFeatureEnabled('new_ui') && <NewComponent />}
```

### **3. A/B Testing**
```typescript
// Simple A/B testing
const getVariant = (userId: string) => {
  const hash = createHash('md5').update(userId).digest('hex');
  return parseInt(hash.slice(0, 8), 16) % 2 === 0 ? 'A' : 'B';
};
```

## 🔍 **Troubleshooting**

### **1. Common Issues**
```bash
# Function not deploying
supabase functions logs ai-agent --follow

# Database connection issues
supabase status
supabase db reset

# Frontend build errors
npm run clean
npm run install-all
```

### **2. Debug Mode**
```bash
# Enable debug logging
supabase functions serve --debug

# View detailed logs
supabase logs --follow
```

### **3. Performance Issues**
```bash
# Database performance
supabase db analyze

# Function performance
supabase functions logs ai-agent --include-metrics
```

## 📚 **Additional Resources**

- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance.html)

---

This deployment guide provides a comprehensive approach to deploying the SaaS Factory application with best practices for security, performance, and maintainability.

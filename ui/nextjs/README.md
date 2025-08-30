# AI SaaS Factory - Next.js Migration

## 🚀 **Module 1: UI Shell Swap - Next.js + shadcn/ui**

This directory contains the new Next.js UI shell that will replace the existing React + Vite frontend while maintaining full compatibility with the current backend systems.

## 📋 **Migration Status**

### ✅ **Completed**
- [x] Next.js 15 project setup with App Router
- [x] shadcn/ui component library integration
- [x] Glassmorphism design system with natural olive greens
- [x] Feature flag infrastructure for migration control
- [x] Authentication provider with backend compatibility
- [x] Navigation component with responsive design
- [x] Landing page at `/app2` route
- [x] Dashboard page with glassmorphism UI
- [x] Feature flag management panel for admins
- [x] Tailwind CSS configuration with custom design tokens

### 🔄 **In Progress**
- [ ] Component migration from legacy React components
- [ ] Route structure implementation
- [ ] API integration layer
- [ ] Testing and validation

### 📋 **Pending**
- [ ] Sign-in/Sign-up pages
- [ ] Additional dashboard pages
- [ ] Component library expansion
- [ ] Performance optimization
- [ ] Accessibility improvements

## 🏗️ **Architecture**

### **Project Structure**
```
src/
├── app/                    # Next.js App Router
│   ├── app2/              # New UI shell routes
│   │   ├── dashboard/     # Main dashboard
│   │   ├── admin/         # Admin features
│   │   └── page.tsx       # Landing page
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main routing logic
│   └── globals.css        # Global styles
├── components/             # React components
│   ├── providers/         # Context providers
│   │   ├── AuthProvider   # Authentication state
│   │   └── FeatureFlagProvider # Feature flags
│   └── Navigation.tsx     # Main navigation
└── lib/                   # Utility functions
    └── utils.ts           # Common utilities
```

### **Key Features**
- **Feature Flag Control**: `ui_shell_v2` flag controls migration rollout
- **Dual Routing**: `/app2` for new UI, legacy routes preserved
- **Glassmorphism Design**: Modern glass-like UI with natural olive greens
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Backend Compatibility**: Maintains existing API boundaries

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 18+ 
- npm or yarn
- Supabase project configured (for Module 4 functionality)

### **Installation**
```bash
cd ui/nextjs
npm install
```

### **Development**
```bash
npm run dev
```

The new UI will be available at `http://localhost:3000/app2`

### **Feature Flag Control**
1. Navigate to `/app2/admin/feature-flags` (requires growth plan)
2. Toggle `ui_shell_v2` to enable new UI shell
3. Users will be automatically routed to new interface

## 🎨 **Design System**

### **Color Palette**
- **Primary**: Natural olive greens (#5a715a, #475a47, #3a483a)
- **Glass**: Transparent overlays with backdrop blur
- **Accents**: Complementary colors for interactive elements

### **Components**
- **Glass Cards**: Transparent cards with backdrop blur
- **Glass Buttons**: Interactive buttons with glassmorphism effect
- **Glass Inputs**: Form inputs with glass styling
- **Responsive Grid**: Mobile-first grid system

### **Typography**
- **Font**: Inter (Google Fonts)
- **Weights**: Regular, Medium, Semibold, Bold
- **Scales**: Responsive typography with Tailwind utilities

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Feature Flags (Production)
NEXT_PUBLIC_FEATURE_UI_SHELL_V2=true
NEXT_PUBLIC_FEATURE_AUTH_SUPABASE=true
NEXT_PUBLIC_FEATURE_DB_DUAL_WRITE=false

# Backend Configuration (Next.js API routes only)
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_HEALTH_API_URL=/api/health
```

### **Feature Flags**
- `ui_shell_v2`: Controls new UI shell activation
- `auth_supabase`: Controls Supabase authentication
- `db_dual_write`: Controls database dual-write mode
- `storage_supabase`: Controls Supabase storage
- `jobs_pg`: Controls PostgreSQL job processing
- `billing_v2`: Controls new billing system
- `emails_v2`: Controls new email service

## 🧪 **Testing**

### **Manual Testing Checklist**
- [ ] Feature flag controls work correctly
- [ ] Navigation responsive on mobile/desktop
- [ ] Glassmorphism effects render properly
- [ ] Routing between legacy and new UI works
- [ ] Authentication state persists correctly
- [ ] Admin panel accessible only to growth users

### **Performance Testing**
- [ ] Lighthouse score > 90
- [ ] LCP < 2.5s
- [ ] CLS < 0.1
- [ ] FID < 100ms

## 🔄 **Migration Process**

### **Phase 1: Foundation ✅**
- Next.js project setup
- Design system implementation
- Feature flag infrastructure
- Basic routing structure

### **Phase 2: Core Components 🔄**
- Component migration from legacy
- Route implementation
- API integration layer
- Testing and validation

### **Phase 3: Rollout**
- Feature flag activation
- Canary deployment
- User feedback collection
- Performance monitoring

### **Phase 4: Completion**
- Full migration
- Legacy system cleanup
- Documentation updates
- Team training

## 🚨 **Rollback Procedures**

### **Immediate Rollback**
1. Set `ui_shell_v2` feature flag to `false`
2. All users automatically return to legacy UI
3. No data loss or service interruption

### **Emergency Rollback**
1. Disable feature flag system
2. Redirect all traffic to legacy routes
3. Maintain existing functionality

## 📊 **Monitoring & Metrics**

### **Key Metrics**
- Feature flag activation rate
- User adoption of new UI
- Performance benchmarks
- Error rates and user feedback

### **Success Criteria**
- Visual parity with legacy UI
- Performance improvements
- User satisfaction maintained
- Zero data loss during migration

## 🤝 **Contributing**

### **Development Guidelines**
- Follow Next.js best practices
- Maintain glassmorphism design system
- Use TypeScript for all components
- Implement proper accessibility features
- Test feature flags thoroughly

### **Code Standards**
- ESLint configuration included
- Prettier formatting
- TypeScript strict mode
- Component documentation

## 📚 **Resources**

### **Documentation**
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Glassmorphism Design](https://www.figma.com/community/file/1012883659109452684)

### **Migration References**
- [Strangler Fig Pattern](https://martinfowler.com/articles/strangler-fig.html)
- [Feature Flag Best Practices](https://launchdarkly.com/blog/feature-flag-best-practices/)
- [Incremental Migration Strategies](https://aws.amazon.com/blogs/architecture/strangler-fig-pattern-for-migrating-to-aws/)

---

**Migration Status**: Phase 1 Complete ✅  
**Next Phase**: Core Component Migration  
**Target Completion**: Module 1 Complete  
**Confidence Level**: 9/10 ⭐⭐⭐⭐⭐

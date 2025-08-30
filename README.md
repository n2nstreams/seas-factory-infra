# 🚀 AI SaaS Factory

> **Modern, Clean Architecture for AI-Powered SaaS Applications**

[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Latest-green?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3+-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

## 🎯 **What is AI SaaS Factory?**

AI SaaS Factory is a **modern, clean architecture** for building AI-powered SaaS applications. After a complete legacy cleanup, the project now features:

- **🤖 AI Agents** - React-based components for intelligent automation
- **⚡ Next.js Frontend** - Modern React with App Router and TypeScript
- **🗄️ Supabase Backend** - PostgreSQL with real-time features and auth
- **🎨 Glassmorphism UI** - Beautiful, modern design system
- **☁️ Supabase Infrastructure** - Scalable backend-as-a-service platform

## ✨ **Key Features**

### **AI Agent System**
- **Tech Stack Agent** - Technology recommendations and analysis
- **Design Agent** - UI/UX generation and prototyping
- **Code Generation Agent** - Automated development assistance
- **QA Agent** - Testing and validation automation
- **Orchestrator Agent** - Workflow management and coordination

### **Modern Frontend**
- **Next.js 14+** with App Router
- **React 18+** with modern hooks
- **TypeScript** for type safety
- **Tailwind CSS** with custom design system
- **shadcn/ui** components
- **Glassmorphism design** with natural olive green theme

### **Backend & Data**
- **Supabase** - PostgreSQL with real-time subscriptions
- **Row Level Security** - Multi-tenant data isolation
- **Built-in Authentication** - OAuth providers (Google, GitHub)
- **Real-time Updates** - Live data synchronization
- **Database Migrations** - Schema versioning and management
- **Edge Functions** - Serverless backend logic
- **Storage** - File uploads and management

### **Infrastructure**
- **Supabase** - Backend-as-a-service platform
- **Vercel** - Frontend deployment platform
- **GitHub Actions** - CI/CD automation
- **PostgreSQL** - Reliable database with extensions

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ 
- npm or yarn
- Supabase account

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "SaaS Factory"
   ```

2. **Install dependencies**
   ```bash
   cd ui/nextjs
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Fill in your Supabase credentials
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   ```
   http://localhost:3000
   ```

## 🏗️ **Project Structure**

```
SaaS Factory/
├── ui/nextjs/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── app2/         # New application shell
│   │   │   │   ├── admin/    # Admin dashboard
│   │   │   │   ├── dashboard/ # User dashboard
│   │   │   │   └── ...       # Other app routes
│   │   │   └── api/          # API routes
│   │   ├── components/       # React components
│   │   └── lib/              # Utility libraries
│   └── public/               # Static assets
├── ai_docs/                   # Project documentation
├── agents/                    # AI agent definitions
├── docs/                      # Additional documentation
└── LICENSE                    # Project license
```

## 🎨 **Design System**

### **Glassmorphism Theme**
- **Natural olive greens** as base colors
- **Backdrop blur effects** for modern UI
- **Semi-transparent elements** for depth
- **Smooth animations** and transitions

### **Color Palette**
- **Primary:** Natural olive greens
- **Secondary:** Complementary earth tones
- **Accent:** Strategic highlight colors
- **Neutral:** Balanced grays and whites

## 🔧 **Development**

### **Available Scripts**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript check
```

### **Code Quality**
- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** for type safety
- **Husky** for git hooks

## 📚 **Documentation**

- **[Tech Stack](./Tech_Stack.md)** - Complete technology overview
- **[Project Architecture](./PROJECT_ARCHITECTURE_MAPPING.md)** - Architecture documentation
- **[AI Docs](./ai_docs/)** - Organized project documentation
- **[Migration Summary](./ai_docs/PROJECT_STRUCTURE_EXTRACTION_SUMMARY.md)** - Legacy cleanup summary

## 🌟 **What's New (Post-Legacy Cleanup)**

### **✅ Completed**
- **Legacy Python backend removed** - Clean, modern architecture
- **Google Cloud infrastructure removed** - Simplified to Supabase
- **Outdated documentation cleaned up** - Focused, relevant docs
- **Project structure organized** - Logical file organization
- **Modern tech stack** - Next.js + React + Supabase + AI agents

### **🚀 Ready For**
- **New feature development** - Clean codebase
- **AI agent enhancement** - Modern component system
- **Performance optimization** - Optimized architecture
- **Scalability improvements** - Supabase-native design

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Next.js team** for the amazing React framework
- **Supabase team** for the powerful backend platform
- **Tailwind CSS team** for the utility-first CSS framework
- **shadcn/ui team** for the beautiful component library

---

**Status:** ✅ **Modern, Clean Architecture Ready for Development**  
**Last Updated:** August 30, 2025 - Post-Legacy Cleanup  
**Version:** 2.0.0 - Clean Architecture Edition 
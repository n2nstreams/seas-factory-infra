# AI SaaS Factory - Frontend Dashboard

A React-based dashboard for the AI SaaS Factory platform, featuring a glassmorphism design with natural olive green theming.

## Features

### 🎯 **Night 74: Onboarding Wizard** 
**First-time user experience with interactive dashboard tour**

The onboarding wizard provides new users with a guided introduction to the AI SaaS Factory dashboard:

- **Automatic Detection**: Shows automatically on first dashboard login
- **5-Step Interactive Tour**:
  1. **Welcome** - Introduction to AI SaaS Factory capabilities
  2. **Submit Ideas** - How to submit your first SaaS idea
  3. **Project Stages** - Understanding the AI factory pipeline
  4. **Dashboard Navigation** - Key features and tabs
  5. **Support Resources** - Where to get help

- **Glassmorphism Design**: Consistent with the platform's natural olive green theme
- **Element Highlighting**: Interactive highlights of key dashboard elements
- **User Preferences**: Persistent tracking via localStorage
- **Development Tools**: Built-in testing utilities for development

#### Usage

The onboarding wizard appears automatically for new users. For testing purposes, developers can use:

```javascript
// In browser console (development mode only)
window.onboardingDevUtils.forceShowOnboarding()
window.onboardingDevUtils.logPreferences()
```

#### Implementation Details

- **Component**: `src/components/OnboardingWizard.tsx`
- **State Management**: `src/lib/userPreferences.ts`
- **Integration**: `src/pages/Dashboard.tsx`
- **Highlighting**: CSS animations with `data-onboarding` attributes

The wizard uses a step-by-step modal approach with:
- Progress indicator
- Navigation controls (Next/Back/Skip)
- Element highlighting with pulsing animations
- Glassmorphism styling with backdrop blur effects

### Other Features

- **Real-time Project Monitoring**
- **Build Progress Tracking** 
- **Billing & Subscription Management**
- **Factory Pipeline Visualization**
- **Responsive Glassmorphism Design**

## Development

```bash
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

## Architecture

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** for component primitives
- **Lucide React** for icons

## Browser Support

- Modern browsers with backdrop-filter support
- Graceful degradation for older browsers
- Mobile-responsive design

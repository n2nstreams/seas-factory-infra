# Forge95 User Journey Audit Report

## Executive Summary

Forge95 aims to help non-technical founders turn SaaS ideas into revenue-generating businesses by automatically designing, coding, and deploying web applications using AI agents.  
The public marketing site emphasises key metrics such as 50+ SaaS products already built, an average build time of 48 hours, zero developer costs, and full code ownership.  
The homepage describes a **three-step journey**: Submit Idea → AI builds → Launch SaaS.

During this audit, the homepage and certain flows were accessible, but multiple critical user journeys (such as `/submit-idea`, `/faq`, `/pricing`) returned **404 Not Found** errors when navigated directly. Sign-up was possible via the homepage CTA, but the login route was unstable. The support chat bubble functioned.  
Overall, while the vision is clear and attractive, execution suffers from broken routes, inconsistent navigation, and limited accessibility of core features.

---

## Issues Identified

### Critical Issues
1. **Broken Routing**
   - **Observed:** Direct navigation to `/submit-idea`, `/faq`, `/pricing`, and `/signin` returned `404 Not Found`.
   - **Reproduction:** Type the URLs directly or use top-navigation links.
   - **Impact:** Users cannot reliably reach idea submission, FAQ, pricing, or login pages.

2. **Sign-in / Sign-up Inconsistency**
   - **Observed:** Header “Sign In” leads to 502/404 depending on path.  
   - **Workaround:** Sign-up works only via homepage “Start Building Now” CTA.
   - **Impact:** Returning users may not be able to log in.

### Major Issues
1. **Form Input Bugs**
   - Email and password fields on auth pages sometimes fail to capture input unless navigated by `Tab`.
   - Placeholder text overlaps with typed content.
2. **Marketplace Unreachable**
   - No functional link or visible catalogue of SaaS products available.
3. **Pricing Cards**
   - Shown on homepage but “Get Started” CTAs often lead to errors.

### Minor Issues
1. **Accessibility**
   - Chat widget overlaps with footer on small screens.  
   - Contrast of CTA buttons vs. background could be improved for WCAG compliance.
2. **Clarity**
   - Users not always informed when features are “coming soon.”
   - Some navigation items scroll to anchors, others break routing.

---

## Opportunities for Improvement
- **Fix React Router configuration** for production: ensure routes like `/submit-idea`, `/faq`, and `/signin` resolve via fallback to `index.html`.  
- **Unify authentication flow** so “Sign In” and “Sign Up” are handled consistently.  
- **Expose Marketplace catalogue** with either live products or demo entries.  
- **Improve accessibility**: add aria-labels, ensure color contrast compliance, fix chat bubble overlap.  
- **Add guided onboarding** after signup to explain the 3-step journey.

---

## Positive Highlights
- **Strong Value Proposition**: Messaging around AI-built SaaS in 48h is clear and compelling.  
- **Modern Design**: Landing page design is visually clean and professional, with trust-building metrics.  
- **Transparent Pricing**: Plans listed from Free to Enterprise, even if links are broken.  
- **Support Presence**: Chat widget works, offering user contact with the team.  

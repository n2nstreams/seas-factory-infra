

# Forge95 User Journey Audit (Post-Fixes – August 2025)

## Executive summary

After resolving several routing issues and updating the interface, Forge95.com offers a more cohesive visitor experience. The homepage now features a clear value proposition—**“Transform your idea into a production-ready SaaS—Automatically”**—and an interactive idea input box with suggested chips that encourage engagement. Internal navigation (How It Works → Pricing → FAQ) generally behaves correctly, and the **SaaS Marketplace** is reachable with a grid of product cards.

Two blockers remain on core journeys:

- **Account creation intermittently fails** (HTTP 500) and the **Terms checkbox intermittently unticks** on submit.  
- **Anonymous idea submission** progresses through Steps 1–3 but **submitting returns HTTP 422** (likely requires an authenticated user or stricter validation).

Sign-in did work in at least one path and led to a functional **Dashboard + Onboarding Tour**; however, the sign-in success state didn’t consistently persist when returning to the public pages (session/state sync). Overall, the site is close: the flows exist and feel modern, but reliability on auth and submission endpoints must be addressed to unlock the full journey.

---

## Method

- Tested on August 2025 as a first-time visitor via `https://forge95.com` with default browser settings.  
- Followed these flows:  
  1) Homepage → How It Works → Pricing → FAQ  
  2) Marketplace browse → product card actions  
  3) Submit Idea wizard (Steps 1–3, submission)  
  4) Sign Up (create account)  
  5) Sign In → Dashboard → Onboarding tour → Quick Start actions  
  6) Support/help surface checks  
- For each step, evaluated **Clarity, Performance, Accuracy, Accessibility** and documented any errors with exact steps.

---

## Journey findings (step-by-step)

### 1) Homepage
- **Clarity:** Strong headline and subhead. The **idea input** with example chips reduces blank-page anxiety. Primary CTAs are visible; top nav is concise.
- **Performance:** Loads quickly; smooth hero animations.
- **Accuracy:** How-it-works anchor and CTA to Pricing behave as expected.
- **Accessibility:** Good color contrast on CTAs; ensure input/controls have visible focus states and proper `aria-label`s. Headline hierarchy appears logical.

### 2) How It Works (3-step overview)
- **Clarity:** Three steps are clear (Submit idea → AI builds → Launch). CTA **“Start your 3-step journey”** scrolls to Pricing (expected).
- **Performance:** Instant anchor scroll; images load fast.
- **Accuracy:** Copy aligns with masterplan (multi-agent pipeline).
- **Accessibility:** Steps and icons appear keyboard-reachable; consider adding skip-links between major sections.

### 3) Pricing
- **Clarity:** Plan cards are understandable; “Free” clearly highlighted.
- **Performance:** Quick; toggles and cards render instantly.
- **Accuracy:** “Get Started Free” routes to **Sign Up** (correct). Paid CTAs point to contact/sales or start flows (verify final link targets).
- **Accessibility:** Ensure plan feature lists are semantic lists; confirm buttons have descriptive accessible names.

### 4) FAQ
- **Clarity:** Accordion questions are scannable; answers short and useful.
- **Performance:** Expand/collapse is instant.
- **Accuracy:** Topics align to expected pre-sales concerns.
- **Accessibility:** Accordions should use `button` with `aria-expanded` and `aria-controls`. Each panel should be labelled and focus returned sensibly.

### 5) Marketplace
- **Clarity:** Filters + grid of SaaS cards (status chips like Beta/Live) are intuitive; **View demo** and **Get started** CTAs are recognizable.
- **Performance:** Grid populates quickly; images/avatars load fast.
- **Accuracy:** Demo CTAs often route to **Sign Up / Sign In** (expected when gated).
- **Accessibility:** Card layout is keyboard navigable; ensure card titles are links with discernible names; add alt text for logos and screenshots.

### 6) Submit Idea wizard (Step 1 → Step 3)
- **Clarity:** Step headings and progress bar are clear. Field labels are explicit (Project Name, Description, Category, Priority).
- **Performance:** Fast field interactions; dropdowns responsive.
- **Accuracy:**  
  - **Pass:** Can complete Steps 1–3 (Business details), including selecting **Subscription (SaaS)** model, timeline, and budget.  
  - **Fail:** **Final submission returns HTTP 422** (validation or auth requirement). If auth is required, the UI should block unauthenticated progression earlier and communicate why.
- **Accessibility:** All fields reachable by keyboard; add inline error messages next to the fields on validation failure (422 currently shows generic failure).

### 7) Sign Up
- **Clarity:** Form design is clean: First/Last name, Email, Password + Confirm, TOS checkbox.
- **Performance:** Field interactions are instant.
- **Accuracy (issues):**  
  - **HTTP 500 on Create Account** (intermittent).  
  - **TOS checkbox state toggles off** on submit in some attempts; feels like a frontend re-render or form state reset issue.  
  - When failure occurs, no granular error is shown (generic server error).
- **Accessibility:** Announce form errors to screen readers; keep the checkbox state stable during submission; keep focus on the first invalid field.

### 8) Sign In → Dashboard → Onboarding
- **Clarity:** Sign in is straightforward. Dashboard displays a **Quick Start** card and offers a 5-step **Onboarding Tour** (Idea → Design → Development → Testing → Deployment; Support).
- **Performance:** Onboarding popovers are snappy.
- **Accuracy (minor):** After signing in, **public pages didn’t always reflect the signed-in state** (e.g., still showing Sign Up/Sign In prompts). Likely a client-side store or cookie sync timing issue.  
- **Accessibility:** Ensure tour steps are dismissible via keyboard and restore focus to the triggering control.

### 9) Help/Support
- **Clarity:** The “Get Help & Support” step in the tour advertises chat/docs/community. Surface these links in the global header/footer too.
- **Performance:** N/A (links).
- **Accuracy:** Ensure all links resolve to live resources (docs, community).
- **Accessibility:** Provide descriptive link names.

---

## Issues list (with reproduction steps)

### Critical
1) **Account creation intermittently fails**  
   - **Steps:** Pricing → “Get Started Free” → Fill form (valid data) → Check TOS → **Create Account** → **HTTP 500**.  
   - **Expected:** Account created, redirect to dashboard, email verification (if applicable).  
   - **Impact:** Blocks any paid conversion and idea submissions that require login.  
   - **Notes:** Also observed **TOS checkbox unticking** at submission—frontend state reset or separate controlled input issue.

2) **Idea submission returns HTTP 422**  
   - **Steps:** Submit Idea → Complete Steps 1–3 with valid values → **Submit Idea** → **422**.  
   - **Expected:** Confirmation screen, ticket ID, or redirect to project brief.  
   - **Impact:** Blocks the flagship “AI SaaS Factory” path for unauthenticated users.  
   - **Notes:** If auth is required, gate at Step 0 with explicit login requirement; otherwise, return field-level validation hints.

### Major
3) **Session state not universally recognized**  
   - **Steps:** Sign in → Navigate back to public pages (e.g., home/submit-idea).  
   - **Observed:** Some surfaces continue to display “Create account / Sign in” prompts despite active session.  
   - **Impact:** Confusing mixed state; may block actions or degrade trust.

4) **Form UX edge cases**  
   - **Observed:** Step 1 fields occasionally appear to lose typed values when scrolling quickly or changing sections.  
   - **Impact:** User confusion, re-entry of data.

### Minor
5) **CTA targets inconsistency**  
   - Some CTAs scroll to anchors rather than start flows—ensure key buttons (e.g., “Start building”) always open the intended action (wizard or signup), not just scroll.

6) **Error messaging**  
   - Generic messages on 422/500. Provide specific, inline errors and user-friendly text (e.g., “Please sign in to submit your idea” or “Email already in use.”)

7) **Accessibility polish**  
   - Verify focus rings on all interactive elements; ensure ARIA on accordions; announce form errors; provide alt text on marketplace logos.

---

## Opportunities for improvement

1) **Harden auth flows**  
   - Stabilize signup endpoint (500) and front-end TOS state. Add inline, field-level validation and top-level error summary.  
   - Persist session in a single source of truth (cookie + client store), and rehydrate it on route change; expose an authenticated header state.

2) **Clarify idea submission requirements**  
   - If login is required to submit, block anonymous progress and surface a short explainer: “Create a free account to save and submit your idea.”  
   - If anonymous is allowed, fix 422 by returning field-level guidance and server-side validation messages.

3) **Improve CTA consistency**  
   - Make “Start building” and equivalent CTAs open the wizard or signup modal directly (not just an anchor). Use one primary style for the main action.

4) **Marketplace depth**  
   - Add filters (category, status, price), badges (Live/Beta), and short feature bullets per card. Consider quick-view modals with screenshots.

5) **Visual polish to surpass competitors**  
   - Adopt a modern gradient or subtle texture in hero; keep brand green as accent on CTAs.  
   - Introduce micro-interactions (hover lift, button press depth), and keep spacing generous across cards and forms.

6) **Support surfaces**  
   - Promote help links in the header/footer; add a compact “Need help?” sticky or chat widget that doesn’t block content.

---

## Positive highlights (aligned with masterplan2.md)

- **Clear positioning & narrative:** The multi-agent “factory” story comes through well across How-It-Works and the Dashboard tour.  
- **Modern, fast UI:** Pages load quickly; animations are tasteful; cards, rounded corners, and typography feel contemporary.  
- **Marketplace presence:** A live grid of products signals credibility and momentum.  
- **Guided onboarding:** The 5-step tour helps first-time users map your process to their expectations.

---

## Summary

Forge95 is very close to a smooth, end-to-end first-time experience. Focus engineering efforts on:  
1) **Signup reliability** (eliminate 500, stabilize TOS state),  
2) **Submission behavior** (resolve 422 or require login earlier), and  
3) **Session persistence** across public/app routes.  

Once these are solid, double down on CTA consistency, marketplace depth, and small-delight visuals to confidently exceed competitors on perceived quality and trust.
Forge95 User Journey Audit (Late August 2025)

Overview
	•	After implementing the previous recommendations, Forge95’s site loads cleanly at https://forge95.com without certificate errors.
	•	The home page prominently states “Transform Your Idea into a Production‑Ready SaaS – Automatically” and features a search-like idea input with popular idea suggestions.
	•	Navigation includes Home, Submit Idea, Marketplace, Pricing, FAQ, Sign In, and Get Started Free.
	•	A chat widget persists on the lower right corner of every page, but the backend is currently unreachable.

Homepage
	•	Clarity: The hero section is visually attractive with bold typography and an interactive idea input. It clearly conveys the value proposition and invites users to start building.
	•	Performance: The page and its animations load quickly and respond smoothly.
	•	Accuracy: Typing an idea into the search box and clicking Start Building redirects to the idea submission page, but the typed value is not carried over (defaults to “TaskManager AI”).
	•	Accessibility: Good color contrast and legible fonts. The interactive idea input and the navigation bar are keyboard accessible.

Account creation & login
	•	Manual sign‑up:
	•	The sign‑up form collects first name, last name, email, password, and confirm password. It includes password strength feedback and a Terms of Service checkbox.
	•	Issue: After filling valid details and checking the Terms box, clicking Create Account unticks the Terms box and leaves the user on the same page. No account is created and no server error is shown.
	•	Social sign‑up (GitHub/Google):
	•	Clicking Continue with GitHub redirects to github.com/login with the placeholder your_github_client_id, which confirms an OAuth integration stub but not a configured client.
	•	Clicking Continue with Google redirects to accounts.google.com/oauth2/v2/auth with your_google_client_id and shows a 404 error page.
	•	Manual sign‑in:
	•	The sign‑in page has social options and an email/password form. Attempting to log in with test credentials results in an “Invalid email or password” message, as expected when sign‑up fails.
	•	Social sign‑in:
	•	GitHub sign‑in goes to GitHub’s login form (same placeholder client), but cannot authenticate back.
	•	Google sign‑in again produces a 404 error.
	•	State persistence: When arriving at authenticated pages (e.g., dashboard) from a past session, the top navigation still shows “Sign In” and “Get Started,” indicating a state sync issue.

Idea submission portal
	•	Step 1 (Project basics):
	•	Asks for project name, description, category (from a dropdown), and priority level.
	•	The form loads correctly and accepts input, but clicking Next scrolls the page back to the top instead of progressing to Step 2.
	•	The progress bar remains at Step 1 of 4, implying that guests cannot advance without logging in, yet no clear message states that login is required.
	•	Steps 2–4: Could not be reached in this session due to the Step 1 blocker.
	•	Help links: Buttons for View Example Ideas, Check Pricing, and View Documentation sit below the form, improving user guidance.

Marketplace
	•	Clarity: The SaaS Marketplace page lists a hero heading and explains that users can discover AI‑powered SaaS solutions.
	•	Performance: The page loads quickly and includes a search bar, category filter and rating sort dropdown.
	•	Accuracy: The product grid currently displays “No products found.” There are no sample products or demos to explore.
	•	Navigation: A “Submit Your Idea” call‑to‑action encourages users to build their own SaaS but routes back to the sign‑up barrier.

Pricing & plans
	•	Plans offered: Free ($0), Starter ($30/mo), Pro ($60/mo), and Scale ($120/mo). Each lists included features and core agent access.
	•	CTA behavior: Buttons such as Get Started Free, Start Building, Scale Up, and Go Enterprise all redirect users to the sign‑up page.
	•	Toggle: A monthly/yearly switch is present but does not visibly update pricing (no yearly discounts).
	•	Clarity & design: Pricing cards use icons, short descriptions, and clear pricing, making comparison easy.

FAQ
	•	Coverage: The FAQ page provides categories (Features, Getting Started, Technical) and collapsible questions.
	•	Content: Answers describe the platform (e.g., it automates design, development and deployment) and explain the AI agent pipeline.
	•	Accessibility: Accordions use buttons and expand/collapse via keyboard; however, there is a banner noting that “default FAQs” are being used, which may confuse visitors.

Support chat
	•	The green chat widget opens a panel labelled “Chat with our AI.”
	•	Typing a message and sending returns “Unable to connect to chat service. Please try again later.” so the chat backend is offline.
	•	Without functional chat, users have no direct support channel from within the site.

Performance & accessibility
	•	Speed: All pages (home, submit idea, marketplace, pricing, FAQ) load within a couple of seconds.
	•	Responsiveness: The design adapts well to different screen widths and maintains readability.
	•	Accessibility concerns:
	•	The small Terms checkbox on the sign‑up form is difficult to click and repeatedly unticks itself.
	•	Form validation lacks descriptive error messages (e.g., after the sign‑up failure).
	•	The multi‑step submission wizard does not clearly indicate that login is required to proceed.

Critical issues (blockers)
	•	Broken account creation: The manual sign‑up form resets the Terms checkbox upon submission and never creates an account. Without an account, users cannot progress beyond Step 1 of idea submission or access paid features.
	•	Misconfigured social logins: GitHub uses placeholder client_id and Google OAuth returns 404 errors, so social sign‑up/sign‑in cannot succeed.
	•	Idea submission gating: The Next button on Step 1 loops the user back to the top of the page, preventing progression to further steps. The site does not explain that a user must log in first.
	•	Chat service unreachable: The support chat shows an error message and cannot deliver assistance.

Major issues
	•	Session handling: Even after sign‑in (from previous sessions), the top nav continues to show Sign In rather than the user’s account or a sign‑out option.
	•	Marketplace emptiness: An empty product grid undermines the credibility of the marketplace; adding sample products or demos would improve trust.
	•	Pricing toggles: The monthly/yearly toggle has no effect on displayed prices, which may confuse users expecting annual discounts.
	•	Interactive hero bug: The idea typed in the homepage search box is not carried into Step 1 of the submission wizard.

Minor issues
	•	Terms checkbox size: It is small and easy to miss, and it resets when Create Account is clicked.
	•	Form field preservation: Data typed into the idea submission form is lost when the page scrolls back to the top; autosave or messaging would be helpful.
	•	FAQ disclaimer: A note about default FAQs indicates the service may still be spinning up; this breaks immersion.
	•	Navigation state: After following CTAs (e.g., from Pricing), there is no “Back to Pricing” link and the user is simply dropped into sign‑up.

Opportunities for improvement
	•	Fix the sign‑up process: Maintain the Terms checkbox state and display field‑level error messages. Confirm account creation with a success message and redirect to the dashboard.
	•	Configure OAuth providers: Replace placeholder client IDs with real ones for GitHub and Google; provide fallback if social logins fail.
	•	Inform guests early: Show a clear message on the idea submission page that logging in is required to complete the process. Disable or hide Next until prerequisites are met.
	•	Populate the marketplace: Seed with example AI SaaS products, including demo pages and purchase flows, to demonstrate value.
	•	Implement chat support: Connect the chat widget to a live or AI‑powered support channel or remove it until ready.
	•	Persist form data: When moving through steps or if a user scrolls to the top, maintain the state of the fields to avoid re‑entry.
	•	Improve navigation after actions: If CTAs lead to sign‑up, provide clear breadcrumb or back buttons to return to the previous context.
	•	Audit accessibility: Ensure all interactive elements have proper focus states, labels and keyboard operability.

Positive highlights
	•	Modern, cohesive design: The updated palette, typography, and layout feel polished and align with a tech‑forward brand.
	•	Informative pricing: Plan cards clearly outline features and use consistent icons.
	•	Engaging how‑it‑works storytelling: The three‑step process, progress bar, and example ideas reinforce the AI factory concept.
	•	Responsive and fast: Pages render quickly and adapt to different screen sizes without layout breaking.
	•	Good content structure: The FAQ, pricing and marketplace pages each have clear headings and intuitive layouts.
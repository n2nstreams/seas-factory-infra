Forge95 User Journey Audit – After Routing Fixes (August 17 2025)

Executive summary

After the reported routing fixes, Forge95.com shows notable improvements.  Navigating via internal menu links now exposes pages that previously returned 404 or 502 errors.  A SaaS Marketplace page is live and lists a range of AI‑powered products, and the multi‑step idea submission wizard flows from Step 1 to Step 3 without crashing.  The sign‑in form is reachable and styled consistently.  Overall the experience feels more complete than earlier versions.

However, severe functional issues remain: direct URL access often returns an nginx 404 page, account creation still fails due to a Request failed: Failed to fetch error, the idea submission cannot be completed, and marketplace actions (e.g., “View Demo”, “Get Started”) are non‑interactive.  These problems block any real use of the platform.  Visual design has improved slightly, but the site still requires aesthetic refinement to match competitors and deliver a modern, compelling experience.


Detailed findings

Home & landing page

Observation
Comment
Clear hero section
The hero headline (“Transform Your Idea into a Production‑Ready SaaS – Automatically”) is bold and attention‑grabbing.  Sub‑headline explains the AI SaaS factory concept clearly.  A metrics card (“Live Business Dashboard”) shows monthly revenue and active users, giving credibility.
Navigation improvements
Top bar includes links to How It Works, Marketplace, Pricing, FAQ, Sign In, and Get Started Free.  On the www.forge95.com version, clicking these links keeps you within a single‑page app and reveals new sections correctly.
How It Works
The anchor scrolls to three cards explaining the process: 1) Submit Your Idea, 2) AI Agents Build It, 3) Launch Your SaaS.  Each card details the step and has icons and notes such as “Typically completed in 24‑48 hours”.  The flow is clear and loads smoothly.
Pricing section
Pricing cards (Free, Starter, Pro, Scale, Enterprise) show monthly prices and features.  Buttons like “Get Started Free”, “Start Building”, “Scale Up” etc. are present, but all redirect to the sign‑up form.
FAQ section
The FAQ uses collapsible accordions; clicking a question reveals the answer.  This improves interactivity and clarity.


Navigation & routing

Observation
Clarity & Accuracy
Performance
Internal links work on www subdomain
Navigating to Marketplace, Submit Idea and Sign In via the top menu on www.forge95.com loads their respective pages.
Pages load quickly; minimal lag.
Direct URLs still broken
Typing or visiting forge95.com/marketplace, forge95.com/submit-idea or forge95.com/signin directly returns a 404 Not Found page.  This indicates server‑side routing is still misconfigured for deep links.
Poor – the SPA relies on client‑side routing; server does not fallback to index.html.
Domain inconsistency
http://forge95.com sometimes resolves to the correct SPA; https://forge95.com or www.forge95.com may behave differently.  Users could see entirely different experiences depending on the scheme and subdomain.
Inconsistent.
Back/forward navigation
The SPA scrolls to anchors but pressing the browser back button returns to previous page/section correctly; however, due to 404 errors when using direct URLs, navigation can trap the user in error pages.
Acceptable within the SPA; broken for full URLs.


Account creation & login

Observation
Issues
Sign‑in page accessible via menu
Clicking Sign In loads a welcome page with social login (GitHub/Google) and email/password fields.  The design is clean and includes remember‑me checkbox and a support link.
Sign‑up flow still fails
The sign‑up form collects first/last name, email, password and requires agreement to Terms of Service, but submitting the form returns Request failed: Failed to fetch and the account is not created.
Cannot log in
Without a working sign‑up, sign‑in cannot be tested.  Attempting to sign in with dummy credentials redirects to /dashboard but yields a 404 Not Found.
Checkbox usability
On the sign‑up form, the Terms‑of‑Service checkbox is small and tricky to click; the tick mark appears only when clicking the text – potential accessibility issue.

Idea submission flow

Step
Findings
Step 1 – Your Idea
Fields: Project Name, Project Description, Category (dropdown) and Priority Level radio buttons.  Selecting a category and clicking Next progresses smoothly to Step 2.
Step 2 – Problem & Solution
Fields for describing the problem, how the solution works, and target audience.  Validation messages and guidance text are present.  Clicking Next progresses to Step 3.
Step 3 – Business Details
Fields for key features, business model (select), timeline (select), budget range (input).  Dropdowns include options such as “Subscription (SaaS)” and timelines from 1‑2 weeks to More than 1 year.
Submission error
Clicking Submit Idea results in a red alert: “Submission Error: Request failed: Failed to fetch”.  The idea is not submitted and no further steps appear.
Support links
Each step provides buttons “View Example Ideas”, “Check Pricing”, and “View Documentation”.  These appear to be placeholders; clicking them does not open any modal or new page.


Marketplace

Feature
Findings
Marketplace page (via menu)
The page now loads and displays a grid of SaaS products with prices and status tags (Beta/Live).  Cards show rating stars, user count, key features and tech stack badges.
Demo & Get Started buttons
Each card includes View Demo and Get Started buttons, but clicking them does nothing – no modal, no navigation or message.  The CTA in the banner (“Submit Your Idea”) also fails to redirect.
Search & filters
There is a search bar, category dropdown and “Sort by Rating” control; these elements appear static – no filtering occurs when interacting with them.


Pricing & contact

Feature
Findings
Pricing cards
Plans from Free to Enterprise list features and use consistent card styling.  All CTAs lead to the same sign‑up page, which currently fails.
Contact Sales
The “Contact Sales” button uses a mailto: link that is blocked in our environment.  There is no inline contact form.
Support & chat
A green chat bubble persists across pages, but clicking it does not open a chat window (no response).  Footer links for Documentation, Community, Help Center point back to the same SPA sections (they appear unimplemented).


Overall user experience
	•	Clarity: The high‑level value proposition and process are clearly communicated.  However, missing functionalities (unresponsive CTAs, submission errors) create confusion.  Domain inconsistencies mean some users may land on a broken site.
	•	Performance: Within the SPA, scrolling and loading are smooth.  The 404 pages load quickly (because they’re static) but degrade confidence.
	•	Accuracy: Many routes and buttons do not lead to the expected outcomes (e.g., sign‑up fails, submit idea fails, marketplace buttons unresponsive).
	•	Accessibility: Font sizes and contrast are acceptable on most sections; however, checkboxes are small, and some form guidance text is light grey.  Keyboard navigation works but could be improved (e.g., focusing on form labels).  Alt text is missing from some decorative images.

⸻

Issues (with reproduction steps)

Critical
	1.	Direct routing returns 404 – server does not rewrite all routes to the SPA.
	•	Steps: Open browser and navigate directly to forge95.com/marketplace or forge95.com/signin.
	•	Result: A 404 Not Found page appears.
	•	Impact: Search engine links or bookmarks will break; deep linking is impossible.
	2.	Account creation fails – cannot create an account.
	•	Steps: Click Get Started Free, fill sign‑up form with valid data, agree to Terms.
	•	Result: A red message appears: “Request failed: Failed to fetch”.
	•	Impact: Users cannot register, blocking all gated functionality.
	3.	Idea submission fails – final submit results in error.
	•	Steps: Navigate to Submit Idea via menu (on forge95.com), complete Steps 1‑3 and click Submit Idea.
	•	Result: A red alert “Submission Error: Request failed: Failed to fetch” appears.
	•	Impact: The core promise of submitting ideas to the AI factory is unusable.
	4.	Marketplace CTAs non‑functional – product demos or purchase flows unreachable.
	•	Steps: On the Marketplace page, click View Demo or Get Started on any product card.
	•	Result: The button visually changes state but nothing else happens.
	•	Impact: Users cannot explore or purchase existing SaaS products.

Major
	1.	Domain inconsistency – www.forge95.com and forge95.com behave differently; some pages only work on one or the other.
	2.	Sign‑in redirect fails – after entering dummy credentials (or hitting Sign In), the app navigates to /dashboard but displays 404 Not Found.
	3.	Support chat not working – chat bubble does not open any widget or contact form.
	4.	Placeholder links – Buttons such as “View Example Ideas”, “Check Pricing”, “View Documentation”, and “Submit Your Idea” on the marketplace do not lead anywhere.

Minor
	•	Checkbox for terms is too small; may not be obvious for all users.
	•	Some text (e.g., form helper text) is light grey and fails contrast guidelines.
	•	No alt text on dashboard graphic and icons.
	•	Buttons change colour when clicked but provide no loading feedback or navigation, causing uncertainty.
	•	Hitting Enter in forms sometimes does nothing; explicit click is required.

⸻

Opportunities for improvement
	1.	Configure server routing to serve index.html for all unmatched routes so that direct URLs (e.g., /signin, /marketplace) load the SPA correctly.  Add 301 redirects between www and non‑www and enforce HTTPS.
	2.	Fix backend API connectivity for sign‑up and idea submission.  Ensure API endpoints accept CORS requests and return meaningful errors instead of Failed to fetch.  Provide success confirmation and guidance after submission.
	3.	Implement marketplace actions.  Each product card should open a product detail page or modal with screenshots and features.  “Get Started” should lead to a sign‑up flow pre‑populated with the selected product.  Search and filter controls should update the list.
	4.	Provide on‑page sign‑in/sign‑up fallback.  If the user lands on a 404 page via direct URL, redirect them to the home page or show a friendly message with a link back.
	5.	Enhance chat/support by integrating a chat widget or support email form; ensure the chat icon opens something.
	6.	Improve accessibility: enlarge checkboxes, increase contrast of helper text, add alt text to images.  Support keyboard navigation across form fields.
	7.	Visual and UX refinements: unify button styles, add hover effects, use consistent paddings.  Consider adding product images or icons to each marketplace card.  Show progress indicators for actions like sign‑up or submit idea.
	8.	Consolidate content across domains.  Host all content under a single domain; update DNS or SSL certificates to avoid certificate mismatch and 404 errors.

⸻

Positive highlights & progress
	•	Marketplace page available – the new marketplace shows multiple AI‑powered SaaS products with pricing and feature lists.  This is a significant step toward the marketplace vision.
	•	Multi‑step idea wizard – the idea submission flow now progresses through several steps with clear labels and helpful placeholder text; validation ensures mandatory fields are filled.
	•	Interactive FAQ – collapsible FAQ improves user experience.
	•	Consistent branding – The green colour palette, icons, and typography are coherent across pages.
	•	Improved messaging – benefit‑driven headlines and testimonials emphasize launching in days and saving development costs.

⸻

Conclusion

Forge95.com has made progress by exposing the Marketplace and Idea Submission flows through internal navigation.  The site articulates a compelling vision of AI‑driven SaaS creation and provides an attractive, modern aesthetic.  Nonetheless, severe functional gaps persist: account creation, idea submission, and product demos all fail due to backend or routing issues.  Domain inconsistencies and unresponsive buttons hinder trust and make the experience unpredictable.  Fixing these critical issues, stabilizing routes, and refining the UI/UX will be essential steps toward delivering on the promise of an accessible AI SaaS factory.

📋 Next Steps:
✅ **COMPLETED: Backend Database Connectivity Fixed**
- Database connections established and tested
- User registration and authentication working
- Idea submission and storage working
- API gateway responding correctly

**Next Priority: Test Frontend-Backend Integration**
Option 1: Test Complete User Journey (High Priority)
- Verify signup form connects to backend
- Verify login form authenticates users  
- Verify idea submission form saves data
- Test end-to-end user experience flow

Option 2: Implement Marketplace Functionality (Medium Priority)
- Add product detail modals
- Wire up "View Demo" and "Get Started" buttons
- Implement search and filtering

Option 3: Fix Sign-in Dashboard Redirect (Medium Priority)
- Create dashboard component
- Fix 404 after login
- Implement protected routes
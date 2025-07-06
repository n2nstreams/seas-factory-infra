Night 13 — Tailwind CSS + shadcn/ui Install & Landing Page  ≈ 2 h

(For clarity, this is the UI-focused Night 13 from the original week-2 checklist.  If you already installed Tailwind in an earlier step, skim to step 6 to add the landing page.)

⸻

Step-by-Step

#	Action / Command	Purpose / Result
1	cd ui	Work inside the React project.
2	Install Tailwind & friends	bash\nnpm install -D tailwindcss@latest postcss autoprefixer\nnpx tailwindcss init -p\n
3	Configure tailwind.config.js	js\n/** @type {import('tailwindcss').Config} */\nexport default {\n  content: [\n    \"./index.html\",\n    \"./src/**/*.{js,ts,jsx,tsx}\",\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n
4	Inject Tailwind directives into src/index.css	css\n@tailwind base;\n@tailwind components;\n@tailwind utilities;\n
5	Add shadcn/ui components	bash\nnpx shadcn-ui@latest init  # choose “React + Vite + TypeScript”\n# Add a few base components:\nnpx shadcn-ui@latest add button card input\n
6	Create landing page src/pages/Landing.tsx	tsx\nimport { Button, Card, CardContent } from \"@/components/ui\";\nexport default function Landing() {\n  return (\n    <div className=\"min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100\">\n      <Card className=\"w-full max-w-md text-center p-8 shadow-xl\">\n        <CardContent>\n          <h1 className=\"text-3xl font-bold mb-4\">AI SaaS Factory</h1>\n          <p className=\"text-muted-foreground mb-6\">\n            Turn any idea into a live SaaS product—no code required.\n          </p>\n          <Button asChild size=\"lg\">\n            <a href=\"/signup\">Get Started</a>\n          </Button>\n        </CardContent>\n      </Card>\n    </div>\n  );\n}\n
7	Wire up routing (if using React Router)	bash\nnpm install react-router-dom\n\nsrc/main.tsx:\ntsx\nimport { BrowserRouter, Routes, Route } from 'react-router-dom';\nimport Landing from './pages/Landing';\nimport Dashboard from './pages/Dashboard';\n\n<BrowserRouter>\n  <Routes>\n    <Route path=\"/\" element={<Landing />} />\n    <Route path=\"/dashboard\" element={<Dashboard />} />\n  </Routes>\n</BrowserRouter>\n
8	Local test	bash\nnpm run dev\n→ http://localhost:5173 shows gradient landing page with shadcn card + button.
9	Update Docker image tag (in ui/Dockerfile build step: change to 0.2 or use $GITHUB_SHA)	Keeps deployment versions unique.
10	Commit & push	bash\ngit add src tailwind.config.js postcss.config.js package.json \\\n  && git commit -m \"Night 13 – Tailwind + shadcn/ui landing page\" && git push\n
11	GitHub Actions pipeline triggers → builds new UI image → Cloud Run redeploys.	
12	Visit production URL (https://web-frontend-…-uc.a.run.app) — confirm landing page loads over HTTPS.


⸻

Night 13 Deliverables ✅
	•	Tailwind CSS configured (tailwind.config.js, directives in index.css).
	•	shadcn/ui initialized with core components (Button, Card, Input).
	•	Responsive Landing Page using Tailwind utilities & shadcn Card/Button.
	•	Client-side routing (/ → Landing, /dashboard → event stream).
	•	New UI image built & auto-deployed via existing GitHub Actions workflow; live at Cloud Run URL.

Novice visitors now see a polished landing screen that sets the tone for the SaaS Factory—and your front-end stack is fully styled and component-ready for future pages.

Night 10 — React + Vite Front-end & Auto-Deploy to Cloud Run  ≈ 3 h

Goal: Scaffold the ui/ React application, integrate Tailwind CSS + shadcn/ui, containerize it, and extend the GitHub Actions pipeline so every push to main builds and redeploys a static Cloud Run site.

⸻

Step-by-Step

#	Action / Command	Why / Result
1	From repo root: `cd ui	
2	cd ui && npm install	Install deps.
3	Add Tailwind & shadcn/ui	bash\nnpm install -D tailwindcss postcss autoprefixer\nnpx tailwindcss init -p\nnpm install @shadcn/ui\n
4	Configure Tailwind	tailwind.config.js:js\ncontent: [\"./index.html\",\"./src/**/*.{ts,tsx}\"],\nIn src/index.css add:@tailwind base; @tailwind components; @tailwind utilities;
5	Demo page	Replace App.tsx with simple hero (<Button>It works 🚀</Button>).
6	Dockerfile in /ui:	dockerfile\n# build stage\nFROM node:22-alpine AS build\nWORKDIR /app\nCOPY . .\nRUN npm ci && npm run build\n\n# run stage (static)\nFROM nginx:1.25-alpine\nCOPY --from=build /app/dist /usr/share/nginx/html\nEXPOSE 80\nCMD [\"nginx\",\"-g\",\"daemon off;\"]\n
7	Artifact Registry repo (one-time):	bash\ngcloud artifacts repositories create saas-factory-web --repository-format=docker --location=us-central1\n
8	cloud-run-ui.tf (prod env):	hcl\nresource \"google_cloud_run_v2_service\" \"frontend\" {\n  name     = \"web-frontend\"\n  location = var.region\n  ingress  = \"INGRESS_TRAFFIC_ALL\"\n  template {\n    containers [{ image = \"us-central1-docker.pkg.dev/${var.project_id}/saas-factory-web/ui:0.1\" }]\n  }\n}\noutput \"web_url\" { value = google_cloud_run_v2_service.frontend.uri }\n
9	terraform init && terraform apply -target google_cloud_run_v2_service.frontend	Creates stub service (image will be pushed shortly).
10	Update GitHub Actions deploy.yml:	Add new build-and-deploy-ui step after auth:
	```yaml\n      - name: Build UI image\n        run:	\n          cd ui\n          docker build -t us-central1-docker.pkg.dev/$GCP_PROJECT_ID/saas-factory-web/ui:$GITHUB_SHA .\n          docker push us-central1-docker.pkg.dev/$GCP_PROJECT_ID/saas-factory-web/ui:$GITHUB_SHA\n\n      - name: Deploy UI to Cloud Run\n        run:
11	Commit & push	bash\ngit add ui Dockerfile cloud-run-ui.tf .github/workflows/deploy.yml && \\\n  git commit -m \"Night 10 – React+Vite UI auto-deployed\" && git push\n
12	Watch Actions → Deploy job	Confirms image build → push → Cloud Run update; output logs show new web_url.
13	Open browser to web_url — should display Tailwind hero button.	


⸻

Night 10 Deliverables
	•	React + Vite TypeScript app under ui/ with Tailwind CSS & shadcn/ui.
	•	Dockerized build (multi-stage) producing lightweight Nginx static container.
	•	Artifact Registry repository saas-factory-web storing versioned UI images.
	•	Cloud Run service web-frontend in us-central1, publicly reachable via HTTPS.
	•	GitHub Actions pipeline automatically builds & redeploys UI on every push to main.

Frontend is now live and wired into CI/CD—next nights can focus on deeper agent logic and marketplace screens.

Night 11 — ADK “Project Orchestrator” Skeleton  ≈ 3 h

Goal: Spin up the core brain of the factory—a minimal ProjectOrchestrator built with Google’s Agent Development Kit (ADK), deploy it to Vertex AI Agent Engine, and expose a REST endpoint so everything else (GitHub Actions, future UI) can kick off full-stack builds.

⸻

Step-by-Step

#	Action / Command	Why / Result
1	From repo root: mkdir orchestrator && cd orchestrator	New top-level package for ADK agents.
2	python -m venv .venv && source .venv/bin/activate	Isolate deps.
3	pip install --upgrade pip then pip install google-ads-sdk (ADK) google-cloud-aiplatform autogen langgraph	Core libraries.
4	requirements.txt — freeze for CI: pip freeze > requirements.txt	Ensures reproducible builds.
5	project_orchestrator.py	Minimal root agent:
	python\nfrom adk import Agent, task\nfrom adk.contrib.google.gemini import GeminiPro\n\nllm = GeminiPro(model=\"models/gemini-2.5-pro-latest\")\n\nclass GreeterAgent(Agent):\n    @task\n    def greet(self, name: str) -> str:\n        return f\"Hello, {name}!\"\n\nclass ProjectOrchestrator(Agent):\n    greeter = GreeterAgent()\n\n    @task\n    def run(self, payload: dict) -> str:\n        name = payload.get(\"name\", \"world\")\n        return self.greeter.greet(name)\n\nif __name__ == \"__main__\":\n    orchestrator = ProjectOrchestrator()\n    print(orchestrator.run({\"name\": \"pong\"}))\n	Shows basic delegation; later you’ll replace GreeterAgent with real Idea/Dev agents.
6	Local test: python project_orchestrator.py → prints “Hello, pong!”	Confirms ADK runtime works locally.
7	Service account (in Terraform, infra/envs/prod/iam-run.tf):	Orchestrator needs Vertex APIs.
	hcl\nresource \"google_service_account\" \"orchestrator_sa\" {\n  account_id   = \"orchestrator-sa\"\n  display_name = \"Vertex AI Agent Engine Orchestrator\"\n}\nresource \"google_project_iam_member\" \"orchestrator_sa_vertex\" {\n  project = var.project_id\n  role    = \"roles/aiplatform.admin\"\n  member  = \"serviceAccount:${google_service_account.orchestrator_sa.email}\"\n}\n	
8	terraform apply -target=google_service_account.orchestrator_sa	Creates SA & IAM.
9	Dockerfile in orchestrator/:	Containerize agent.
	dockerfile\nFROM python:3.12-slim as base\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\"python\", \"project_orchestrator.py\"]\n	
10	Build & push image (Artifact Registry):	bash\nexport IMAGE=us-central1-docker.pkg.dev/$PROJECT_ID/saas-factory/orchestrator:0.1\n\ndocker build -t $IMAGE .\ndocker push $IMAGE\n
11	Deploy to Vertex AI Agent Engine:	bash\ngcloud beta agent-builder agents create orchestrator \\\n  --display-name=\"ProjectOrchestrator\" \\\n  --image-uri=$IMAGE \\\n  --location=us-central1 \\\n  --service-account=$(terraform output -raw orchestrator_sa_email)\n
12	Smoke call:	bash\ncurl -X POST -H \"Content-Type: application/json\" \\\n  -d '{\"name\":\"Factory\"}' \\\n  \"<AGENT_ENDPOINT_URI>\"\n
13	Output vars in Terraform (outputs.tf):	hcl\noutput \"orchestrator_endpoint\" { value = \"<AGENT_ENDPOINT_URI>\" }\n
14	GitHub Secrets ➔ add ORCH_ENDPOINT with the URI	CI / UI can call orchestrator.
15	Commit & push	bash\ngit add orchestrator requirements.txt Dockerfile infra/envs/prod/iam-run.tf outputs.tf && \\\n  git commit -m \"Night 11 – ADK ProjectOrchestrator deployed\" && git push\n


⸻

Night 11 Deliverables (bullet):
	•	orchestrator/ folder with ADK code & Dockerfile.
	•	ProjectOrchestrator root agent delegating to a GreeterAgent (proof-of-life).
	•	Container pushed to Artifact Registry (saas-factory/orchestrator:0.1).
	•	Vertex AI Agent Engine deployment running under orchestrator-sa service account.
	•	Public (or internal) REST endpoint URI exported as Terraform output & saved to GitHub secret ORCH_ENDPOINT.

You now have a callable agent brain ready to be extended with real Idea/Dev/QA delegates—next nights will start wiring those speciality agents into the orchestrator.

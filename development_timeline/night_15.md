Night 15 — Initialize ADK Project & Define ProjectOrchestrator  ≈ 2 h

Goal
Lay the foundation of the agent hierarchy: set up a proper Python package called orchestrator/, install Google’s Agent Development Kit (ADK), and implement a minimal ProjectOrchestrator root agent that successfully runs locally.
(Deployment to Vertex AI Agent Engine happens on a later night—this session focuses on code structure and a green-light local test.)

⸻

Step-by-Step

#	Action / Command	Purpose / Result
1	From repo root: mkdir orchestrator && cd orchestrator	Creates a dedicated package for orchestrator code.
2	Virtual-env (optional but clean)	bash\npython -m venv .venv\nsource .venv/bin/activate\npip install --upgrade pip\n
3	Install deps	bash\npip install agent-development-kit google-cloud-aiplatform\npip freeze > requirements.txt\n
4	Package skeleton	bash\nmkdir orchestrator  # inner package dir\ntouch orchestrator/__init__.py\n
5	Create project_orchestrator.py (inside inner orchestrator/)	python\nfrom adk import Agent, task\nfrom adk.contrib.google.gemini import GeminiPro\n\nllm = GeminiPro(model=\"models/gemini-2.5-pro-latest\")\n\nclass GreeterAgent(Agent):\n    \"\"\"Tiny helper agent for first-run smoke test.\"\"\"\n\n    @task\n    def greet(self, name: str) -> str:  # noqa: D401, ANN001\n        return f\"Hello, {name}! 👋\"\n\nclass ProjectOrchestrator(Agent):\n    \"\"\"Root agent — will later delegate to Idea, Dev, QA agents.\"\"\"\n\n    greeter: GreeterAgent  # ADK injects sub-agent instance\n\n    @task\n    def run(self, payload: dict) -> str:  # noqa: ANN001\n        name = payload.get(\"name\", \"world\")\n        # For now just call sub-agent.  Later we'll branch by payload[\"stage\"].\n        return self.greeter.greet(name)\n\nif __name__ == \"__main__\":  # quick local smoke test\n    orchestrator = ProjectOrchestrator()\n    print(orchestrator.run({\"name\": \"Factory\"}))\n
6	Run local smoke test	bash\npython orchestrator/project_orchestrator.py\n → prints Hello, Factory! 👋
7	Unit test stub tests/test_orchestrator.py	python\nfrom orchestrator.project_orchestrator import ProjectOrchestrator\n\ndef test_greets():\n    orch = ProjectOrchestrator()\n    assert \"Hello\" in orch.run({\"name\": \"Tester\"})\n
8	Add orchestrator to root pyproject.toml (if using Poetry) or update setup.cfg so any tooling knows import path.	
9	CI pipeline ( .github/workflows/ci.yml ) — ensure unit-test step includes orchestrator tests (the YAML from Night 8 already calls pytest, so nothing extra needed).	
10	Git add & commit	bash\ngit add orchestrator requirements.txt tests/test_orchestrator.py \\\n    && git commit -m \"Night 15 – ADK init & ProjectOrchestrator root agent\" && git push\n


⸻

Night 15 Deliverables ✅
	•	orchestrator/ Python package with ADK dependency frozen in requirements.txt.
	•	Minimal ProjectOrchestrator root agent containing one delegated GreeterAgent.
	•	Local run successfully prints greeting, proving ADK wiring works.
	•	Unit test (tests/test_orchestrator.py) added and passes in CI.

Your factory now has an extensible agent skeleton ready to receive specialist Idea-, TechStack-, Dev-, QA-, and Ops-agents in upcoming nights.

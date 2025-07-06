Night 8 — Local Dev Environment & CI Scaffold  ≈ 90 min

Goal: Give yourself (and future novice users) a one-command make dev-up workflow that spins up Postgres + pgvector locally, runs unit tests, and lints the code every push to GitHub.

⸻

Step-by-Step

#	Action / Command	Purpose
1	From repo root: mkdir -p dev && cd dev	Keep local-only files out of Terraform tree.
2	Create docker-compose.yml	nano docker-compose.yml:yaml\nversion: '3.9'\nservices:\n  db:\n    image: postgres:15\n    environment:\n      POSTGRES_DB: factorydb\n      POSTGRES_USER: factoryadmin\n      POSTGRES_PASSWORD: localpass\n    ports:\n      - \"5432:5432\"\n    command: [\"postgres\", \"-c\", \"shared_preload_libraries=pgvector\"]\n  adminer:\n    image: adminer\n    ports:\n      - \"8080:8080\"\n
3	Install pgvector into container	Create init.sql in same folder:sql\nCREATE EXTENSION IF NOT EXISTS vector;\nAdd to db service: volumes: ["./init.sql:/docker-entrypoint-initdb.d/init.sql:ro"]
4	Makefile helper (root of repo)	Add:make\n.PHONY: dev-up dev-down\n\ndev-up:\n\tdocker compose -f dev/docker-compose.yml up -d\n\ndev-down:\n\tdocker compose -f dev/docker-compose.yml down\n
5	make dev-up	Starts db (≈10 s).
6	Verify pgvector	bash\npsql -h localhost -U factoryadmin -d factorydb -c \"\\dx\"\n → should list vector.
7	CI linter & tests workflow	.github/workflows/ci.yml:```yaml\nname: CI\non:\n  push:\n    branches: [ main ]\n  pull_request:\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - name: Set up Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: ‘3.12’\n      - name: Install deps\n        run:
8	Pre-commit hooks (optional but nice)	pip install pre-commit && pre-commit installCreate .pre-commit-config.yaml with black, ruff, terraform_fmt.
9	Git commit & push	bash\ngit add dev docker-compose.yml Makefile .github && \\\n  git commit -m \"Night 8 – local dev docker & CI scaffold\" && git push\n


⸻

Night 8 Deliverables
	•	make dev-up spins Postgres 15 (+ pgvector) and Adminer locally.
	•	Connection string for local agents: postgresql://factoryadmin:localpass@localhost:5432/factorydb.
	•	GitHub Actions CI pipeline lints & unit-tests on every push.
	•	(Optional) Local pre-commit hooks enforce formatting before commits.

You now have a friction-free environment for experimenting, writing agents, and running tests—all without touching cloud resources or billing.

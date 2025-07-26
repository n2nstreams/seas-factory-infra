# AI SaaS Factory ‑ Masterplan

## Purpose

A step‑by‑step, **novice‑friendly** guide for building Version 1 of your fully‑automated AI SaaS Factory on **Google Cloud Platform (GCP)**. Every instruction assumes only 3 hours of focused work per night. Following this plan you will:

1. **Stand‑up core cloud infrastructure** (Cloud Run, Cloud SQL, Vertex AI Agent Engine, Cloud Monitoring).
2. **Assemble a hybrid multi‑agent orchestration layer** (Vertex AI ADK + LangGraph + AutoGen) with shared‑first, isolate‑if‑needed tenancy.
3. **Create an end‑to‑end factory pipeline** from Idea → Design → Code/QA → Deploy → Operate.
4. **Ship a client‑facing marketplace** with Stripe subscriptions and self‑service idea submission.

---

## Quick‑Start Reference

| Component              | Tech                                               | Service                           | Runtime                |
| ---------------------- | -------------------------------------------------- | --------------------------------- | ---------------------- |
| **Agent Orchestrator** | Google ADK 0.6 + AutoGen 0.3                       | Vertex AI Agent Engine            | Stateful container     |
| **Worker Agents**      | Python 3.12, LangGraph 0.1                         | Cloud Run (Rev ≥ 2025‑05‑15)      | Stateless container    |
| **LLMs**               | OpenAI GPT‑4o, Google Gemini 2.5 Pro               | Vertex AI Models API & OpenAI API | N/A                    |
| **Data Store**         | Postgres 15                                        | Cloud SQL                         | Regional (us‑central1) |
| **Vector DB**          | pgvector / Weaviate (optional)                     | Cloud Run or Cloud SQL ext        |                        |
| **Secrets**            | Secret Manager                                     | GCP                               | per‑project            |
| **Frontend**           | React 18 + Vite 5 + Tailwind CSS                   | Cloud Run (static)                |                        |
| **CI/CD**              | GitHub Actions + Cloud Build                       | GitHub → GCP                      |                        |
| **Observability**      | Cloud Logging • Cloud Monitoring • Error Reporting | GCP                               |                        |
| **Payments**           | Stripe Checkout (USD)                              | Stripe Cloud                      |                        |

> **SLA Goal** — Public: **99.9 %**.  Internal design target: **99.95 %** using multi‑region Cloud Run + Cloud SQL replicas.

---

## Repository Layout

```
saas‑factory/
├── infra/                 # Terraform & IaC modules
├── orchestrator/          # ADK Project Orchestrator agent
├── agents/                # Worker agents (idea, design, code, qa…)
│   ├── idea/
│   ├── techstack/
│   ├── design/
│   ├── dev/
│   ├── qa/
│   └── ops/
├── ui/                    # React dashboard + marketplace
├── shared/                # Reusable utils, common prompts, schemas
└── docs/                  # Generated & manual documentation
```

---

## 12‑Week Timeline (3 hrs × 7 days / wk)

> **Tip:** Each bullet ≈ 90 min block.

### Week 1 – Environment Bootstrap

* **Night 1:** Sign in to Google Cloud → create core project `saas‑factory‑prod`.  Enable APIs (Cloud Run, Cloud SQL, Vertex AI, Secret Manager).
* **Night 2:** Install CLI tools (gcloud, terraform, docker, node, python).
* **Night 3:** Fork GitHub template repo. Create **infra/** Terraform backend (state in Cloud Storage).  Commit & push.
* **Night 4:** Define baseline IAM roles (owner, devops, viewer).  Add your account as owner.
* **Night 5:** Terraform module *network‑base*: VPC, two subnets (public, private), Cloud NAT.
* **Night 6:** Cloud SQL Postgres inst ‑ single region, private IP.  Configure `pgvector` extension.
* **Night 7:** Secret Manager: store OpenAI + Stripe API keys.

### Week 2 – Local Dev & CI Scaffold

* **Night 8:** `make dev‑up`: Docker compose for local Postgres + pgvector.
* **Night 9:** Create `.github/workflows/push.yml` → lint + pytest matrix.
* **Night 10:** Configure GitHub OIDC → workload identity federation to deploy to GCP.
* **Night 11:** Cloud Build trigger: on `main` push, build & deploy container to Cloud Run `hello‑world`.
* **Night 12:** React + Vite scaffold in **ui/**.  Auto‑deploy static build to Cloud Run.
* **Night 13:** Tailwind & shadcn/ui install.  Add a landing page.
* **Night 14:** CI pipeline artifact: upload React build to Cloud Storage bucket in staging.

### Week 3 – ADK Orchestrator Skeleton

* **Night 15:** Init ADK project `orchestrator/`.  Define root agent *ProjectOrchestrator*.
* **Night 16:** Model provider config for Gemini 2.5 Pro & GPT‑4o.
* **Night 17:** Supply chain: `requirements.txt` (adk, autogen, langgraph).
* **Night 18:** Write minimal delegation flow: *ProjectOrchestrator* → *GreeterAgent* (returns “pong”).  Deploy to Vertex AI Agent Engine.
* **Night 19:** Expose orchestration endpoint `/api/orchestrate` (Cloud Run proxy → Vertex REST).
* **Night 20:** Add Agent2Agent protocol library; test message bounce with dummy LangGraph agent.
* **Night 21:** Logging hook: push orchestrator traces to Cloud Logging (structured).

### Week 4 – Worker Agent Framework

* **Night 22:** Create **agents/base.py** (abstract python class, LangGraph node wrapper).
* **Night 23:** Implement *IdeaValidationAgent* (LLM + internet search tool via SerpAPI).
* **Night 24:** Implement *MarketResearchAgent* (newsapi, social sentiment via Twitter API).
* **Night 25:** Implement *RequirementsAgent* → collects Q/A chat & outputs `requirements.yml`.
* **Night 26:** Push each agent as separate Cloud Run service with Cloud SQL connection.
* **Night 27:** Set up pub/sub topic `agent‑events` for inter‑agent notifications.
* **Night 28:** Dashboard stub: real‑time websocket to stream events.

### Week 5 – Tech Stack & Design Automation

* **Night 29:** *TechStackAgent* → fetches library scores from awesome‑lists API; outputs ranked stack options + pros/cons.
* **Night 30:** *DesignAgent* → calls Galileo AI → Figma REST to create wireframes.
* **Night 31:** Add UI endpoint to preview Figma frames in dashboard.
* **Night 32:** Tenant model (shared): add `tenant_id` column + Row Level Security in Postgres.
* **Night 33:** Isolation promo script: clone schema to dedicated DB and update routing table.
* **Night 34:** Unit tests for tenancy enforcement; QA agent writes tests automatically.
* **Night 35:** GitHub Action: on PR label `promote‑tenant` run isolation script.

### Week 6 – Code Generation & QA Loop

* **Night 36:** *DevAgent* (coder) – uses GPT‑4o function‑calling + pydantic schema for module spec.
* **Night 37:** *ReviewAgent* – runs Pytest in Cloud Build; on failure loops back to DevAgent.
* **Night 38:** Auto‑commit: DevAgent opens PR; ReviewAgent comments; orchestrator merges on green.
* **Night 39:** *UIDevAgent* – scaffolds React pages from Figma JSON via CLI `html‑to‑react`.
* **Night 40:** Playwright tests authored by QA agent.
* **Night 41:** Security scan step: Snyk CLI in pipeline; SecurityAgent parses report.
* **Night 42:** Dashboard shows codegen progress bars + PR links.

### Week 7 – DevOps & AIOps

* **Night 43:** Terraform module `app‑infra`: Cloud Run service, Cloud SQL user, Cloud Load Balancer, IAM.
* **Night 44:** LLM‑generated Terraform diff review by DevOpsAgent.
* **Night 45:** Cloud Monitoring uptime check; alert channel → Slack.
* **Night 46:** *AIOpsAgent* – stream logs, detect anomalies using Gemini on log batches.
* **Night 47:** Auto‑rollback strategy via Cloud Deploy: if error budget > 1% in 1 h.
* **Night 48:** Multi‑region rollout script (us‑central1 / us‑east1) with blue‑green.
* **Night 49:** Cost Alerts: Billing budget + Pub/Sub → CostGuardAgent sends email.

### Week 8 – Marketplace MVP

* **Night 50:** React pages: pricing, signup, dashboard.
* **Night 51:** Stripe Checkout integration (mode=subscription, USD).  Webhook → *BillingAgent*.
* **Night 52:** Self‑service idea submission form → hits `/api/orchestrate` with tenant context.
* **Night 53:** Access control hook: Verify tenant entitlement via Stripe subscription.
* **Night 54:** Admin console: approve/reject ideas, upgrade tenant to isolated.
* **Night 55:** Email templates via SendGrid: welcome, payment receipt.
* **Night 56:** End‑to‑end test: create new user → pay → submit idea → watch factory run.

### Week 9 – Personalization & Support Bots

* **Night 57:** *PersonalizationAgent* – event consumer (Pub/Sub) → shards user feature embeddings into pgvector.
* **Night 58:** Runtime feature flag system (GrowthBook) enabled via agent decisions.
* **Night 59:** Chatbot front‑end: React chat widget with serverless `/chat` endpoint (OpenAI GPT‑4o, retrieval from docs).
* **Night 60:** SupportAgent autopopulates FAQ from docs/ folder.
* **Night 61:** A/B test loop: ExperimentAgent sets variants, metrics logged to BigQuery.
* **Night 62:** Analytics dashboard panels (BigQuery charts) embedded in admin UI.
* **Night 63:** Retention email drip: MarketingAgent uses SendGrid; schedule via Cloud Scheduler.

### Week 10 – Compliance Hardening & Isolation Path

* **Night 64:** License scan agent (OSS Review Toolkit) – fail pipeline on GPL.
* **Night 65:** Privacy stub: link‑able DPA for customers; minimal GDPR checkbox.
* **Night 66:** Tenant isolation CLI: `make isolate TENANT_ID=foo` (creates dedicated DB + Cloud Run revision).
* **Night 67:** SecretsManagerAgent – rotates tokens monthly, supports AWS & Azure variants for future.
* **Night 68:** K8s path POC: deploy DevAgent to GKE Autopilot to ensure portability.
* **Night 69:** Stress test: k6 load test script via AIOpsAgent.
* **Night 70:** Failover drill: kill us‑central1 SQL instance, validate read replica takeover.

### Week 11 – Polish & Docs

* **Night 71:** `docs/CONTRIBUTING.md` – generated by DocAgent.
* **Night 72:** Architecture diagram (Mermaid) auto‑embedded in README.
* **Night 73:** Video walkthrough: DocAgent → TL;DR YouTube script + Synthesia. ✅ **COMPLETED**
* **Night 74:** Onboarding wizard on first dashboard login. ✅ **COMPLETED**
* **Night 75:** FAQ auto‑generated from code comments.
* **Night 76:** Smoke tests for marketplace signup flow in CI.
* **Night 77:** Draft marketing landing copy via CopyWriterAgent.

### Week 12 – Launch Week

* **Night 78:** Final security scan & penetration test script (OWASP ZAP).
* **Night 79:** Create status page (Cloud StatusPage.io) & incident playbook.
* **Night 80:** Switch DNS → Cloud Run custom domain ([www.launch24.com](http://www.launch24.com)). ✅ **COMPLETED**
* **Night 81:** Announce launch (Twitter, LinkedIn) via SocialAgent.
* **Night 82:** Monitor first live tenant through dashboard; validate SLA metrics.
* **Night 83:** Add feedback widget; funnel early feedback into IdeaValidationAgent.
* **Night 84:** Retrospective → backlog grooming for v1.1 (multi‑cloud, HIPAA, etc.).

---

## Detailed Architecture

```mermaid
flowchart TD
    subgraph Orchestrator Layer
        PO(Project Orchestrator) -->|Agent2Agent| IV(Idea Validation)
        PO --> TR(Tech Stack Recommender)
        PO --> DZ(Design)
        PO --> DV(Dev)
        PO --> QA
        PO --> DP(DevOps)
    end

    subgraph Worker Agents
        IV -->|market data| PG>{Postgres + pgvector}
        TR --> PG
        DZ --> Figma
        DV --> GitHub
        QA --> GitHub
        DP --> CloudRun
    end

    GitHub -->|CI/CD| CloudRun
    CloudRun --> CloudSQL
    CloudRun --> VertexAI
    Stripe --> MarketplaceUI
    MarketplaceUI --> PO
```

---

## Tenancy Strategy

1. **Shared‑first:** All tenants share one Postgres + one Cloud Run service.  Row‑level security via policy `tenant_id = current_setting('app.tenant_id')`.
2. **Isolation upgrade path:** On demand, run promotion script:

   * Clone DB to new instance `tenant‑<id>`.
   * Duplicate Cloud Run revision with env `TENANT_DB_URL`.
   * Route DNS `app‑<tenant>.your‑factory.com` via Cloud Load Balancer.

---

## Security & Secrets Guidelines

* Store all creds in Secret Manager; mount via `secrets:` block in Cloud Run.
* Each agent uses **Workload Identity Federation** with least‑privilege IAM.
* Rotate secrets on a 90‑day schedule via SecretsManagerAgent.

---

## Cost Control

* Cloud Run max instances = 10 per service (autoscaling guardrail).
* Vertex AI min replicas = 0.
* Billing alert budget: \$200/mo; notify CostGuardAgent.

---

## User Journey Overview (Novice‑First)

A brand‑new user lands on the factory’s public site, clicks **“Launch My Idea”**, and is greeted by a **mini on‑page chatbot**. The bot asks 3‑5 plain‑language questions ("What problem are you solving?", "Key features?", "Who will use it?") and summarizes their responses. From these answers the **IdeaValidationAgent** kicks off the project and the dashboard lights up—showing each stage (Idea ✔, Stack 🏗, Design 🎨, Code 💻, Deploy 🚀). In under 24 hours the user receives a live, HTTPS‑secured URL plus an email summary of next steps.

## Guided Prompt & Mini Chatbot

* **Location :** Hero section or modal after sign‑up.
* **Tech :** React component calling `/api/mini‑chat` (GPT‑4o; system prompt tuned for requirement capture).
* **Output :** Validated `requirements.yml` handed to **RequirementsAgent**.
* **Safety :** JSON schema + guardrails to block PII and disallowed content.

## Starter SaaS Templates (v1)

| Template                                                     | Description                     | Typical Add‑ons               |
| ------------------------------------------------------------ | ------------------------------- | ----------------------------- |
| **CRM Lite**                                                 | Contacts + deals pipeline       | Kanban UI, email reminders    |
| **Subscription Billing Dashboard**                           | Stripe customer portal clone    | Invoices, usage metering      |
| **Blog / CMS**                                               | Markdown posts & comments       | SEO sitemap, rich‑text editor |
| **Task Tracker**                                             | Kanban board, due dates         | Calendar sync                 |
| **Survey / Form Builder**                                    | Drag‑and‑drop forms, CSV export | Zapier webhook                |
| **Landing Page + Email Capture**                             | Static site + Mailchimp opt‑in  | A/B hero images               |
| Users can start from a template or choose **Blank Project**. |                                 |                               |

## In‑App Guidance & Docs

* **Tooltips** generated by *SupportAgent* attach to key UI controls.
* **Docs drawer** (markdown) fetched from `/docs/{step}.md` and searchable via fuzzy search.
* Guidance is context‑aware—e.g., while the Design stage is active, docs focus on reviewing Figma frames.

## Pricing Tiers (Draft)

| Tier                                                                                                    | Price / mo | Projects | Build Hours \* | DB Isolation         | Support         |
| ------------------------------------------------------------------------------------------------------- | ---------- | -------- | -------------- | -------------------- | --------------- |
| **Starter**                                                                                             | **\$29**   | 1        | 15             | Shared (row‑level)   | Community forum |
| **Pro**                                                                                                 | **\$99**   | 3        | 60             | Shared               | Email, 48 h SLA |
| **Growth**                                                                                              | **\$299**  | 5        | Unlimited      | Optional isolated DB | Slack, 24 h SLA |
| \*Build hours = cumulative agent compute minutes per billing cycle; alerts warn if a run nears the cap. |            |          |                |                      |                 |

## User Success KPIs

* **Time‑to‑first‑deploy ≤ 24 h** (target P95).
* **Idea→Live conversion rate ≥ 60 %** for Starter users.
* **Guided‑chat completion ≤ 10 min** median.
* **Support deflection ≥ 70 %** (questions answered by tooltips/docs without opening a ticket).

---

## Appendix

* **Glossary** of AI/DevOps terms.
* **Troubleshooting matrix** (common errors & fixes).
* **Future roadmap** (AWS/Azure parity, FedRAMP, mobile agents, etc.).

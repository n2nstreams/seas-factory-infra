Overview

The objective of this migration plan is to methodically transition our application stack toward a leaner, more maintainable architecture built on Next.js, shadcn/ui, and Supabase, while preserving the long-term flexibility needed for advanced AI-driven workflows. The current stack—though powerful—is overly complex for a solo builder at the MVP stage, introducing unnecessary operational overhead, cost, and risk. By adopting Supabase as the unified middleware (Auth, Database, Storage, Jobs) and Next.js with shadcn/ui for the frontend, we reduce moving parts, accelerate iteration, and simplify infrastructure without sacrificing scalability or multi-tenant security.

This plan follows a modular, strangler-fig approach: each component of the legacy system is replaced in isolation, behind feature flags and with full rollback paths, ensuring no broad or risky rewrites. The transition is structured around small, verifiable steps:
	•	Introduce new modules in parallel to existing ones (shadow or dual-run).
	•	Validate correctness and performance against predefined SLOs.
	•	Gradually shift traffic or data ownership to the new system.
	•	Decommission legacy components only after stability is proven.

The outcome is a streamlined stack that:
	•	Improves developer velocity by reducing boilerplate and infra management.
	•	Enhances reliability and observability with a smaller operational surface area.
	•	Preserves multi-tenant security via Row Level Security (RLS).
	•	Supports growth and future AI orchestration by keeping the database and auth layers Postgres-compatible and standards-aligned.

Ultimately, this migration is not a wholesale rebuild—it is an incremental evolution of the platform toward an MVP-friendly foundation, designed to get features in front of users faster while retaining a clear path to scale.

⸻

Global Governance (applies to all modules)

Feature flags & routing
	•	Flags: ui_shell_v2, auth_supabase, db_dual_write_<table>, storage_supabase, billing_v2, jobs_pg, emails_v2.
	•	Canary routing: route allowlisted users to /app2 or app2.<domain>. Keep legacy at /app.

Environments
	•	dev (personal), staging (pre-prod), prod (live).
	•	Every module lands in staging for at least 48h with telemetry parity checks.

Success SLOs
	•	p95 full-page latency: marketing ≤ 1.5s; app read ≤ 2.0s; write ≤ 2.5s.
	•	Error budget: < 1% 5xx on app routes; auth success ≥ 99.5%.
	•	Cost guardrails: monthly ceilings per environment with alerts at 50/80/100%.

Rollback
	•	Every change guarded by a flag. Rollback = disable flag + revert routing. No schema drops until 2–4 weeks after stable.

⸻

Module 1 — UI Shell Swap: Next.js + shadcn/ui (no logic change)

Objective
Replace only layout/navigation/theming while all data still calls your current backend.

Artifacts
	•	Navigation inventory: routes, required roles, data dependencies, entry points.
	•	Theming spec: tokens (colors, spacing, radii), dark mode rules, a11y contrast targets.
	•	Component adoption map: shadcn primitives to use (buttons, inputs, dialog, table, sheet, toast, tabs).

Interfaces/Contracts
	•	API boundary unchanged: same endpoints, same payloads, same auth cookie headers.
	•	Analytics map: current events → new client events (names, props, sampling).

Verification
	•	Visual parity checklist for top 10 routes.
	•	Lighthouse: LCP < 2.5s, CLS < 0.1 on /app2.
	•	A11y: keyboard navigation, focus rings, ARIA on dialogs/menus.

Rollback
	•	Flip ui_shell_v2 off. All users back to legacy shell instantly.

⸻

Module 2 — Authentication Migration: Supabase Auth (parallel → dual → cutover)

Objective
Introduce Supabase sessions without breaking legacy sessions.

Artifacts
	•	Identity mapping spec: how a legacy user_id pairs with Supabase auth.user.id.
	•	Session lifecycle doc: TTLs, refresh policy, sign-out semantics across both systems.
	•	Provider matrix: Google, GitHub, email/magic link; error taxonomies and user messages.

Interfaces/Contracts
	•	Cookies: name prefixes (sb: for Supabase). No collision with legacy cookies.
	•	Authorization: /app2 treats presence of a valid Supabase session as sufficient; legacy remains valid on /app.

Verification
	•	OAuth success ≥ 99.5% across providers.
	•	Single sign-out clears both session types within 5s.
	•	No duplicate user records during first 1k Supabase sign-ins (monitor creation vs link).

Rollback
	•	Disable auth_supabase; block /app2 gated routes or require legacy token.

⸻

Module 3 — Database On-Ramp: Supabase Postgres (shadow → dual-write → read switch)

Objective
Introduce Supabase DB table-by-table with reconciliation.

Artifacts
	•	Schema canonicalization doc: table list, PKs, FKs, unique indexes, soft-delete policy.
	•	Tenancy model doc: org_id convention; what’s tenant-scoped vs global; deny-by-default access posture.
	•	RLS policy matrix (human-readable): who can select/insert/update/delete for each table; admin override rules.
	•	ETL map: legacy → Supabase table and column mapping; nullability; default value rules.
	•	Reconciliation plan: sampling strategy, row-count parity thresholds, hash checks.

Interfaces/Contracts
	•	Dual-write controller: per-table flag (db_dual_write_<table>). Writes mirrored; reads still from legacy.
	•	Conflict resolution: source-of-truth = legacy until read switch. Idempotency keys for upserts.

Verification
	•	Drift < 0.1% for dual-written tables over 7 days.
	•	Golden queries (top 20 read patterns) return identical record counts and keys across DBs.
	•	RLS pen-tests: blocked cross-tenant reads/writes verified.

Rollback
	•	Disable per-table dual-write; keep ETL flowing; reads remain legacy.

⸻

Module 4 — File/Object Storage: Supabase Storage (new uploads → backfill → read resolver)

Objective
Migrate uploads safely without breaking existing links.

Artifacts
	•	Bucket inventory: names, ACL/policy intents, path conventions, retention rules.
	•	Object naming scheme: {org_id}/{resource}/{yyyy}/{mm}/{uuid}.{ext}.
	•	Signed URL policy: default TTLs by use case; client cache headers; CDN strategy.

Interfaces/Contracts
	•	Upload abstraction: single interface with two providers (legacy & Supabase) chosen by flag.
	•	Read resolver: try Supabase; on miss, fallback to legacy; write returned location into a link-rewrite backlog.

Verification
	•	Upload success ≥ 99.9%; average upload time ±10% of baseline.
	•	Backfill coverage ≥ 99% for hot objects (top 30d).
	•	No 404s in /app2 content scans.

Rollback
	•	Switch resolver order to legacy-first; pause backfill.

⸻

Module 5 — Jobs & Scheduling: Supabase Edge Functions / pg-boss (A/B first, C later)

Objective
Migrate background work by job family.

Artifacts
	•	Job catalog: name, trigger, inputs/outputs, max runtime, retries, idempotency key, owner.
	•	SLA grid: p95 runtime targets; failure escalation path; alert rules.
	•	Dead-letter policy: retention, inspection cadence, remediation runbook.

Interfaces/Contracts
	•	Submission API: one place where UI and services enqueue work—decides destination by flag.
	•	Status model: states (queued, in_progress, succeeded, failed, canceled), timestamps, error summaries.

Verification
	•	Short jobs (A) and cron (B) maintain p95 < 10s and < 1 min drift respectively.
	•	Duplicate suppression rate ~100% for retried A jobs.
	•	No job loss during flag flips (prove with injected canary tasks).

Rollback
	•	Point submission API back to Celery/Redis; drain in-flight cleanly.

⸻

Module 6 — Billing: Stripe Checkout + Customer Portal (shadow → enforce)

Objective
Standardize plans and entitlements without custom billing UI.

Artifacts
	•	Price catalog: Free, Pro, Business (monthly/annual), currency, trial policy, proration rules.
	•	Entitlements matrix: feature → plan mapping; usage caps per plan.
	•	Subscription state model: trialing, active, past_due, canceled; effective date semantics.
	•	Revenue events log: created, upgraded, downgraded, canceled; audit fields.

Interfaces/Contracts
	•	Webhook processing: idempotent, ordered by event time; retries handled; poison event bucket.
	•	Enforcement points: guard routes, feature toggles, rate-limiters driven by subscription state and usage.

Verification
	•	End-to-end: Checkout → success → access granted within 10s; cancel in portal → access revoked within 60s.
	•	Proration math matches Stripe dashboard totals for 3 common flows (upgrade mid-cycle, downgrade, cancel at period end).
	•	Free-tier metering halts at limit with clear UX.

Rollback
	•	Hide upgrade buttons in /app2; keep portal read-only; fall back to legacy enforcement.

⸻

Module 7 — Email/Notifications: Resend (or Supabase email) template-by-template

Objective
Migrate critical transactional mail safely.

Artifacts
	•	Template registry: name, trigger, locale, required variables, legal footer inclusion.
	•	Deliverability setup: SPF/DKIM/DMARC for your sending domain; warm-up plan; bounce/complaint handling.
	•	Unsubscribe policy: which templates are transactional vs marketing; link targets.

Interfaces/Contracts
	•	Notification router: event → template → provider; provider chosen by flag.
	•	Observability: per-template open/click/delivery/fail dashboards; correlation IDs in links.

Verification
	•	Deliverability ≥ 98%; complaint rate < 0.1%.
	•	All links resolve and carry correlation IDs; unsubscribe honored where required.

Rollback
	•	Switch provider to legacy SMTP; queue undelivered for retry.

⸻

Module 8 — Observability: Sentry + Vercel Analytics + Minimal Health Index

Objective
Keep visibility high during the swap.

Artifacts
	•	Error taxonomy: auth, network, data, permissions, payments, jobs; severities and paging rules.
	•	Health Index spec: hourly aggregates of 5xx, job failures, auth failures, webhook failures.

Interfaces/Contracts
	•	Correlation ID propagation from UI → API → job → DB (header/ctx naming standard).
	•	Dashboards: per-module boards with SLOs and current error budget.

Verification
	•	Error rates in /app2 ≤ legacy after 72h canary.
	•	On-call runbook tested with a simulated P1 (auth outage).

Rollback
	•	Disable /app2 traffic; keep telemetry for forensics.

⸻

Module 9 — AI Workloads: keep simple until jobs migrate

Objective
Constrain latency/cost until background pipeline is ready.

Artifacts
	•	Allowlist of short AI actions (≤ 20s) permitted in /app2.
	•	Cost guard: monthly cap, per-org cap, per-request token/latency thresholds.

Interfaces/Contracts
	•	Request envelope includes org_id, user_id, purpose, sensitivity tag; masked logging only.
	•	Timeout policy: if over threshold, enqueue via Module 5 and notify user.

Verification
	•	p95 ≤ 10s; aborts < 1%; no PII leakage in logs.

Rollback
	•	Route all AI calls to legacy orchestrator endpoints.

⸻

Module 10 — Hosting, Domains, DNS: Vercel + weighted canaries

Objective
Introduce /app2 safely to live traffic.

Artifacts
	•	Routing matrix: which paths live on Vercel vs legacy; cache policies for marketing pages.
	•	TLS and HSTS config; www/non-www policy.
	•	Canary plan: cohorts, duration, KPIs, rollback triggers.

Interfaces/Contracts
	•	Edge middleware rules for user allowlists and percentage-based rollout.

Verification
	•	24–48h canary at 10–20% with no KPI regressions.
	•	SEO parity for marketing routes (no duplicate canonical, no index bloat).

Rollback
	•	Send 100% back to legacy; keep Vercel warm for next attempt.

⸻

Module 11 — Security & Compliance: RLS + least-privilege + audits

Objective
Strengthen tenant isolation while reducing custom code.

Artifacts
	•	Data classification: P0 (PII/payment), P1 (user content), P2 (telemetry).
	•	Access review: who holds service keys, Stripe keys; rotation schedule; break-glass accounts.
	•	Admin action audit spec: who did what, when, on which org, with reason.

Interfaces/Contracts
	•	RLS posture: deny-by-default on tenant tables; explicit allow via membership checks.
	•	Secrets management: environment-scoped keys; prohibition of service role in client paths.

Verification
	•	Red-team tests for cross-tenant reads/writes fail as expected.
	•	Quarterly access reviews logged; key rotations verified.

Rollback
	•	Disable /app2 writes to tenant data; review RLS matrices.

⸻

Module 12 — Performance & Cost: budgets, quotas, and load tests

Objective
Prevent regressions and bill shock.

Artifacts
	•	Budgets: DB connections, function invocations, egress, email sends; alert thresholds.
	•	Load test plan: top 5 read and top 3 write flows; target concurrency; data volumes.

Interfaces/Contracts
	•	Pagination rules and default limits per list endpoint.
	•	Indexing checklist for new read paths; connection pool policy on server routes.

Verification
	•	Load tests meet SLOs at 1.5× expected peak.
	•	Monthly burn charts for Vercel/Supabase/Stripe under budget.

Rollback
	•	Reduce free-tier limits temporarily; disable heaviest features via flags.

⸻

Module 13 — Final Data Migration: source-of-truth cutover

Objective
Flip per-table reads to Supabase once proven.

Artifacts
	•	Pre-cutover checklist: freeze window, comms template, last-mile ETL, parity report.
	•	Post-cutover monitoring: reconciliation job frequency, alert thresholds, auto-repair rules.

Interfaces/Contracts
	•	Read-switch per table governed by flag; ability to revert table-by-table.

Verification
	•	24–48h after switch: zero missing keys, referential integrity clean, drift < 0.05% then trending to 0.

Rollback
	•	Re-enable legacy reads for affected tables; queue writes for replay if necessary.

⸻

Module 14 — Decommission (after 2–4 weeks stable)

Objective
Reduce complexity and cost safely.

Artifacts
	•	Decommission inventory: services, queues, buckets, terraform modules, DNS entries.
	•	Backup & retention plan: what to snapshot, how long to keep, where to store.

Interfaces/Contracts
	•	Replacement confirmation: each retired component has a named replacement & doc link.

Verification
	•	Cost delta report vs baseline; no runtime errors referencing decommissioned assets.

Rollback
	•	Keep snapshots and IaC to restore a component within 60 minutes if needed.

⸻

Suggested Execution Timeline (no code, task-level)

Week 1
	•	M1 UI shell (2 read-only screens), M8 telemetry in staging.
	•	M2 Supabase Auth in parallel (shadow sign-in), M3 DB ETL shadow for read-heavy tables.

Week 2
	•	M1 expand to 5 core screens; 10% canary to /app2.
	•	M2 dual-auth for /app2 read-only routes.
	•	M3 dual-write tiny table (preferences).
	•	M6 Stripe webhooks in shadow; M4 new uploads → Supabase in staging.

Week 3
	•	M5 migrate short jobs (A) & cron (B).
	•	M6 enable Checkout/Portal for /app2, enforce features via mirrored state.
	•	M7 move auth and invite emails.
	•	Raise canary to 20%.

Week 4
	•	M3 add 2–3 more tables to dual-write; start read-switch for first table.
	•	M4 begin read resolver with fallback.
	•	M11 RLS red-team; M12 load testing.

Weeks 5–6
	•	M5 plan long-running jobs (C) to a small worker;
	•	M3 finish read switches for core tables;
	•	M13 final migrations per domain;
	•	M14 retire unused infra.

⸻

Checklists You’ll Keep in Cursor (one per module)
	•	Runbook (entry/exit, flags, rollback, paging tree)
	•	Acceptance Tests (happy path, error path, load, adversarial)
	•	Dashboards/Alerts (links + thresholds)
	•	Decision Log (what flipped when, why, results)

⸻

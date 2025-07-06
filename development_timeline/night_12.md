Night 12 — Live Dashboard Stub & Event Pipeline  ≈ 3 h

Goal:
	1.	Push runtime “agent events” (start / finish / log) into Pub/Sub.
	2.	Stand-up a lightweight Event Relay service on Cloud Run that receives Pub/Sub pushes and stores them in Firestore.
	3.	Add a React dashboard stub that polls Firestore and streams the events to the browser (SSE-style).
This lays the plumbing for the real-time status panel novices will watch.

⸻

Step-by-Step

#	Action / Command	Why / Result
1	cd infra/envs/prod	Work in prod env.
2	event-infra.tf — create topic & Firestore DB	hcl\n# Pub/Sub topic\nresource \"google_pubsub_topic\" \"agent_events\" { name = \"agent-events\" }\n\n# Firestore Native mode (if not yet)\nresource \"google_firestore_database\" \"default\" {\n  name          = \"(default)\"\n  location_id   = \"us-central\"\n  type          = \"FIRESTORE_NATIVE\"\n}\n
3	terraform apply -target google_pubsub_topic.agent_events	Create topic (Firestore may already exist).
4	Modify project_orchestrator.py (orchestrator folder) — add publish helper	python\nfrom google.cloud import pubsub_v1, firestore\nPROJECT_ID = os.getenv(\"PROJECT_ID\")\npublisher = pubsub_v1.PublisherClient()\nTOPIC_PATH = publisher.topic_path(PROJECT_ID, \"agent-events\")\n\ndef emit(event_type: str, payload: dict):\n    data = json.dumps({\"type\": event_type, **payload}).encode(\"utf-8\")\n    publisher.publish(TOPIC_PATH, data)\n\nCall emit(\"START\", {\"stage\": \"design\"}) and emit(\"FINISH\", {...}) inside the GreeterAgent tasks (for now).
5	Re-build & push orchestrator image → bump tag 0.2 and redeploy via gcloud beta agent-builder agents update …	Orchestrator now streams events.
6	Event Relay micro-service — new folder event-relay/	app.py:
7	Dockerfile for relay	dockerfile\nFROM python:3.12-slim\nWORKDIR /app\nCOPY app.py requirements.txt ./\nRUN pip install --no-cache-dir -r requirements.txt\nCMD [\"uvicorn\",\"app:app\",\"--host\",\"0.0.0.0\",\"--port\",\"8080\"]\n
8	Push image & deploy Cloud Run event-relay (region us-central1) under the same VPC connector; note HTTPS URL.	
9	Create Pub/Sub push subscription (Terraform)	hcl\nresource \"google_pubsub_subscription\" \"relay\" {\n  name  = \"event-relay-push\"\n  topic = google_pubsub_topic.agent_events.name\n  push_config {\n    push_endpoint = google_cloud_run_v2_service.event_relay.uri\n    oidc_token { service_account_email = google_service_account.run_sa.email }\n  }\n}\n
10	terraform apply -target google_pubsub_subscription.relay	Pub/Sub now pushes events to Firestore via relay.
11	React dashboard stub (ui/src/pages/Dashboard.tsx)	tsx\nimport { useEffect, useState } from 'react'\nexport default function Dashboard() {\n  const [events, setEvents] = useState<any[]>([])\n  useEffect(() => {\n    const fetcher = async () => {\n      const res = await fetch('/api/events') // proxy to Cloud Run relay (add to vite.config)\n      setEvents(await res.json())\n    }\n    fetcher(); const id = setInterval(fetcher, 3000); return () => clearInterval(id)\n  }, [])\n  return <ul className=\"p-4 space-y-2\">{events.map((e,i)=>(<li key={i} className=\"text-sm font-mono\">{JSON.stringify(e)}</li>))}</ul>\n}\n
12	Add simple read endpoint to relay (GET /events) that returns last 100 docs from Firestore.	
13	Update UI build + docker push, then GitHub push → pipeline auto-deploys new UI.	
14	Visit /dashboard → see JSON lines streaming (“START design”, “FINISH greet”).	


⸻

Night 12 — Deliverables ✅
	•	Pub/Sub topic agent-events created.
	•	Event Relay Cloud Run service subscribed (push) to topic, writing documents into Firestore collection events.
	•	Orchestrator now publishes start/finish events.
	•	React Dashboard stub (/dashboard) polling relay endpoint every 3 s and listing event JSON.
	•	Code, Dockerfiles, Terraform updates committed & deployed.

With Night 12 complete, you have an end-to-end real-time telemetry loop—every future agent activity can appear in the UI for novices to watch, building trust and transparency.

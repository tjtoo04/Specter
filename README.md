# Specter

**Mystery Shopper** – AI-powered autonomous testing agent for mobile signup flows: uses vision to navigate, detects bugs, diagnoses root cause, and alerts teams via Slack, Microsoft Teams, Discord, email, and Jira/Linear.

---

## Repo layout

| Path | Description |
|------|-------------|
| **[ai/](ai/)** | Mystery Shopper AI agent: alert routing (Slack, Teams, Discord, email, webhooks), issue models, run/verify scripts. See **[ai/README.md](ai/README.md)** for setup, `.env`, and usage. |
| **[dashboard/](dashboard/)** | Web dashboard and backend (React + FastAPI). |

---

## Quick start – AI alerts

1. From repo root: `pip install -r ai/requirements.txt`
2. Copy `ai/.env.example` to `ai/.env` and **set every variable** (all backends required). **`ai/.env` is gitignored**; never commit it.
3. Dry run: `python -m ai.run_verify`
4. Send to all backends: `python -m ai.run_verify --send`

See **[ai/README.md](ai/README.md)** for full docs.


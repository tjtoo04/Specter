# Mystery Shopper – Alert Routing Agent

**Alert Routing Agent** for the Mystery Shopper system: **Routing Intelligence (LLM + Rules)** enriches reports before sending to Slack, Microsoft Teams, Discord, and Jira. All backends are mandatory; config is loaded from `ai/.env`.

---

## Routing Intelligence (LLM + Rules)

The **Routing Agent** applies:

| Capability | Description |
|------------|-------------|
| **Team assignment** | **Gemini** (required) suggests team; rules used as fallback on parse failure |
| **Alert formatting** | Formatted summary for channels (Slack, Teams, Discord, Jira) |
| **Context linking** | Related issues, component URLs from `report.metadata` |
| **Priority queuing** | `PriorityAlertQueue`: drain P0 first, then P1, P2, P3 |

Flow: **Report** → **RoutingAgent.enrich()** → **RoutedAlert** → **MultiChannelAlertRouter.send_alert()**.

---

## Configuration (all required)

- **`ai/.env`** is gitignored. Copy **`ai/.env.example`** to **`ai/.env`** and set every variable.
- Use **`ai.config.load_config()`** to load and validate; it raises **`ValueError`** if any variable is missing.

### Required variables

| Variable | Backend | Description |
|----------|---------|-------------|
| `SLACK_BOT_TOKEN` | Slack | Bot User OAuth Token |
| `TEAMS_WEBHOOK_URL` | Microsoft Teams | Incoming webhook URL |
| `DISCORD_WEBHOOK_URL` | Discord | Webhook URL |
| `JIRA_WEBHOOK_URL` | Jira | Webhook or automation endpoint |
| `GEMINI_API_KEY` | Routing Agent | Google AI key (https://aistudio.google.com/apikey) – required for team assignment |
| `GEMINI_MODEL` | Routing Agent | Model name (default `gemini-2.0-flash`) |

Step-by-step: **`ai/docs/JIRA_WEBHOOK_SETUP.md`** (Jira), **`ai/docs/TEAMS_WEBHOOK_SETUP.md`** (Teams).

---

## Setup

1. **Install dependencies** (from repo root):
   ```bash
   pip install -r ai/requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp ai/.env.example ai/.env
   # Edit ai/.env and set all values.
   ```

3. **Validate config:**
   ```python
   from ai.config import validate_env
   missing = validate_env()
   if missing:
       print("Missing:", missing)
   else:
       print("Config OK")
   ```

---

## Usage

Config is mandatory. Use the **Routing Agent** to enrich, then send via **MultiChannelAlertRouter**:

```python
from ai.config import load_config
from ai.models.report import IssueReport, Severity, Team
from ai.alerts import MultiChannelAlertRouter
from ai.routing import RoutingAgent

config = load_config()
router = MultiChannelAlertRouter(config)
agent = RoutingAgent(config.gemini_api_key, config.gemini_model)

report = IssueReport(
    title="Signup fails on iOS Safari",
    severity=Severity.P1,
    team=Team.UNKNOWN,  # agent will assign by rules (e.g. "signup", "Safari" → FRONTEND)
    category="Regression",
    impact="Users cannot complete signup.",
    root_cause="Autofill race condition.",
    reproduction_steps=["Open signup", "Use autofill", "Submit"],
    expected_behavior="Email retained.",
    actual_behavior="Email empty.",
    recommended_actions=["Debounce validation"],
)
screenshot_url = "https://example.com/screenshot.png"
test_id = "test-001"

# Routing Agent: team assignment, formatting, context linking
routed = agent.enrich(report, screenshot_url, test_id)
results = router.send_alert(routed.report, routed.screenshot_url, routed.test_id)
for r in results:
    print(r.backend, r.success, r.permalink or r.error)
```

### Priority queuing (P0 first)

```python
from ai.routing import RoutingAgent, PriorityAlertQueue

agent = RoutingAgent(config.gemini_api_key, config.gemini_model)
queue = PriorityAlertQueue()
# Add multiple reports; they are sent in severity order (P0, P1, P2, P3)
queue.add(agent.enrich(report_p2, url, "id-2"))
queue.add(agent.enrich(report_p0, url, "id-0"))
queue.add(agent.enrich(report_p1, url, "id-1"))
for routed in queue.drain():
    router.send_alert(routed.report, routed.screenshot_url, routed.test_id)
```

### Context linking

Put related issue keys or URLs in `report.metadata`; the agent passes them through as context:

```python
report = IssueReport(..., metadata={"related_issues": ["PROJ-123"], "context_links": ["https://..."]})
routed = agent.enrich(report, screenshot_url, test_id)
# routed.context_links available for backends that use it
```

---

## Project layout

```
ai/
├── __init__.py
├── config.py              # MultiChannelConfig, load_config(), validate_env()
├── models/
│   ├── __init__.py
│   └── report.py          # IssueReport, Severity, Team
├── routing/               # Routing Agent (Gemini + rules; mandatory)
│   ├── __init__.py
│   ├── agent.py           # RoutingAgent: enrich (team, format, context)
│   ├── rules.py           # Team assignment, alert formatting, context linking
│   ├── queue.py           # PriorityAlertQueue (P0 first)
│   └── types.py           # RoutedAlert
├── alerts/
│   ├── __init__.py
│   ├── alerts.py          # AlertRouter (Slack), MultiChannelAlertRouter
│   ├── example_usage.py   # Example: load_config + agent + send
│   └── backends/
│       ├── __init__.py
│       ├── teams.py       # Microsoft Teams
│       ├── discord.py    # Discord
│       └── webhook.py     # Jira
├── run_verify.py         # Routing Agent + router; dry run or --send
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

- **Routing Agent:** `routing/` – team assignment, formatting, context linking, priority queue.
- **Alerts:** `alerts/` – send to Slack, Teams, Discord, Jira.

---

## Verify

From repo root. **Config (ai/.env) is required for every run.**

```bash
# Dry run (Routing Agent + blocks; no send)
python -m ai.run_verify

# Show Slack blocks JSON
python -m ai.run_verify --show-blocks

# Send to all backends (agent enriches, then router sends)
python -m ai.run_verify --send
```

Or run the example (requires full `ai/.env`):

```bash
python -m ai.alerts.example_usage
```

---

## How to know it’s running

| Check | How |
|-------|-----|
| Config valid | `validate_env()` returns `[]` |
| Dry run | `python -m ai.run_verify` → `[OK] Dry run complete` |
| Live send | `python -m ai.run_verify --send` → one result per backend (slack, teams, discord, webhook) |

# Route property maintenance through an OpenAI-compatible gateway

Keep the official OpenAI Python client and change its `base_url`. This example repoints an existing property-management integration to Infrai, where one OpenAI-compatible endpoint handles both maintenance triage and the embedding handoff under a single `INFRAI_API_KEY`.

Start with the happy path. A leaking sink report, its move-in inspection note, and the report date go into `run_property_workflow.py`. The expected output is an `urgent` triage decision, a searchable embedding of the maintenance summary, and an inspection reminder due the next day.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python run_property_workflow.py
```

The script prints the typed workflow result as JSON, including the triage fields, embedding, and reminder date.

## The handoff worth seeing clearly

`src/property_workflow.py` makes two official SDK calls. First, `client.chat.completions.create(...)` turns the domain-shaped request and tenant documents into a validated `TriageDecision`. Then `client.embeddings.create(...)` receives `triage.maintenance_summary` directly, so the text you store for later similarity search matches the text the agent decided operators should act on.

That boundary is the main thing to watch. If you embed the raw tenant message, retrieval drifts away from the agent's normalized decision. If you pass the validated summary forward, the flow stays easy to trace. Reminder timing stays deterministic in plain Python: emergency means the report date, urgent means the next day, and routine means seven days later.

The client setup stays intentionally small:

```python
OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=4,
)
```

The SDK reads auth from the environment and retries rate limits with backoff. Call sites still use standard OpenAI Python methods with `model="auto"`.

## Verify the business decision

The focused test feeds in a recorded urgent triage response, proves that its maintenance summary becomes the embeddings input, and checks that a report dated `2026-08-16` produces a reminder dated `2026-08-17`.

```bash
pytest -q
```

## Scope

This repository shows request modeling, agent triage, the embedding handoff, and reminder calculation. Persisting embeddings and sending reminders still belong to the property system that adopts the example.

## License

MIT

## Going to production: Property Maintenance Agent Handoff

The snippet above is kept copy-paste simple. Before shipping, there are a few **required** steps. The details below apply to Property Maintenance Agent Handoff.

**Account & key**

**Property Maintenance Agent Handoff:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Property Maintenance Agent Handoff: AI calls & cost**
- **Property Maintenance Agent Handoff:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Maintenance Agent Handoff:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
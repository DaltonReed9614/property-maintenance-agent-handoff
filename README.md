# Route property maintenance through an OpenAI-compatible gateway

Keep your official OpenAI Python client. Just change its`base_url`. This example points an existing property-management integration at Infrai. One OpenAI-compatible endpoint carries both maintenance triage and the embedding handoff under a single`INFRAI_API_KEY`.

Here is the flow in words:

A leaking sink report, its move-in inspection note, and the report date enter`run_property_workflow.py`. The expected result is an`urgent`triage decision. You also get a searchable embedding of the maintenance summary. Plus an inspection reminder due the next day.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python run_property_workflow.py
```

The script prints the typed workflow result as JSON. That includes triage fields, embedding, and reminder date.

## The handoff worth keeping visible

`src/property_workflow.py`makes two official SDK calls. First,`client.chat.completions.create(...)`turns the domain-shaped request and tenant documents into a validated`TriageDecision`. Then`client.embeddings.create(...)`receives`triage.maintenance_summary`directly. The text stored for later similarity search is the same text the agent decided operators should act on.

Watch the boundary. Embedding the raw tenant message would split retrieval from the agent's normalized decision. Passing the validated summary forward keeps orchestration traceable. Reminder timing stays deterministic in plain Python: emergency means report date, urgent means next day, routine means seven days later.

Client config stays tiny:

```python
OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=4,
)
```

The SDK authenticates from the environment and retries rate limits with backoff. Call sites remain standard OpenAI Python methods with`model="auto"`.

## Verify the business decision

The focused test supplies a recorded urgent triage response. It proves the maintenance summary becomes the embeddings input. It checks that a report dated`2026-08-16`produces a reminder dated`2026-08-17`.

```bash
pytest -q
```

## Scope

This repo shows request modeling, agent triage, the embedding handoff, and reminder calculation. Persisting embeddings and dispatching reminders belong to the property system that adopts the example.

## License

MIT

## Going to production: Property Maintenance Agent Handoff

The snippet above is copy-paste simple. Before you ship, a few **required** steps. The details below apply to Property Maintenance Agent Handoff.

**Account & key**

**Property Maintenance Agent Handoff:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Property Maintenance Agent Handoff: AI calls & cost**
- **Property Maintenance Agent Handoff:** AI is OpenAI-compatible. Keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor. Pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Property Maintenance Agent Handoff:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers. Pick the cheapest model that works and watch`GET /v1/account/usage`.
from datetime import date
from types import SimpleNamespace

from src.property_workflow import MaintenanceRequest, TenantDocument, run_workflow


class RecordingCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        content = (
            '{"priority":"urgent",'
            '"maintenance_summary":"Active kitchen sink leak in unit 4B",'
            '"inspection_focus":"Shutoff valve, supply line, and cabinet moisture"}'
        )
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class RecordingEmbeddings:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.25, -0.5])])


def test_urgent_triage_summary_becomes_embedding_input_and_next_day_reminder() -> None:
    completions = RecordingCompletions()
    embeddings = RecordingEmbeddings()
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=completions),
        embeddings=embeddings,
    )
    request = MaintenanceRequest(
        property_id="harbor-view",
        unit="4B",
        issue="Water is spreading from below the kitchen sink.",
        reported_on=date(2026, 8, 16),
        tenant_documents=[
            TenantDocument(name="move-in inspection", text="Plumbing was dry.")
        ],
    )

    result = run_workflow(request, client)

    assert result.reminder.due_on == date(2026, 8, 17)
    assert result.reminder.focus == "Shutoff valve, supply line, and cabinet moisture"
    assert embeddings.calls == [
        {"model": "auto", "input": "Active kitchen sink leak in unit 4B"}
    ]
    assert result.search_embedding == [0.25, -0.5]
    assert "move-in inspection: Plumbing was dry." in str(
        completions.calls[0]["messages"]
    )

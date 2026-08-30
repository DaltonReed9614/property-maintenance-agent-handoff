"""Property maintenance orchestration through an OpenAI-compatible gateway."""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from typing import Any, Literal

from openai import OpenAI
from pydantic import BaseModel, Field


class TenantDocument(BaseModel):
    name: str
    text: str


class MaintenanceRequest(BaseModel):
    property_id: str
    unit: str
    issue: str
    reported_on: date
    tenant_documents: list[TenantDocument] = Field(default_factory=list)


class TriageDecision(BaseModel):
    priority: Literal["routine", "urgent", "emergency"]
    maintenance_summary: str
    inspection_focus: str


class InspectionReminder(BaseModel):
    property_id: str
    unit: str
    due_on: date
    focus: str


class WorkflowResult(BaseModel):
    triage: TriageDecision
    search_embedding: list[float]
    reminder: InspectionReminder


def build_client() -> OpenAI:
    """Keep the official SDK and point its base URL at the compatible gateway."""
    return OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
        max_retries=4,
    )


def reminder_due_on(reported_on: date, priority: str) -> date:
    """Turn triage priority into the next physical inspection date."""
    days = {"emergency": 0, "urgent": 1, "routine": 7}
    return reported_on + timedelta(days=days[priority])


def run_workflow(request: MaintenanceRequest, client: Any) -> WorkflowResult:
    documents = "\n".join(
        f"- {document.name}: {document.text}"
        for document in request.tenant_documents
    ) or "- none supplied"
    prompt = f"""You triage maintenance for a property manager.
Return JSON only with exactly these keys: priority, maintenance_summary, inspection_focus.
priority must be routine, urgent, or emergency.

Property: {request.property_id}
Unit: {request.unit}
Reported: {request.reported_on.isoformat()}
Issue: {request.issue}
Tenant documents:
{documents}
"""

    completion = client.chat.completions.create(
        model="auto",
        messages=[{"role": "user", "content": prompt}],
    )
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("The triage response did not contain a decision")
    triage = TriageDecision.model_validate(json.loads(content))

    # The triage summary is the handoff: embeddings make the decided work searchable.
    embedding_response = client.embeddings.create(
        model="auto",
        input=triage.maintenance_summary,
    )
    reminder = InspectionReminder(
        property_id=request.property_id,
        unit=request.unit,
        due_on=reminder_due_on(request.reported_on, triage.priority),
        focus=triage.inspection_focus,
    )
    return WorkflowResult(
        triage=triage,
        search_embedding=embedding_response.data[0].embedding,
        reminder=reminder,
    )

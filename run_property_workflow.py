"""Run one maintenance request through triage, indexing, and reminder planning."""

from datetime import date

from src.property_workflow import MaintenanceRequest, TenantDocument, build_client, run_workflow


def main() -> None:
    request = MaintenanceRequest(
        property_id="harbor-view",
        unit="4B",
        issue="Water is spreading from below the kitchen sink.",
        reported_on=date.today(),
        tenant_documents=[
            TenantDocument(
                name="move-in inspection",
                text="Kitchen plumbing was dry and accessible at move-in.",
            )
        ],
    )
    result = run_workflow(request, build_client())
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

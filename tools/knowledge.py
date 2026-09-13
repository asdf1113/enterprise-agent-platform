from datetime import date

from rag.retriever import KnowledgeRetriever


KNOWLEDGE_SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "name": "knowledge_search",
    "description": (
        "Search enterprise manuals, policies, FAQs, and SOPs. "
        "Use this tool for questions about enterprise knowledge. "
        "If the user explicitly asks about a historical date or period, "
        "provide an appropriate ISO date in as_of_date. "
        "Otherwise set as_of_date to null."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The enterprise knowledge question to search for."
                ),
            },
            "as_of_date": {
                "type": ["string", "null"],
                "description": (
                    "ISO date YYYY-MM-DD for historical knowledge lookup. "
                    "Use null for the currently effective knowledge."
                ),
            },
        },
        "required": [
            "query",
            "as_of_date",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}


def knowledge_search(
    retriever: KnowledgeRetriever,
    *,
    query: str,
    role: str,
    current_date: date,
    as_of_date: str | None,
) -> dict:
    effective_date = (
        date.fromisoformat(as_of_date)
        if as_of_date is not None
        else current_date
    )

    results = retriever.search(
        query,
        role=role,
        as_of_date=effective_date,
    )

    evidence = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        evidence.append(
            {
                "citation_id": f"K{index}",
                "document_id": result.document_id,
                "document_name": result.document_name,
                "version": result.version,
                "section_title": result.section_title,
                "source_path": result.source_path,
                "content": result.content,
            }
        )

    return {
        "query": query,
        "as_of_date": effective_date.isoformat(),
        "count": len(evidence),
        "results": evidence,
    }

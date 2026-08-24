from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from coherent.config import get_settings
from coherent.core.schemas.state import CoherentState, StageEnum
from coherent.core.schemas.documents import ProjectKnowledgeRegistry
from coherent.core.llm_integration.llm import get_llm, extract_text_content

async def spec_refiner_node(state: CoherentState) -> dict:
    settings = get_settings()
    llm = get_llm()

    # 1. Ingest referenced documents
    registry = ProjectKnowledgeRegistry(session_id=state["session_id"])
    for f in state.get("referenced_files", []):
        registry.add_document(f)
    docs_context = "\n\n".join(
        f"--- Reference Document: {k} ---\n{v}"
        for k, v in registry.get_all_raw_contents().items()
    )

    prompt = f"""You are the Lead Requirements Architect for Coherent.
Analyze the user intent and referenced documents to draft a complete, production-grade Markdown Specification.

Feature Intent:
{state['raw_prompt']}

Reference Documents Context:
{docs_context or 'None provided.'}
"""

    if state.get("user_feedback"):
        prompt += f"\n\nHuman Feedback to incorporate:\n{state['user_feedback']}"

    response = await llm.ainvoke([
        SystemMessage(content="You generate formal SPEC-XXX.md specifications with functional requirements, non-functional requirements, and edge cases."),
        HumanMessage(content=prompt),
    ])

    spec_content = extract_text_content(response.content)
    spec_dir = settings.storage_dir / "specs"
    spec_file = spec_dir / f"SPEC-{state['session_id']}.md"
    spec_file.write_text(spec_content, encoding="utf-8")

    return {
        "current_stage": StageEnum.REFINEMENT,
        "spec_file_path": str(spec_file),
        "stage_approved": False,
        "user_feedback": None,
        "messages": [{"role": "assistant", "stage": "refinement", "content": spec_content}],
    }
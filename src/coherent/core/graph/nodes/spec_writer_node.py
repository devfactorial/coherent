from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage
from coherent.config import get_settings
from coherent.core.llm_integration.llm import get_llm, extract_text_content
from coherent.core.schemas.state import CoherentState, StageEnum


async def spec_writer_node(state: CoherentState) -> dict:
    settings = get_settings()
    llm = get_llm()

    qna_summary = "\n".join(
        f"- **Q:** {item['question']}\n  **Answer:** {item.get('user_answer')}"
        for item in state.get("qna_history", [])
    )

    prompt = f"""You are the Lead Technical Spec Writer.
Draft the formal, production-ready SPEC Markdown artifact using the confirmed facts, resolved gaps, and Q&A findings.

Feature Intent:
{state['raw_prompt']}

Confirmed Facts:
{state.get('confirmed_facts', [])}

Validated Assumptions:
{state.get('active_assumptions', [])}

Resolved Clarification History:
{qna_summary}
"""

    response = await llm.ainvoke([
        SystemMessage(content="You generate formal SPEC-XXX.md specifications with functional requirements, non-functional requirements, and edge cases."),
        HumanMessage(content=prompt),
    ])

    spec_content = extract_text_content(response.content)
    spec_dir = settings.storage_dir / "specs"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_file = spec_dir / f"SPEC-{state['session_id']}.md"
    spec_file.write_text(spec_content, encoding="utf-8")

    return {
        "current_stage": StageEnum.REFINEMENT,
        "spec_file_path": str(spec_file),
        "stage_approved": False,
        "user_feedback": None,
        "messages": [{"role": "assistant", "stage": "refinement", "content": spec_content}],
    }
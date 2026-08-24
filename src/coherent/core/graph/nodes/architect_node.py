from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from coherent.config import get_settings
from coherent.core.schemas.state import CoherentState, StageEnum
from coherent.core.llm_integration.llm import get_llm, extract_text_content

async def architect_node(state: CoherentState) -> dict:
    settings = get_settings()
    llm = get_llm()

    spec_text = Path(state["spec_file_path"]).read_text(encoding="utf-8")

    prompt = f"""You are the Principal System Architect.
Based on the approved specification below, produce an Architecture Decision Record (MADR format) and technical design.

Specification:
{spec_text}
"""
    if state.get("user_feedback"):
        prompt += f"\n\nHuman Feedback to incorporate:\n{state['user_feedback']}"

    response = await llm.ainvoke([
        SystemMessage(content="You generate MADR-compliant Architectural Decision Records (ADR-XXX.md) with context, drivers, options, and consequences."),
        HumanMessage(content=prompt),
    ])

    adr_dir = settings.storage_dir / "adrs"
    adr_file = adr_dir / f"ADR-{state['session_id']}.md"
    adr_content = extract_text_content(response.content)
    adr_file.write_text(adr_content, encoding="utf-8")

    return {
        "current_stage": StageEnum.ARCHITECTURE,
        "adr_file_paths": [str(adr_file)],
        "stage_approved": False,
        "user_feedback": None,
        "messages": [{"role": "assistant", "stage": "architecture", "content": response.content}],
    }
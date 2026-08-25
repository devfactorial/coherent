from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage

from coherent.config import get_settings
from coherent.core.llm_integration.llm import get_llm, extract_text_content
from coherent.core.schemas.state import CoherentState, StageEnum


async def adr_writer_node(state: CoherentState) -> dict:
    settings = get_settings()
    llm = get_llm()

    spec_text = ""
    if state.get("spec_file_path") and Path(state["spec_file_path"]).exists():
        spec_text = Path(state["spec_file_path"]).read_text(encoding="utf-8")

    arch_qna_summary = "\n".join(
        f"- **Q:** {item['question']}\n  **Decision/Answer:** {item.get('user_answer')}\n  **Rationale:** {item.get('rationale', '')}"
        for item in state.get("arch_qna_history", [])
    )
    
    tech_stack = state.get("tech_stack_context") or {}
    tech_stack_summary = "\n".join(
        f"- **{k.replace('_', ' ').title()}:** {v}"
        for k, v in tech_stack.items()
    )

    prompt = f"""You are the Principal System Architect.
Draft a comprehensive MADR-compliant Architectural Decision Record (ADR-XXX.md) capturing the technical architecture, component design, and trade-offs.

Approved Requirements Specification:
{spec_text}

Target Tech Stack Baseline:
{tech_stack_summary}

Confirmed Technical Decisions:
{state.get('confirmed_tech_decisions', [])}

Resolved Technical Trade-offs:
{state.get('active_tech_tradeoffs', [])}

Technical Discovery Q&A Log:
{arch_qna_summary}

Structure the document with:
1. Title & Status (Accepted)
2. Context and Problem Statement
3. Decision Drivers (NFRs, latency, complexity, scalability)
4. Considered Technical Options & Trade-offs
5. Decision Outcome (Selected architecture, schemas, interfaces)
6. Positive & Negative Consequences
"""

    response = await llm.ainvoke(
        [
            SystemMessage(
                content="You generate formal MADR-compliant Architectural Decision Records (ADR-XXX.md)."
            ),
            HumanMessage(content=prompt),
        ]
    )

    adr_content = extract_text_content(response.content)
    adr_dir = settings.storage_dir / "adrs"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"ADR-{state['session_id']}.md"
    adr_file.write_text(adr_content, encoding="utf-8")

    return {
        "current_stage": StageEnum.ARCHITECTURE.value,
        "adr_file_paths": [str(adr_file)],
        "stage_approved": False,
        "user_feedback": None,
        "messages": [
            {
                "role": "assistant",
                "stage": "architecture",
                "content": adr_content,
            }
        ],
    }
import json
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage

from coherent.core.llm_integration import extract_text_content, get_llm
from coherent.core.schemas.state import CoherentState, StageEnum
from coherent.core.schemas.architecture import ArchDiscoveryResponse


async def arch_gap_analyzer_node(state: CoherentState) -> dict:
    llm = get_llm()

    spec_text = ""
    if state.get("spec_file_path") and Path(state["spec_file_path"]).exists():
        spec_text = Path(state["spec_file_path"]).read_text(encoding="utf-8")

    tech_stack = state.get("tech_stack_context") or {}
    tech_stack_summary = (
        "\n".join(f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in tech_stack.items())
        if tech_stack
        else "No baseline tech stack provided (greenfield defaults)."
    )

    qna_list = state.get("arch_qna_history", [])
    arch_qna_log = "\n".join(
        f"Q: {item['question']}\nRecommended: {item.get('recommended_default')}\nDecision: {item.get('user_answer', 'Pending')}"
        for item in qna_list
    )

    prompt = f"""You are the Principal System Architect conducting Technical Discovery.
Your goal is to validate non-functional requirements, data schemas, module boundaries, and trade-offs.

Approved Requirements Specification:
{spec_text}

Baseline Tech Stack & Constraints:
{tech_stack_summary}

Confirmed Technical Decisions:
{state.get('confirmed_tech_decisions', [])}

Active Technical Trade-offs:
{state.get('active_tech_tradeoffs', [])}

Previous Technical Q&A History ({len(qna_list)} questions completed):
{arch_qna_log or 'No technical questions asked yet.'}

Engineer's Latest Input:
{state.get('user_feedback') or 'Initial architectural pass.'}

### INSTRUCTIONS:
1. Examine the spec and baseline tech stack for unresolved technical trade-offs (e.g., data persistence schemas, API contracts, state management, error handling/retries, throughput/concurrency).
2. If there are critical technical decisions still unconfirmed, formulate EXACTLY ONE atomic question with a production-grade recommended default.
3. If all technical dimensions are sufficiently resolved to draft a complete ADR, set "arch_clarification_complete" to true and "next_question" to null.

Output ONLY valid JSON matching this schema:
{{
  "arch_clarification_complete": false,
  "confirmed_tech_decisions": ["Decision 1"],
  "active_tech_tradeoffs": ["Trade-off 1"],
  "next_question": {{
    "question": "Specific architectural question",
    "recommended_default": "Concrete recommended choice",
    "rationale": "Justification grounded in the tech stack"
  }}
}}
"""

    response = await llm.ainvoke(
        [
            SystemMessage(
                content="You are a strict Principal Architect. Ask atomic technical trade-off questions one at a time based on the spec and tech stack. Output valid JSON only."
            ),
            HumanMessage(content=prompt),
        ]
    )

    raw_text = extract_text_content(response.content)
    cleaned_json = raw_text.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned_json)
    
    print(f"\n[DEBUG arch_analyzer] LLM raw clarification_complete: {data.get('arch_clarification_complete')}")
    print(f"[DEBUG arch_analyzer] LLM next_question: {data.get('next_question')}")
    print(f"[DEBUG arch_analyzer] QnA history length: {len(state.get('arch_qna_history', []))}\n")

    arch_qna_history = list(state.get("arch_qna_history", []))

    # Record answered question if user provided input
    if state.get("arch_current_question") and state.get("user_feedback"):
        answered_q = state["arch_current_question"]
        answered_q["user_answer"] = state["user_feedback"]
        arch_qna_history.append(answered_q)

    next_q = data.get("next_question")
    clarification_complete = data.get("arch_clarification_complete", False) or (next_q is None)

    return {
        "current_stage": StageEnum.ARCHITECTURE.value,
        "confirmed_tech_decisions": data.get("confirmed_tech_decisions", []),
        "active_tech_tradeoffs": data.get("active_tech_tradeoffs", []),
        "arch_qna_history": arch_qna_history,
        "arch_current_question": next_q if not clarification_complete else None,
        "arch_clarification_complete": clarification_complete,
        "user_feedback": None,
        "stage_approved": False,
    }
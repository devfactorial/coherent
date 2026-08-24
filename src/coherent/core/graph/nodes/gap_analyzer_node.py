import json
from langchain_core.messages import SystemMessage, HumanMessage
from coherent.core.llm_integration.llm import get_llm, extract_text_content
from coherent.core.schemas.state import CoherentState, StageEnum
from coherent.core.schemas.documents import ProjectKnowledgeRegistry
from coherent.core.llm_integration.llm import get_llm, extract_text_content

async def gap_analyzer_node(state: CoherentState) -> dict:
    llm = get_llm()

    # Ingest project docs
    registry = ProjectKnowledgeRegistry(session_id=state["session_id"])
    for f in state.get("referenced_files", []):
        registry.add_document(f)
    docs_context = "\n\n".join(
        f"--- {k} ---\n{v}" for k, v in registry.get_all_raw_contents().items()
    )

    qna_log = "\n".join(
        f"Q: {item['question']}\nRecommended: {item.get('recommended_default')}\nUser Answer: {item.get('user_answer', 'Not answered yet')}"
        for item in state.get("qna_history", [])
    )

    prompt = f"""You are the Lead Business Analyst & Product Domain Specialist.
Your SOLE purpose is to discover business rule ambiguities, domain edge cases, and missing functional requirements.

Feature Intent:
{state['raw_prompt']}

Referenced Docs:
{docs_context or 'None provided.'}

Confirmed Functional Facts:
{state.get('confirmed_facts', [])}

Active Business Assumptions:
{state.get('active_assumptions', [])}

Previous Q&A History:
{qna_log or 'No questions asked yet.'}

Human's latest input / answer:
{state.get('user_feedback') or 'Initial run.'}

### STRICT BOUNDARIES & RULES:
1. **FUNCTIONAL DOMAIN ONLY**: Focus strictly on:
   - Business rules, tax logic, tier definitions, and threshold boundaries.
   - Domain invariants (e.g., "Can revenue be negative?", "Are taxes inclusive or exclusive?").
   - User workflows and business outcomes.
2. **ZERO TECHNICAL / IMPLEMENTATION QUESTIONS**:
   - **STRICTLY FORBIDDEN**: HTTP status codes (e.g., 400, 404, 500), REST vs GraphQL, JSON schema layouts, database columns/tables, Redis/caching, framework choices, regex patterns, or API error envelope formats.
   - All technical and wiring decisions will be handled in the **Architecture** stage, not here.
3. **ATOMIC QUESTIONS ONLY**: Ask about EXACTLY ONE single business variable, rule, or policy at a time. No compound questions joined by "and", "or", or commas.
4. **RECOMMENDED DEFAULT**: Provide a sensible, standard industry business default.
5. Set "clarification_complete" to true once the core domain logic and functional edge cases are clear.

Output ONLY valid JSON matching this schema:
{{
  "clarification_complete": false,
  "confirmed_facts": ["Revenue below threshold has 0% tax", "Threshold is 100,000"],
  "active_assumptions": ["Revenue is annual, not monthly"],
  "invalidated_items": [],
  "next_question": {{
    "question": "How should negative revenue values (e.g., refunds or net losses) be treated in the tax calculation?",
    "recommended_default": "Reject negative revenue as invalid business input and report an invalid value error",
    "rationale": "Clarifies whether refunds offset tax liability or if input represents gross sales."
  }}
}}
"""

    response = await llm.ainvoke([
        SystemMessage(content="You are a strict Product Domain Specialist. You ask ONLY functional and business logic questions. Never ask about HTTP codes, database schemas, or technical implementation details. Output valid JSON only."),
        HumanMessage(content=prompt),
    ])

    raw_text = extract_text_content(response.content)
    cleaned_json = raw_text.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned_json)

    qna_history = list(state.get("qna_history", []))

    # Record answered question if user responded
    if state.get("current_question") and state.get("user_feedback"):
        answered_q = state["current_question"]
        answered_q["user_answer"] = state["user_feedback"]
        qna_history.append(answered_q)

    next_q = data.get("next_question")

    return {
        "current_stage": StageEnum.REFINEMENT,
        "confirmed_facts": data.get("confirmed_facts", []),
        "active_assumptions": data.get("active_assumptions", []),
        "qna_history": qna_history,
        "current_question": next_q if not data.get("clarification_complete") else None,
        "clarification_complete": data.get("clarification_complete", False),
        "user_feedback": None,  # Reset feedback buffer
        "stage_approved": False,
    }
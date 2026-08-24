import json
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from coherent.config import get_settings
from coherent.core.schemas.state import CoherentState, StageEnum
from coherent.core.schemas.task import TaskDAG
from coherent.core.llm_integration.llm import get_llm, extract_text_content

async def task_planner_node(state: CoherentState) -> dict:
    settings = get_settings()
    llm = get_llm()

    spec_text = Path(state["spec_file_path"]).read_text(encoding="utf-8")
    adr_text = "\n".join(Path(p).read_text(encoding="utf-8") for p in state["adr_file_paths"])

    prompt = f"""You are the Task Decomposition Planner.
Decompose the following Spec and ADR into an atomic, topologically valid Task DAG.

Spec:
{spec_text}

ADR:
{adr_text}

Output ONLY valid JSON matching this schema:
{{
  "tasks": [
    {{
      "id": "task_01",
      "title": "Short title",
      "description": "Details",
      "scope": {{
        "primary_targets": ["path/to/file.py"],
        "dynamic_expansion_patterns": ["app/**/__init__.py"],
        "immutable_read_only": ["tests/**"]
      }},
      "dependencies": [],
      "acceptance_criteria": ["Criteria 1"],
      "verification_command": "pytest tests/test_feature.py -v"
    }}
  ]
}}
"""
    if state.get("user_feedback"):
        prompt += f"\n\nHuman Feedback to incorporate:\n{state['user_feedback']}"

    response = await llm.ainvoke([
        SystemMessage(content="You output pure JSON task lists for DAG compilation."),
        HumanMessage(content=prompt),
    ])
    raw_text = extract_text_content(response.content)
    cleaned_json = raw_text.replace("```json", "").replace("```", "").strip()
    dag_data = json.loads(cleaned_json)
    validated_dag = TaskDAG(**dag_data)

    return {
        "current_stage": StageEnum.PLANNING,
        "task_dag": [t.model_dump() for t in validated_dag.tasks],
        "current_task_index": 0,
        "stage_approved": False,
        "user_feedback": None,
        "messages": [{"role": "assistant", "stage": "planning", "content": cleaned_json}],
    }
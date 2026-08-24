# InquirerPy approval dialogs

from typing import Tuple, Optional
from InquirerPy import inquirer


async def prompt_stage_approval(stage_name: str) -> Tuple[bool, Optional[str]]:
    action = await inquirer.select(
        message=f"Action required for stage [{stage_name.upper()}]:",
        choices=[
            {"name": "✓ Approve and advance to next stage", "value": "approve"},
            {"name": "✎ Provide conversational feedback / Request edits", "value": "feedback"},
            {"name": "✖ Abort session", "value": "abort"},
        ],
        default="approve",
    ).execute_async()

    if action == "approve":
        return True, None
    elif action == "feedback":
        feedback_text = await inquirer.text(
            message="Enter feedback / changes required for this stage:"
        ).execute_async()
        return False, feedback_text
    else:
        raise KeyboardInterrupt
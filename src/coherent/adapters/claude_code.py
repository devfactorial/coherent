# Subprocess harness for Claude Code

import asyncio
from typing import Any, Dict
from .base import BaseAgentAdapter


class ClaudeCodeAdapter(BaseAgentAdapter):
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        targets = " ".join(task["scope"]["primary_targets"])
        cmd = f"claude -p 'Implement: {task['description']}. Targets: {targets}' --output-format json"
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        return {
            "exit_code": proc.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
        }
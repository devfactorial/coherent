# Subprocess harness for Aider

import asyncio
from typing import Any, Dict
from .base import BaseAgentAdapter


class AiderAdapter(BaseAgentAdapter):
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        targets = " ".join(f"--file {f}" for f in task["scope"]["primary_targets"])
        cmd = f"aider --message '{task['description']}' {targets} --yes-always --no-git"

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
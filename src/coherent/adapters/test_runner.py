# Subprocess runner for pytest/npm test

import asyncio
from typing import Dict, Any


class TestRunner:
    async def run_command(self, command: str) -> Dict[str, Any]:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() + "\n" + stderr.decode()

        return {
            "exit_code": proc.returncode,
            "output": output.strip(),
        }
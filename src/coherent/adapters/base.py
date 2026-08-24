# Base agent adapter interface

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgentAdapter(ABC):
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the task manifest headlessly and returns execution stats."""
        pass
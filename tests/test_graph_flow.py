import pytest
from coherent.core.schemas.context import ExecutionContext


def test_execution_context_thread_id():
    ctx = ExecutionContext.create(project_id="test-proj", user_prompt="Add user auth")
    assert ctx.project_id == "test-proj"
    assert "add-user-auth" in ctx.session_id
    assert ctx.thread_id.startswith("test-proj:add-user-auth")
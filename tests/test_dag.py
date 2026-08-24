from coherent.core.schemas.task import TaskDAG, TaskNode, ScopeContract


def test_task_dag_creation():
    node = TaskNode(
        id="task_01",
        title="Create Stripe Webhook Handler",
        description="Verify signatures and parse event JSON",
        scope=ScopeContract(primary_targets=["app/api/webhooks.py"]),
        verification_command="pytest tests/test_webhooks.py",
    )
    dag = TaskDAG(tasks=[node])
    assert len(dag.tasks) == 1
    assert dag.get_task("task_01").title == "Create Stripe Webhook Handler"
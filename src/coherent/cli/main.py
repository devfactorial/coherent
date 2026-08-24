# Typer CLI entrypoints (start, resume)

import asyncio
from typing import List, Optional
import typer
from rich import print
from coherent.cli.session import run_cli_session
from InquirerPy import inquirer
from pathlib import Path

app = typer.Typer(
    name="coherent",
    help="Spec-driven governance and orchestration layer for coding agents.",
)


@app.command()
def start(
    prompt: str = typer.Argument(..., help="Feature intent or task description"),
    files: List[str] = typer.Option(
        [], "--files", "-f", help="Paths to reference documents (RFCs, PRDs, specs)"
    ),
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Project name / identifier"
    ),
):
    
    """Starts a new governed coding session."""
    default_project = project or Path.cwd().name or "default-project"
    
    # Prompt interactively if not passed via CLI
    if not project:
        project_name = inquirer.text(
            message="Enter Project Name:",
            default=default_project,
        ).execute().strip()
    else:
        project_name = project.strip()

    if not prompt:
        prompt_text = inquirer.text(
            message="Enter Feature Intent / Prompt:",
        ).execute().strip()
    else:
        prompt_text = prompt
        
    asyncio.run(run_cli_session(prompt=prompt_text, files=files, project_id=project_name,))


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="Session ID to resume"),
):
    """Resumes an existing session from SQLite checkpoint."""
    #thread_id = f"{project}:{session_id}:{stage}"
    print(f"[bold green]Resuming thread:[/] {session_id}")
    # Dispatches to interactive session runner
    asyncio.run(
        run_cli_session(
            prompt="",
            files=[],
            resume_session_id=session_id,
        )
    )
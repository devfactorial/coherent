# Rich panels, tables, & streaming formatters

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def render_stage_header(stage_name: str, session_id: str, project_id: str = "") -> None:
    clean_stage = str(stage_name).strip()
    proj_tag = f"[bold white]Project:[/] [cyan]{project_id}[/] | " if project_id else ""
    console.print(
        Panel(
            f"[bold cyan]Stage:[/] [bold yellow]{clean_stage.upper()}[/] | {proj_tag}[dim]Session: {session_id}[/]",
            expand=False,
        )
    )


def render_markdown_artifact(title: str, content: str) -> None:
    console.print(Panel(Markdown(content), title=f"[bold green]{title}[/]", expand=True))
    

def render_gap_question(question: str, recommended_default: str, rationale: str = "") -> None:
    body = (
        f"[bold yellow]Question:[/] {question}\n\n"
        f"[bold]Rationale:[/] {rationale or 'Clarifying architectural constraints'}\n\n"
        f"[bold green]Recommended Default:[/] {recommended_default}"
    )
    console.print(Panel(body, title="🔍 [bold cyan]Requirements Gap Analyzer[/]", expand=False))
    
def render_arch_question(
    question: str, recommended_default: str, rationale: str = ""
) -> None:
    body = (
        f"[bold yellow]Question:[/] {question}\n\n"
        f"[bold]Rationale:[/] {rationale or 'Validating technical architectural constraints'}\n\n"
        f"[bold green]Recommended Default:[/] {recommended_default}"
    )
    console.print(
        Panel(
            body,
            title="🏗️ [bold cyan]Architecture Technical Discovery[/]",
            expand=False,
        )
    )
    
def render_tech_intake_header() -> None:
    console.print(
        Panel(
            "[bold yellow]Technical Architecture Intake[/]\n"
            "[dim]Specify your target runtime, frameworks, and database constraints before entering discovery.[/]",
            title="⚙️ [bold cyan]Architecture Baseline Setup[/]",
            expand=False,
        )
    )

def render_info(message: str) -> None:
    console.print(message)
    
def render_session_resumed(session_id: str) -> None:
    console.print(
        f"\n[bold green]Resuming active session:[/] [cyan]{session_id}[/]\n"
    )


def render_session_paused(session_id: str) -> None:
    console.print(
        f"\n[yellow]Session paused. Resume with: coherent resume {session_id}[/]\n"
    )


def render_session_completed() -> None:
    console.print(
        "\n[bold green]🎉 All tasks executed and verified successfully![/]\n"
    )


def render_warning(message: str) -> None:
    console.print(f"[yellow]{message}[/]")
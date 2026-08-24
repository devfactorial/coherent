from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"
    OLLAMA = "ollama"
    GEMINI = "gemini"


class GovernanceTier(str, Enum):
    AUTONOMOUS = "autonomous"
    STANDARD = "standard"
    STRICT = "strict"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="COHERENT_",
        extra="ignore",
    )

    # ---------------------------------------------------------------------------
    # Application & Storage Paths
    # ---------------------------------------------------------------------------
    app_name: str = "coherent"
    debug: bool = False
    base_dir: Path = Field(default_factory=lambda: Path.cwd())
    storage_dir: Path = Field(default_factory=lambda: Path.cwd() / "coherent_data")
    sqlite_db_path: Path = Field(
        default_factory=lambda: Path.cwd() / "coherent_data" / "state.db"
    )

    # ---------------------------------------------------------------------------
    # LLM Settings
    # ---------------------------------------------------------------------------
    default_provider: LLMProvider = LLMProvider.ANTHROPIC
    primary_model: str = "claude-3-7-sonnet-20250219"
    fast_model: str = "claude-3-5-haiku-20241022"
    temperature: float = 0.2

    # Provider API Keys (Supports standard unprefixed env vars via alias)
    anthropic_api_key: Optional[str] = Field(
        default=None, validation_alias="ANTHROPIC_API_KEY"
    )
    openai_api_key: Optional[str] = Field(
        default=None, validation_alias="OPENAI_API_KEY"
    )
    groq_api_key: Optional[str] = Field(
        default=None, validation_alias="GROQ_API_KEY"
    )
    google_api_key: Optional[str] = Field(
        default=None, validation_alias="GOOGLE_API_KEY"
    )
    ollama_base_url: str = "http://localhost:11434"

    # ---------------------------------------------------------------------------
    # Governance & Execution Limits
    # ---------------------------------------------------------------------------
    default_governance_tier: GovernanceTier = GovernanceTier.AUTONOMOUS
    max_self_healing_retries: int = 3
    default_agent_backend: str = "claude-code"  # "claude-code", "aider", or "direct"

    def ensure_directories(self) -> None:
        """Ensures all necessary runtime and artifact directories exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        (self.storage_dir / "specs").mkdir(parents=True, exist_ok=True)
        (self.storage_dir / "adrs").mkdir(parents=True, exist_ok=True)
        (self.storage_dir / "tasks").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Returns a cached singleton instance of Settings."""
    settings = Settings()
    settings.ensure_directories()
    return settings
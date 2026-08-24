import pytest
from pathlib import Path
from coherent.config import get_settings


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path, monkeypatch):
    monkeypatch.setenv("COHERENT_STORAGE_DIR", str(tmp_path / ".coherent"))
    monkeypatch.setenv("COHERENT_SQLITE_DB_PATH", str(tmp_path / ".coherent" / "state.db"))
    settings = get_settings()
    settings.ensure_directories()
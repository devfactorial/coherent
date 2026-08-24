from coherent.config import get_settings, GovernanceTier


def test_settings_initialization():
    settings = get_settings()
    assert settings.app_name == "coherent"
    assert settings.default_governance_tier in [
        GovernanceTier.AUTONOMOUS,
        GovernanceTier.STANDARD,
        GovernanceTier.STRICT,
    ]
    assert settings.storage_dir.exists()
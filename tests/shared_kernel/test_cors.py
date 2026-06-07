from shared_kernel.http import CorsConfig, parse_cors_origins


def test_parse_cors_origins_normalizes_and_deduplicates_values() -> None:
    origins = parse_cors_origins(
        " http://localhost:5173/ , http://localhost:3000, http://localhost:5173 "
    )

    assert origins == ("http://localhost:5173", "http://localhost:3000")


def test_cors_config_keeps_explicit_policy_values() -> None:
    config = CorsConfig(
        enabled=True,
        allow_origins=("http://localhost:5173",),
        allow_credentials=True,
    )

    assert config.enabled is True
    assert config.allow_origins == ("http://localhost:5173",)
    assert "GET" in config.allow_methods
    assert "Authorization" in config.allow_headers

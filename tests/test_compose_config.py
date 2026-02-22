from pathlib import Path


def test_xianyu_web_overrides_entrypoint_to_start_web() -> None:
    compose_text = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert 'entrypoint: ["python", "-m", "xianyu_agent.web"]' in compose_text
    assert 'xianyu-web:' in compose_text

from pathlib import Path
import re


def test_playwright_version_aligned_between_requirements_and_dockerfile() -> None:
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    req_match = re.search(r"^playwright==([0-9]+\.[0-9]+\.[0-9]+)$", requirements, re.MULTILINE)
    docker_match = re.search(
        r"mcr\.microsoft\.com/playwright/python:v([0-9]+\.[0-9]+\.[0-9]+)-jammy",
        dockerfile,
    )

    assert req_match is not None, "requirements.txt should pin playwright version"
    assert docker_match is not None, "Dockerfile should use a versioned playwright base image"
    assert req_match.group(1) == docker_match.group(1)

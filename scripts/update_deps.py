"""Update all Python dependencies via uv remove/add, preserving order in pyproject.toml."""

import re
import subprocess
import tomllib
from pathlib import Path

SERVICES = [
    "auth_service",
    "checklists_service",
    "knowledge_service",
    "notification_service",
    "escalation_service",
    "feedback_service",
    "meeting_service",
    "telegram_bot",
]


def parse_deps(pyproject_path: Path) -> tuple[list[str], list[str]]:
    """Parse direct deps and dev deps from pyproject.toml."""
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    deps = data.get("project", {}).get("dependencies", [])
    dev_deps = data.get("dependency-groups", {}).get("dev", [])
    return deps, dev_deps


def extract_pkg_name(dep: str) -> str:
    """Extract package name from dep string like 'fastapi>=0.128.0'."""
    m = re.match(r"^([a-zA-Z0-9_.-]+(?:\[[^\]]+\])?)", dep)
    assert m, f"Invalid dep string: {dep}"
    return m.group(1)


def update_service(service_dir: Path) -> int:
    pyproject = service_dir / "pyproject.toml"
    if not pyproject.exists():
        return 0

    deps, dev_deps = parse_deps(pyproject)

    # Remove in reverse order
    for dep in reversed(dev_deps):
        pkg = extract_pkg_name(dep)
        subprocess.run(["uv", "remove", pkg, "--directory", str(service_dir)], capture_output=True, text=True)
    for dep in reversed(deps):
        pkg = extract_pkg_name(dep)
        subprocess.run(["uv", "remove", pkg, "--directory", str(service_dir)], capture_output=True, text=True)

    # Add back in original order
    for dep in deps:
        pkg = extract_pkg_name(dep)
        subprocess.run(["uv", "add", pkg, "--directory", str(service_dir)], capture_output=True, text=True)
    for dep in dev_deps:
        pkg = extract_pkg_name(dep)
        subprocess.run(["uv", "add", pkg, "--directory", str(service_dir), "--dev"], capture_output=True, text=True)

    return len(deps) + len(dev_deps)


def main() -> None:
    total = 0

    for service in SERVICES:
        service_dir = Path(service)
        if not service_dir.is_dir():
            continue

        total += update_service(service_dir)



if __name__ == "__main__":
    main()

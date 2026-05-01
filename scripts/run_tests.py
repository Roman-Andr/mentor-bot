#!/usr/bin/env python3
"""Run tests across all Python services asynchronously."""

import asyncio
import os
import sys
from pathlib import Path

SERVICES = [
    "auth_service",
    "checklists_service",
    "escalation_service",
    "feedback_service",
    "knowledge_service",
    "meeting_service",
    "notification_service",
    "telegram_bot",
]


def check_uv_available():
    """Check if uv is available."""
    import shutil

    return shutil.which("uv") is not None


async def run_service_tests(service: str, results: dict) -> None:
    """Run tests for a single service."""
    service_path = Path(service)
    test_path = service_path / "tests"

    if not test_path.exists():
        results[service] = ("SKIPPED", "no tests", 0)
        return

    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    proc = await asyncio.create_subprocess_exec(
        "uv",
        "run",
        "pytest",
        "-q",
        cwd=service,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    stdout, stderr = await proc.communicate()
    output = (stdout.decode() + stderr.decode()).strip()

    if proc.returncode == 0:
        results[service] = ("PASSED", output, 0)
    elif proc.returncode == 5:  # No tests collected
        results[service] = ("SKIPPED", "no tests collected", 0)
    else:
        results[service] = ("FAILED", output, proc.returncode)


async def main() -> int:
    """Run all tests asynchronously."""
    if not check_uv_available():
        print("Error: 'uv' command not found. Please install uv.")
        return 1

    print("Running tests asynchronously across all services...\n")

    results = {}
    tasks = [run_service_tests(svc, results) for svc in SERVICES]
    await asyncio.gather(*tasks)

    # Print results
    failed = []
    passed = 0
    skipped = 0

    for service in SERVICES:
        status, output, _code = results.get(service, ("UNKNOWN", "", 1))

        if status == "PASSED":
            print(f"✅ {service}: PASSED")
            passed += 1
        elif status == "SKIPPED":
            print(f"⏭️  {service}: SKIPPED ({output})")
            skipped += 1
        else:
            print(f"❌ {service}: FAILED")
            failed.append((service, output))

    print()

    # Show failed details
    if failed:
        print("=" * 60)
        print("FAILED SERVICES:")
        print("=" * 60)
        for service, output in failed:
            print(f"\n--- {service} ---")
            print(output)
        print()

    # Summary
    total = len(SERVICES)
    print(f"Results: {passed} passed, {len(failed)} failed, {skipped} skipped ({total} total)")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

#!/usr/bin/env python3
"""Generate .env file with interactive input for required secrets and auto-generation for others"""

import secrets
import string
import sys
from pathlib import Path


def generate_secret(length: int = 32) -> str:
    """Generate a URL-safe random secret of specified length"""
    return secrets.token_urlsafe(length)


def generate_password(length: int = 24) -> str:
    """Generate a secure password with mixed characters (letters only)"""
    alphabet = string.ascii_letters
    return "".join(secrets.choice(alphabet) for _ in range(length))


def get_user_input(prompt: str, default: str = "", *, required: bool = True) -> str:
    """Get user input with optional default and required validation"""
    prompt = f"{prompt} [{default}]: " if default else f"{prompt}: "

    while True:
        value = input(prompt).strip()
        if not value:
            if default:
                return default
            if required:
                print("This field is required. Please enter a value.")  # noqa: T201
                continue
            return ""
        return value


def main() -> None:
    """Generate .env file with interactive input for required secrets and auto-generation for others."""
    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_example.exists():
        print("Error: .env.example not found")  # noqa: T201
        sys.exit(1)

    print("=" * 70)  # noqa: T201
    print("ENVIRONMENT FILE GENERATOR")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print()  # noqa: T201

    # Ask for domain first
    domain = get_user_input("Domain (e.g., example.com)")
    server_ip = get_user_input("Server IP address (e.g., 1.2.3.4)")
    print()  # noqa: T201

    # Variables to generate secrets for (key: generator function)
    auto_vars = {
        "POSTGRES_PASSWORD": lambda: generate_password(24),
        "TELEGRAM_API_KEY": lambda: generate_secret(32),
        "SERVICE_API_KEY": lambda: generate_secret(32),
        "SECRET_KEY": lambda: generate_secret(32),
        "JWT_SECRET_KEY": lambda: generate_secret(32),
        "PGADMIN_DEFAULT_PASSWORD": lambda: generate_password(20),
        "S3_SECRET_KEY": lambda: generate_secret(32),
        "MINIO_ROOT_PASSWORD": lambda: generate_password(24),
        "ADMIN_PASSWORD": lambda: generate_password(24),
    }

    # Generate all auto secrets
    auto_values = {}
    for key, generator in auto_vars.items():
        auto_values[key] = generator()

    # Variables that require user input (key: prompt description)
    user_input_vars = {
        "GOOGLE_CLIENT_ID": "Google Client ID (for OAuth)",
        "GOOGLE_CLIENT_SECRET": "Google Client Secret (for OAuth)",
        "SMTP_HOST": "SMTP Host (e.g., smtp.gmail.com)",
        "SMTP_USER": "SMTP Username (email address)",
        "SMTP_PASSWORD": "SMTP Password (app password)",
        "DOCKER_USERNAME": "Docker Hub Username (for deployment)",
    }

    # Collect user input
    print("Please provide the following required values:")  # noqa: T201
    print("-" * 70)  # noqa: T201
    user_values = {}

    # Telegram configuration
    user_values["TELEGRAM_BOT_TOKEN"] = get_user_input(
        "Telegram Bot Token (get from BotFather: https://t.me/botfather)"
    )
    user_values["TELEGRAM_BOT_USERNAME"] = get_user_input("Telegram Bot Username (without @)")
    use_proxy = get_user_input("Use Telegram Proxy? (yes/no)", "no", required=False).lower()
    telegram_proxy = ""
    if use_proxy in ("yes", "y"):
        telegram_proxy = get_user_input(
            "Telegram Proxy URL (for host machine proxy use host.docker.internal)",
            "socks5://host.docker.internal:1080",
        )
    print()  # noqa: T201

    # Other required values
    for key, description in user_input_vars.items():
        user_values[key] = get_user_input(f"{description}")
    print()  # noqa: T201

    # Read .env.example
    content = env_example.read_text()
    lines = content.split("\n")

    output_lines = []
    for line in lines:
        # Special handling for TELEGRAM_PROXY comment
        if "# TELEGRAM_PROXY=" in line:
            if telegram_proxy:
                output_lines.append(f"TELEGRAM_PROXY={telegram_proxy}")
            else:
                output_lines.append(line)
            continue

        # Skip comments and empty lines
        if line.strip().startswith("#") or not line.strip():
            output_lines.append(line)
            continue

        # Parse variable
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Use user input if applicable
            if key in user_values:
                output_lines.append(f"{key}={user_values[key]}")
            # Use auto-generated secret if applicable
            elif key in auto_values:
                output_lines.append(f"{key}={auto_values[key]}")
            # Replace domain-based values
            elif key == "GOOGLE_REDIRECT_URI":
                output_lines.append(f"{key}=https://{domain}/auth/google/callback")
            elif key == "DEFAULT_FROM_EMAIL":
                output_lines.append(f"{key}=noreply@{domain}")
            elif key in ("PGADMIN_DEFAULT_EMAIL", "ADMIN_EMAIL"):
                output_lines.append(f"{key}=admin@{domain}")
            elif key == "CORS_ORIGINS":
                output_lines.append(f'{key}=["https://{domain}"]')
            elif key == "ALLOWED_HOSTS":
                output_lines.append(f'{key}=["{server_ip}", "{domain}", "www.{domain}", "localhost"]')
            else:
                # Keep as-is
                output_lines.append(line)
        else:
            output_lines.append(line)

    # Write to .env
    output_content = "\n".join(output_lines)
    env_file.write_text(output_content)

    print("=" * 70)  # noqa: T201
    print("✓ .env file generated successfully!")  # noqa: T201
    print("=" * 70)  # noqa: T201
    print()  # noqa: T201
    print("The following secrets were auto-generated:")  # noqa: T201
    for var, value in sorted(auto_values.items()):
        print(f"  - {var}: {value}")  # noqa: T201
    print()  # noqa: T201
    print("You provided values for:")  # noqa: T201
    for var, value in sorted(user_values.items()):
        print(f"  - {var}: {value}")  # noqa: T201
    print(f"  - Domain: {domain}")  # noqa: T201
    print(f"  - Server IP: {server_ip}")  # noqa: T201
    if telegram_proxy:
        print(f"  - TELEGRAM_PROXY: {telegram_proxy}")  # noqa: T201
    print()  # noqa: T201


if __name__ == "__main__":
    main()

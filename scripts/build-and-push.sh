#!/usr/bin/env bash
# Build and push all mentor-bot service images to a Docker registry.
#
# Usage:
#   DOCKER_USERNAME=youruser ./scripts/build-and-push.sh [tag]
#
# Defaults:
#   tag          = current git short SHA (falls back to "latest")
#   REGISTRY     = docker.io
#   PLATFORM     = linux/amd64   (target VPS arch)
#   PUSH_LATEST  = 1             (also tag & push :latest)
#
# Requirements: docker buildx, logged in to the registry (`docker login`).

set -euo pipefail

REGISTRY="${REGISTRY:-docker.io}"
PLATFORM="${PLATFORM:-linux/amd64}"
PUSH_LATEST="${PUSH_LATEST:-1}"
IMAGE_PREFIX="${IMAGE_PREFIX:-mentor-bot}"

if [[ -z "${DOCKER_USERNAME:-}" ]]; then
  echo "ERROR: DOCKER_USERNAME is not set" >&2
  exit 1
fi

TAG="${1:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_SERVICES=(
  auth_service
  checklists_service
  knowledge_service
  notification_service
  escalation_service
  feedback_service
  meeting_service
  telegram_bot
)

BUILDER_NAME="mentor-bot-builder"
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
  docker buildx create --name "$BUILDER_NAME" --use >/dev/null
else
  docker buildx use "$BUILDER_NAME"
fi

image_ref() {
  local svc="$1" tag="$2"
  echo "${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_PREFIX}-${svc}:${tag}"
}

build_and_push() {
  local name="$1"; shift
  local context="$1"; shift
  local dockerfile="$1"; shift
  # remaining args: extra build flags (e.g. --build-arg, --target)

  local tags=(-t "$(image_ref "$name" "$TAG")")
  if [[ "$PUSH_LATEST" == "1" ]]; then
    tags+=(-t "$(image_ref "$name" "latest")")
  fi

  echo ">>> Building $name ($(image_ref "$name" "$TAG"))"
  docker buildx build \
    --platform "$PLATFORM" \
    --file "$dockerfile" \
    "${tags[@]}" \
    "$@" \
    --push \
    "$context"
}

for svc in "${PYTHON_SERVICES[@]}"; do
  build_and_push "$svc" "." "Dockerfile" --target prod --build-arg "SERVICE_NAME=$svc"
done

build_and_push "admin_web" "./admin_web" "./admin_web/Dockerfile" --target runner

echo
echo "Done. Tag: $TAG"
echo "Deploy on VPS with:"
echo "  IMAGE_TAG=$TAG docker compose -f docker-compose.prod.yml pull"
echo "  IMAGE_TAG=$TAG docker compose -f docker-compose.prod.yml up -d"

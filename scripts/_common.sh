#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${REPO_ROOT}/backend"
FRONTEND_DIR="${REPO_ROOT}/frontend"

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

BACKEND_PID=""
FRONTEND_PID=""

log() {
  printf '[startup] %s\n' "$*"
}

require_command() {
  local command_name="$1"
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "${command_name}" >&2
    exit 1
  fi
}

port_is_listening() {
  python3 - "$1" "$2" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.5)
    sys.exit(0 if sock.connect_ex((host, port)) == 0 else 1)
PY
}

ensure_port_available() {
  local host="$1"
  local port="$2"
  local service_name="$3"

  if port_is_listening "${host}" "${port}"; then
    printf '%s port %s is already in use on %s\n' "${service_name}" "${port}" "${host}" >&2
    exit 1
  fi
}

check_environment() {
  require_command bash
  require_command python3
  require_command uv
  require_command npm
  ensure_port_available "${BACKEND_HOST}" "${BACKEND_PORT}" "Backend"
  ensure_port_available "${FRONTEND_HOST}" "${FRONTEND_PORT}" "Frontend"
}

install_backend_dependencies() {
  log "Installing backend dependencies"
  (
    cd "${BACKEND_DIR}"
    uv sync
  )
}

install_frontend_dependencies() {
  log "Installing frontend dependencies"
  (
    cd "${FRONTEND_DIR}"
    rm -rf node_modules
    npm install
  )
}

reset_backend_database() {
  log "Resetting backend database files"
  rm -f \
    "${BACKEND_DIR}/sql_app.db" \
    "${BACKEND_DIR}/sql_app.db-shm" \
    "${BACKEND_DIR}/sql_app.db-wal"
}

run_backend_migrations() {
  log "Running database migrations"
  (
    cd "${BACKEND_DIR}"
    uv run alembic upgrade head
  )
}

seed_backend_data() {
  log "Seeding Shanghai demo data"
  (
    cd "${BACKEND_DIR}"
    uv run python seed_shanghai_data.py
  )
}

start_backend() {
  log "Starting backend on http://${BACKEND_HOST}:${BACKEND_PORT}"
  (
    cd "${BACKEND_DIR}"
    exec uv run uvicorn app.main:app \
      --host "${BACKEND_HOST}" \
      --port "${BACKEND_PORT}" \
      --reload \
      --reload-dir app
  ) &
  BACKEND_PID=$!
}

start_frontend() {
  log "Starting frontend on http://${FRONTEND_HOST}:${FRONTEND_PORT}"
  (
    cd "${FRONTEND_DIR}"
    exec npm run dev -- \
      --host "${FRONTEND_HOST}" \
      --port "${FRONTEND_PORT}" \
      --strictPort
  ) &
  FRONTEND_PID=$!
}

print_access_info() {
  cat <<EOF

Backend:  http://${BACKEND_HOST}:${BACKEND_PORT}
Frontend: http://${FRONTEND_HOST}:${FRONTEND_PORT}

Press Ctrl+C to stop both services.
EOF
}

cleanup() {
  local exit_code=$?

  trap - EXIT INT TERM

  for pid in "${FRONTEND_PID:-}" "${BACKEND_PID:-}"; do
    if [ -n "${pid}" ] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
    fi
  done

  wait "${FRONTEND_PID:-}" 2>/dev/null || true
  wait "${BACKEND_PID:-}" 2>/dev/null || true

  exit "${exit_code}"
}

wait_for_stack() {
  print_access_info
  wait -n "${BACKEND_PID}" "${FRONTEND_PID}"
}

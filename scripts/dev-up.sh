#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

trap cleanup EXIT INT TERM

check_environment
reset_backend_database
run_backend_migrations
seed_backend_data
start_backend
start_frontend
wait_for_stack

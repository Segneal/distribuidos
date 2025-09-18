#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROTO_DIR="${ROOT_DIR}/proto"
USER_OUT="${ROOT_DIR}/services/user-service/src"
INVENTORY_OUT="${ROOT_DIR}/services/inventory-service/src"
EVENTS_OUT="${ROOT_DIR}/services/events-service/src"

mkdir -p "${USER_OUT}" "${INVENTORY_OUT}" "${EVENTS_OUT}"

echo "Generating gRPC stubs..."

python -m grpc_tools.protoc -I"${PROTO_DIR}" \
  --python_out="${USER_OUT}" \
  --grpc_python_out="${USER_OUT}" \
  "${PROTO_DIR}/user.proto"

python -m grpc_tools.protoc -I"${PROTO_DIR}" \
  --python_out="${INVENTORY_OUT}" \
  --grpc_python_out="${INVENTORY_OUT}" \
  "${PROTO_DIR}/inventory.proto"

python -m grpc_tools.protoc -I"${PROTO_DIR}" \
  --python_out="${EVENTS_OUT}" \
  --grpc_python_out="${EVENTS_OUT}" \
  "${PROTO_DIR}/events.proto"

echo "gRPC Python stubs generated successfully."

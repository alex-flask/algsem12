#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CXX="${CXX:-c++}"
TEST_BIN="$(mktemp "${TMPDIR:-/tmp}/team1_23_tree.XXXXXX")"
trap 'rm -f "$TEST_BIN"' EXIT

echo "=== Команда 1: проверка 2-3 дерева ==="
echo "Компилятор: $CXX"
"$CXX" -std=c++17 -O2 -Wall -Wextra -pedantic \
  "$SCRIPT_DIR/team1_23_tree.cpp" -o "$TEST_BIN"

echo
echo "=== Самопроверка ==="
"$TEST_BIN" --self-test

echo
echo "=== Результаты тестовых наборов (CSV) ==="
"$TEST_BIN" --csv
echo "=== Конец вывода ==="

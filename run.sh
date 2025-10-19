#!/usr/bin/env bash
set -e
source .venv/bin/activate || true
OMP_NUM_THREADS=1 python3 -m python.collect_all
cd go && go run main.go


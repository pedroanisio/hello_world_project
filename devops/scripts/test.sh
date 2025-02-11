#!/usr/bin/env bash
# test.sh: Run the test suite with coverage reporting.

pip install pytest-cov httpx
pytest --cov=src --cov-report=term-missing

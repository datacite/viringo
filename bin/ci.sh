#!/usr/bin/env bash
echo "Installing Test Dependencies"
pipenv sync --dev

echo "Running Tests"
pipenv run pytest


#!/bin/bash
# Development only: when FLASK_DEBUG is set (e.g. `FLASK_DEBUG=1 docker compose up`),
# install the dev dependencies and have Passenger restart the app on every
# request, so edits in the bind-mounted source tree are picked up.
RESTART_FILE=/home/app/webapp/tmp/always_restart.txt

case "${FLASK_DEBUG,,}" in
  "" | 0 | false | no)
    # Don't keep restarting because of a file left behind by an earlier dev run.
    rm -f "$RESTART_FILE"
    exit 0
    ;;
esac

mkdir -p "$(dirname "$RESTART_FILE")"
touch "$RESTART_FILE"
pipenv sync --dev

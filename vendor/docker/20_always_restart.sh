#!/bin/bash
if [ "$FLASK_ENV" == "development" ]; then
  mkdir -p /home/app/webapp/viringo/tmp
  touch /home/app/webapp/viringo/tmp/always_restart.txt
  pipenv install --dev
fi

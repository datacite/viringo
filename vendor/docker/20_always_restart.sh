#!/bin/sh
if [ "$FLASK_ENV" == "development" ]; then
  mkdir -p tmp;
  touch tmp/always_restart.txt;
fi

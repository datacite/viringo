#!/bin/sh
cd /home/app/vendor/middleman
bundle exec middleman build -e ${FLASK_ENV}

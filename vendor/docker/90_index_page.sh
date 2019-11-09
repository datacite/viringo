#!/bin/sh
cd /home/app/vendor/middleman
ls -l
bundle exec middleman build -e ${FLASK_ENV}

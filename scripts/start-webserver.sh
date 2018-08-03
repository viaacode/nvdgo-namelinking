#!/bin/bash
cd `dirname "$0"`
cd ../pywebserver/

echo Starting Gunicorn.
gunicorn pywebserver.wsgi:application --bind 0.0.0.0:8000 --workers 3


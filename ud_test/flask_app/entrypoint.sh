#!/usr/bin/env bash
echo "Start script" >&2
flask db upgrade
python app.py



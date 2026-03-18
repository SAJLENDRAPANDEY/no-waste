#!/bin/bash
pip install -r requirements.txt
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

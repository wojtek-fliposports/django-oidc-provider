#!/bin/bash
python3 manage.py migrate
printf "from django.contrib.auth.models import User \nif not User.objects.filter(email='admin@example.com').exists():\n    User.objects.create_superuser('admin', 'admin@example.com', 'nimda')\n" | python manage.py shell
python3 manage.py runserver 0.0.0.0:8000


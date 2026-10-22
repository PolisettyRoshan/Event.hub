@echo off
python -m venv venv
call venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
pause

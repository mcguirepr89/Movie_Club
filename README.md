1. Clone repo
1. Enter repo directory `cd Movie_Club`
1. Setup `venv`: `python3 -m venv venv`
1. Activate venv: `source ./venv/bin/activate`
1. Install Django: `pip install -U pip && pip install Django`
1. Make migrations `python manage makemigrations`
1. Migrate `python manage migrate`
1. Create Super User `python manage createsuperuser`
1. Load fixtures:
   ```
   python manage.py loaddata people
   python manage.py loaddata categories 
   python manage.py loaddata streaming_services
   python manage.py loaddata people
   ```
1. Compile TailwindCSS `tailwind -i static/css/input -o static/css/tailwind.css`

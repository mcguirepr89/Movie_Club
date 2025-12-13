1. Clone repo
1. Enter repo directory `cd Movie_Club`
1. Setup `venv`: `python3 -m venv venv`
1. Install Django: `pip install -U pip && pip install Django`
1. Create Super User `python manage createsuperuser`
1. Make migrations `python manage makemigrations`
1. Migrate `python manage migrate`
1. Load fixtures:
   ```
   python manage loaddata people
   python manage loaddata categories 
   python manage loaddata streaming_services
   python manage loaddata people
   ```
1. Compile TailwindCSS `tailwind -i static/css/input -o static/css/tailwind.css`

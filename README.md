1. Clone repo
1. Enter repo directory `cd Movie_Club`
1. Setup `venv`: `python3 -m venv venv`
1. Activate venv: `source ./venv/bin/activate`
1. Install requirements: `pip install -U pip && pip install -r requirements.txt`
1. Rename the DEVELOPMENT ONLY `settings.py`: `mv movie_club/settings.py.fordevelopmentonly movie_club/settings.py`
1. Make migrations `python manage.py makemigrations`
1. Migrate `python manage.py migrate`
1. Load fixtures:
   ```
   python manage.py loaddata people
   python manage.py loaddata categories 
   python manage.py loaddata streaming_services
   python manage.py loaddata patrick_movies
   python manage.py loaddata alyssa_movies
   ```
1. Run the development server: `python manage.py runserver`

Create a superuser if you want to access the admin panel:
```
python manage.py createsuperuser
```

If you make any changes to the CSS styling, remember to recompile TailwindCSS:
1. First install the TailwindCSS version used for development: `v4.1.18`. Be sure to get the version for your architecture.
[TailwindCSS tags](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.18)
1. Rename the binary to `tailwindcss` and `chmod +x tailwindcss` to use. Make sure it's in your path (`venv/bin/tailwindcss` works well) to keep it just for this project.
Then:
```
tailwind -i static/css/input -o static/css/tailwind.css
```


Copy and paste to do it all in one go:
```
git clone https://github.com/mcguirepr89/Movie_Club.git && \
cd Movie_Club && \
python3 -m venv venv && \
source ./venv/bin/activate && \
pip install -U pip && \
pip install -r requirements.txt && \
mv movie_club/settings.py.fordevelopmentonly movie_club/settings.py && \
python manage.py makemigrations && \
python manage.py migrate && \
python manage.py loaddata people && \
python manage.py loaddata categories && \
python manage.py loaddata streaming_services && \
python manage.py loaddata movies && \
python manage.py runserver
```

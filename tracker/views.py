import random
from django.contrib import messages
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from .forms import MovieForm, ViewingForm
from .models import Movie, Viewing, Category, Person


def who_are_you(request):
    """
    Landing page: select who you are.
    """
    if request.method == "POST":
        person_id = request.POST.get("person")
        if person_id:
            request.session["person_id"] = int(person_id)
            return redirect("movie_list")

    people = Person.objects.order_by("name")
    return render(request, "tracker/who_are_you.html", {"people": people})


def change_user(request):
    """
    Clears the current session identity.
    """
    request.session.pop("person_id", None)
    return redirect("who_are_you")

def movie_list(request):
    if "person_id" not in request.session:
        return redirect("who_are_you")

    current_user = get_object_or_404(Person, pk=request.session["person_id"])

    movies = Movie.objects.prefetch_related(
        "categories", "streaming_services"
    )

    viewings = Viewing.objects.select_related("person", "movie")

    viewing_map = {}
    current_user_viewings = {}

    for v in viewings:
        if v.person_id == current_user.id:
            current_user_viewings[v.movie_id] = v
        else:
            viewing_map.setdefault(v.movie_id, []).append(v)

    return render(
        request,
        "tracker/movie_list.html",
        {
            "movies": movies,
            "current_user": current_user,
            "current_user_viewings": current_user_viewings,
            "viewing_map": viewing_map,
        },
    )

def movie_detail(request, movie_id):
    if "person_id" not in request.session:
        return redirect("who_are_you")

    current_user = get_object_or_404(Person, pk=request.session["person_id"])
    movie = get_object_or_404(
        Movie.objects.prefetch_related("categories", "streaming_services", "viewing_set__person"),
        pk=movie_id
    )

    # Current user's viewing
    try:
        current_user_viewing = Viewing.objects.get(person=current_user, movie=movie)
    except Viewing.DoesNotExist:
        current_user_viewing = None

    # Handle form submission to add/update viewing
    if request.method == "POST":
        form = ViewingForm(request.POST, instance=current_user_viewing)
        if form.is_valid():
            viewing = form.save(commit=False)
            viewing.person = current_user
            viewing.movie = movie
            viewing.save()
            return redirect("movie_detail", movie_id=movie.id)
    else:
        form = ViewingForm(instance=current_user_viewing)

    # All viewings for this movie
    other_viewings = movie.viewing_set.exclude(person=current_user)

    return render(
        request,
        "tracker/movie_detail.html",
        {
            "movie": movie,
            "current_user": current_user,
            "current_user_viewing": current_user_viewing,
            "other_viewings": other_viewings,
            "form": form,
        },
    )

def movie_edit(request, movie_id):
    if "person_id" not in request.session:
        return redirect("who_are_you")

    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == "POST":
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            return redirect("movie_detail", movie_id=movie.id)
    else:
        form = MovieForm(instance=movie)

    return render(
        request,
        "tracker/movie_edit.html",
        {
            "movie": movie,
            "form": form,
        },
    )

def movie_delete(request, movie_id):
    if "person_id" not in request.session:
        return redirect("who_are_you")

    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == "POST":
        movie.delete()
        messages.success(request, f"Movie '{movie.title}' has been deleted.")
        return redirect("movie_list")

    return render(
        request,
        "tracker/movie_delete_confirm.html",
        {"movie": movie},
    )

def toggle_seen(request, movie_id):
    """
    Toggle the 'seen' status for a movie for the current user.
    """
    if "person_id" not in request.session:
        return redirect("who_are_you")

    person = get_object_or_404(Person, pk=request.session["person_id"])
    movie = get_object_or_404(Movie, pk=movie_id)

    viewing, created = Viewing.objects.get_or_create(person=person, movie=movie)

    if created:
        # Mark as seen with no additional info yet
        viewing.save()
    else:
        # Already exists → remove it (unmark)
        viewing.delete()

    return redirect("movie_list")

def movie_suggest(request):
    """
    Suggest a movie for the current user, filtered by:
    - Seen / unseen (required)
    - Categories (optional)
    - Writer / Director / Starring (optional, select from DB values)
    """
    if "person_id" not in request.session:
        return redirect("who_are_you")

    person = get_object_or_404(Person, pk=request.session["person_id"])
    categories = Category.objects.all()

    # Get distinct choices from existing movies
    writers = Movie.objects.exclude(writer__isnull=True).exclude(writer__exact='').values_list('writer', flat=True).distinct().order_by('writer')
    directors = Movie.objects.exclude(director__isnull=True).exclude(director__exact='').values_list('director', flat=True).distinct().order_by('director')
    starring_set = set()
    for s in Movie.objects.exclude(starring__isnull=True).exclude(starring__exact='').values_list('starring', flat=True):
        actors = [actor.strip() for actor in s.split(',')]
        starring_set.update(actors)
    
    starring_list = sorted(starring_set)

    suggested_movie = None
    selected_categories = []
    seen_filter = "all"  # default
    writer_filter = ""
    director_filter = ""
    starring_filter = ""

    if request.method == "POST":
        seen_filter = request.POST.get("seen_filter", "unseen")
        selected_categories = request.POST.getlist("categories")
        writer_filter = request.POST.get("writer", "")
        director_filter = request.POST.get("director", "")
        starring_filter = request.POST.get("starring", "")

        movies = Movie.objects.all()

        # Seen/unseen filter
        viewed_ids = Viewing.objects.filter(person=person).values_list("movie_id", flat=True)
        if seen_filter == "unseen":
            movies = movies.exclude(id__in=viewed_ids)
        elif seen_filter == "seen":
            movies = movies.filter(id__in=viewed_ids)
        # else 'all' → no filtering

        # Categories filter
        if selected_categories:
            movies = movies.filter(categories__id__in=selected_categories).distinct()

        # Writer / Director / Starring filters
        if writer_filter:
            movies = movies.filter(writer=writer_filter)
        if director_filter:
            movies = movies.filter(director=director_filter)
        if starring_filter:
            movies = movies.filter(starring__icontains=starring_filter)

        movies_list = list(movies)
        if movies_list:
            suggested_movie = random.choice(movies_list)

    return render(
        request,
        "tracker/movie_suggest.html",
        {
            "person": person,
            "categories": categories,
            "writers": writers,
            "directors": directors,
            "starring_list": starring_list,
            "suggested_movie": suggested_movie,
            "selected_categories": [int(c) for c in selected_categories],
            "seen_filter": seen_filter,
            "writer_filter": writer_filter,
            "director_filter": director_filter,
            "starring_filter": starring_filter,
        },
    )

def add_movie(request):
    if "person_id" not in request.session:
        return redirect("who_are_you")

    current_user = Person.objects.get(pk=request.session["person_id"])

    if request.method == "POST":
        movie_form = MovieForm(request.POST)
        viewing_form = ViewingForm(request.POST)

        if movie_form.is_valid() and viewing_form.is_valid():
            # Save the movie
            movie = movie_form.save(commit=False)
            movie.recommended_by = current_user
            movie.save()
            movie_form.save_m2m()  # Save categories & streaming services

            # Save viewing tied to current user
            viewing = viewing_form.save(commit=False)
            viewing.person = current_user
            viewing.movie = movie
            viewing.save()

            return redirect("movie_list")  # Redirect to movie list after adding

    else:
        movie_form = MovieForm()
        viewing_form = ViewingForm()

    return render(
        request,
        "tracker/movie_add.html",
        {"movie_form": movie_form, "viewing_form": viewing_form},
    )

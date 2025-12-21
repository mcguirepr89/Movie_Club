import random
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth.models import User
from .forms import MovieForm, ViewingForm
from .models import Movie, Viewing, Category, StreamingService

SORT_OPTIONS = {
    "title_asc": "title",
    "title_desc": "-title",
    "year_asc": "year",
    "year_desc": "-year",
    "recent": "-created_at",
}

def movie_list(request):
    # Base queryset
    movies = Movie.objects.prefetch_related(
        "categories",
        "streaming_services",
    ).all()

    # --- Sorting ---
    sort_key = request.GET.get("sort", "title_asc")
    ordering = SORT_OPTIONS.get(sort_key, "title")
    movies = movies.order_by(ordering)

    # --- Filters ---
    # Seen/Unseen
    seen_filter = ""
    if request.user.is_authenticated:
        seen_filter = request.GET.get("seen")
        if seen_filter == "1":
            movies = movies.filter(viewing__user=request.user)
        elif seen_filter == "0":
            movies = movies.exclude(viewing__user=request.user)

    # Categories (multi-choice)
    category_ids = request.GET.getlist("categories")
    if category_ids:
        movies = movies.filter(categories__id__in=category_ids).distinct()

    # Director / Writer / Starring filters
    director_filter = request.GET.get("director", "")
    if director_filter:
        movies = movies.filter(director=director_filter)

    writer_filter = request.GET.get("writer", "")
    if writer_filter:
        movies = movies.filter(writer=writer_filter)

    starring_filter = request.GET.get("starring", "")
    if starring_filter:
        movies = movies.filter(starring__icontains=starring_filter)

    # Recommender / Streaming filters
    recommender_id = request.GET.get("recommended_by", "")
    if recommender_id:
        movies = movies.filter(recommended_by__id=recommender_id)

    streaming_id = request.GET.get("streaming", "")
    if streaming_id:
        movies = movies.filter(streaming_services__id=streaming_id)

    # --- Viewings mapping ---
    current_user_viewings = {}
    viewing_map = {}
    viewings = Viewing.objects.select_related("user", "movie")

    if request.user.is_authenticated:
        for v in viewings:
            if v.user_id == request.user.id:
                current_user_viewings[v.movie_id] = v
            else:
                viewing_map.setdefault(v.movie_id, []).append(v)
    else:
        for v in viewings:
            viewing_map.setdefault(v.movie_id, []).append(v)

    # --- Filter data for dropdowns ---
    categories = Category.objects.all().order_by("name")
    streaming_services = StreamingService.objects.all()
    recommenders = User.objects.filter(recommended_movies__isnull=False).distinct()
    writers = Movie.objects.exclude(writer="").values_list("writer", flat=True).distinct()
    directors = Movie.objects.exclude(director="").values_list("director", flat=True).distinct()
    starring_list = sorted({
        a.strip()
        for s in Movie.objects.exclude(starring="").values_list("starring", flat=True)
        for a in s.split(",")
    })

    context = {
        "movies": movies,
        "current_user_viewings": current_user_viewings,
        "viewing_map": viewing_map,
        "categories": categories,
        "streaming_services": streaming_services,
        "recommenders": recommenders,
        "sort": sort_key,
        "selected_seen": seen_filter,
        "selected_categories": category_ids,
        "selected_director": director_filter,
        "selected_writer": writer_filter,
        "selected_starring": starring_filter,
        "selected_recommender": recommender_id,
        "selected_streaming": streaming_id,
        "writers": writers,
        "directors": directors,
        "starring_list": starring_list,
    }

    # --- AJAX response for live filtering ---
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "tracker/_movie_grid.html", context)

    # --- Full page render ---
    return render(request, "tracker/movie_list.html", context)

def movie_detail(request, movie_id):
    movie = get_object_or_404(
        Movie.objects.prefetch_related(
            "categories",
            "streaming_services",
            "viewing_set__user",
        ),
        pk=movie_id,
    )

    current_user_viewing = None
    form = None

    if request.user.is_authenticated:
        try:
            current_user_viewing = Viewing.objects.get(
                user=request.user,
                movie=movie,
            )
        except Viewing.DoesNotExist:
            current_user_viewing = None

        if request.method == "POST":
            form = ViewingForm(request.POST, instance=current_user_viewing)
            if form.is_valid():
                viewing = form.save(commit=False)
                viewing.user = request.user
                viewing.movie = movie
                viewing.save()
                return redirect("movie_detail", movie_id=movie.id)
        else:
            form = ViewingForm(instance=current_user_viewing)

    other_viewings = movie.viewing_set.exclude(
        user=request.user
    ) if request.user.is_authenticated else movie.viewing_set.all()

    return render(
        request,
        "tracker/movie_detail.html",
        {
            "movie": movie,
            "current_user_viewing": current_user_viewing,
            "other_viewings": other_viewings,
            "form": form,
        },
    )

@login_required
def add_movie(request):
    if request.method == "POST":
        movie_form = MovieForm(request.POST, request.FILES)
        viewing_form = ViewingForm(request.POST)

        if movie_form.is_valid() and viewing_form.is_valid():
            movie = movie_form.save(commit=False)
            movie.recommended_by = request.user
            movie.save()
            movie_form.save_m2m()

            viewing = viewing_form.save(commit=False)
            viewing.user = request.user
            viewing.movie = movie
            viewing.save()

            return redirect("movie_list")
    else:
        movie_form = MovieForm()
        viewing_form = ViewingForm()

    return render(
        request,
        "tracker/movie_add.html",
        {
            "movie_form": movie_form,
            "viewing_form": viewing_form,
        },
    )

@login_required
def movie_edit(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES, instance=movie)
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

@login_required
def movie_delete(request, movie_id):
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

@login_required
def toggle_seen(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    viewing, created = Viewing.objects.get_or_create(
        user=request.user,
        movie=movie,
    )

    if not created:
        viewing.delete()
        status = "unseen"
    else:
        status = "seen"

    # If AJAX, return JSON instead of redirect
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": status})

    return redirect("movie_list")

def movie_suggest(request):
    categories = Category.objects.all().order_by("name")

    writers = Movie.objects.exclude(writer__exact="").values_list(
        "writer", flat=True
    ).distinct().order_by("writer")

    directors = Movie.objects.exclude(director__exact="").values_list(
        "director", flat=True
    ).distinct().order_by("director")

    starring_set = set()
    for s in Movie.objects.exclude(starring__exact="").values_list("starring", flat=True):
        starring_set.update(a.strip() for a in s.split(","))

    suggested_movie = None

    if request.method == "POST":
        movies = Movie.objects.all()

        if request.user.is_authenticated:
            viewed_ids = Viewing.objects.filter(
                user=request.user
            ).values_list("movie_id", flat=True)

            seen_filter = request.POST.get("seen_filter", "unseen")
            if seen_filter == "unseen":
                movies = movies.exclude(id__in=viewed_ids)
            elif seen_filter == "seen":
                movies = movies.filter(id__in=viewed_ids)

        selected_categories = request.POST.getlist("categories")
        if selected_categories:
            movies = movies.filter(categories__id__in=selected_categories).distinct()

        if request.POST.get("writer"):
            movies = movies.filter(writer=request.POST["writer"])
        if request.POST.get("director"):
            movies = movies.filter(director=request.POST["director"])
        if request.POST.get("starring"):
            movies = movies.filter(starring__icontains=request.POST["starring"])

        movies = list(movies)
        if movies:
            suggested_movie = random.choice(movies)

    return render(
        request,
        "tracker/movie_suggest.html",
        {
            "categories": categories,
            "writers": writers,
            "directors": directors,
            "starring_list": sorted(starring_set),
            "suggested_movie": suggested_movie,
        },
    )

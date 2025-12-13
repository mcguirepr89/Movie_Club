from django.urls import path
from . import views

urlpatterns = [
    path("", views.who_are_you, name="who_are_you"),
    path("change-user/", views.change_user, name="change_user"),
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/toggle/<int:movie_id>/", views.toggle_seen, name="toggle_seen"),
    path("suggest/", views.movie_suggest, name="movie_suggest"),
    path("add/", views.add_movie, name="add_movie"),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:movie_id>/edit/', views.movie_edit, name='movie_edit'),
    path('movies/<int:movie_id>/delete/', views.movie_delete, name='movie_delete'),
]

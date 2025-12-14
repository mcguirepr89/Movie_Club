from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, StreamingService, Movie, Viewing


# -----------------------------
# Viewing Inline for MovieAdmin
# -----------------------------
class ViewingInline(admin.TabularInline):
    model = Viewing
    extra = 1  # Show one empty form by default for adding new viewing
    fields = ("user", "watched_on", "rating", "comment", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)
    ordering = ("-created_at",)
    show_change_link = True


# -----------------------------
# Movie Admin
# -----------------------------
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "year",
        "recommended_by",
        "display_categories",
        "display_streaming_services",
    )
    list_filter = ("categories", "streaming_services", "recommended_by")
    search_fields = ("title", "director", "writer", "starring")
    ordering = ("title",)
    inlines = [ViewingInline]
    autocomplete_fields = ("recommended_by", "categories", "streaming_services")

    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    display_categories.short_description = "Categories"

    def display_streaming_services(self, obj):
        return ", ".join([s.name for s in obj.streaming_services.all()])

    display_streaming_services.short_description = "Streaming Services"


# -----------------------------
# Viewing Admin
# -----------------------------
@admin.register(Viewing)
class ViewingAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "watched_on", "rating", "comment", "created_at")
    list_filter = ("watched_on", "rating", "movie", "user")
    search_fields = ("movie__title", "user__username", "comment")
    autocomplete_fields = ("user", "movie")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


# -----------------------------
# Category Admin
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# -----------------------------
# Streaming Service Admin
# -----------------------------
@admin.register(StreamingService)
class StreamingServiceAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

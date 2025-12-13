from django import forms
from .models import Movie, Viewing, Category, StreamingService

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            "title",
            "year",
            "description",
            "runtime_minutes",
            "starring",
            "director",
            "writer",
            "categories",
            "streaming_services",
        ]
        widgets = {
            "categories": forms.CheckboxSelectMultiple,
            "streaming_services": forms.CheckboxSelectMultiple,
        }


class ViewingForm(forms.ModelForm):
    class Meta:
        model = Viewing
        fields = ["watched_on", "rating", "comment"]
        widgets = {
            "watched_on": forms.DateInput(attrs={"type": "date"}),
            "rating": forms.NumberInput(attrs={"step": 0.5, "min": 0, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 2}),
        }

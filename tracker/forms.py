from django import forms
from .models import Movie, Viewing


class TailwindFormMixin:
    BASE_INPUT_CLASSES = (
        "block w-full rounded-md border border-gray-300 "
        "px-3 py-2 shadow-sm "
        "focus:border-indigo-500 focus:ring-indigo-500"
    )

    TEXTAREA_CLASSES = (
        "block w-full rounded-md border border-gray-300 "
        "px-3 py-2 shadow-sm "
        "focus:border-indigo-500 focus:ring-indigo-500"
    )

    CHECKBOX_GROUP_CLASSES = "space-y-2"

    def apply_tailwind_classes(self):
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get("class", "")

            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{existing} {self.CHECKBOX_GROUP_CLASSES}".strip()

            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = f"{existing} {self.TEXTAREA_CLASSES}".strip()

            else:
                widget.attrs["class"] = f"{existing} {self.BASE_INPUT_CLASSES}".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_tailwind_classes()


class MovieForm(TailwindFormMixin, forms.ModelForm):
    """
    Movie creation/editing form.
    `recommended_by` must be assigned in the view using request.user.
    """

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
	    "poster",
        ]
        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
            "streaming_services": forms.CheckboxSelectMultiple(),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ViewingForm(TailwindFormMixin, forms.ModelForm):
    """
    Viewing form.
    The `user` and `movie` must be assigned in the view.
    """

    class Meta:
        model = Viewing
        fields = ["watched_on", "rating", "comment"]
        widgets = {
            "watched_on": forms.DateInput(attrs={"type": "date"}),
            "rating": forms.NumberInput(attrs={"step": 0.5, "min": 0, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 2}),
        }

from django import forms
from .models import UserProfile


class ProfileForm(forms.ModelForm):
    """
    This is to create a form for the user
    to fill to create an account
    """
    class Meta:
        model = UserProfile
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "default_phone_number": "Phone Number",
            "default_county": "County, State or Locality",
            "default_street_add_line1": "First Line of your Address",
            "default_street_add_line2": "Second Line of your Address",
            "default_town_r_city": "Town / City",
            "default_postcode": "Postal Code"}

        self.fields["default_phone_number"].widget.attrs["autofocus"] = True
        for field in self.fields:
            if field != "default_country":
                if self.fields[field].required:
                    placeholder = f"{placeholders[field]}"
                else:
                    placeholder = placeholders[field]
            self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].label = False
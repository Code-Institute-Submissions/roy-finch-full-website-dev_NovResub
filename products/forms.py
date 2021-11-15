from django import forms
from .widget import CustomFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    Form for the products when adding and removing
    products from the website
    """
    class Meta:
        model = Product
        fields = "__all__"

    image = forms.ImageField(
        label="Image", required=False, widget=CustomFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "w-100 mb-3 p-2"

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import ProfileForm


@login_required
def profile(request):
    """
    This is to render the profile
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile update successfully')
        else:
            messages.error(request, "Unable to update your profile")
    else:
        form = ProfileForm(instance=profile)
    orders = profile.orders.all()

    context = {
        "profile": profile,
        "form": form,
        "orders": orders,
    }

    return render(request, 'profiles/profiles.html', context)

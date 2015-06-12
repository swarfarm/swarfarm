from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import FeedbackForm

@login_required
def index(request):
    form = FeedbackForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        feedback = form.save(commit=False)
        feedback.user = request.user.username
        feedback.save()

        return redirect('feedback:thanks')

    return render(request, 'feedback/index.html', {'form': form})


def thanks(request):
    return render(request, 'feedback/thanks.html')

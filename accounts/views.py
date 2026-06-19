from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:poll_list')
    else:
        form = UserCreationForm()

    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    # Simplify help text — Django's default is too verbose for the UI
    form.fields['username'].help_text = 'Letters, digits and @/./+/-/_ only.'
    form.fields['password1'].help_text = 'At least 8 characters, not entirely numeric.'
    form.fields['password2'].help_text = ''

    return render(request, 'accounts/signup.html', {'form': form})
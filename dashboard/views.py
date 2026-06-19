from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from polls.models import Poll, Choice, Vote


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    total_polls = Poll.objects.count()
    active_polls = Poll.objects.filter(is_active=True).count()
    total_votes = Vote.objects.count()
    total_users = User.objects.count()

    recent_polls = Poll.objects.order_by('-created_at')[:5]

    return render(request, 'dashboard/home.html', {
        'total_polls': total_polls,
        'active_polls': active_polls,
        'total_votes': total_votes,
        'total_users': total_users,
        'recent_polls': recent_polls,
    })


@login_required
@user_passes_test(is_admin)
def create_poll(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        show_results_before_end = request.POST.get('show_results_before_end') == 'on'

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('dashboard:create_poll')

        poll = Poll.objects.create(
            title=title,
            description=description,
            show_results_before_end=show_results_before_end,
        )

        # Handle dynamic choices (choice_1, choice_2, choice_3, ...)
        choice_texts = request.POST.getlist('choices')
        valid_choices = [c.strip() for c in choice_texts if c.strip()]

        if len(valid_choices) < 2:
            poll.delete()
            messages.error(request, 'Please provide at least 2 choices.')
            return redirect('dashboard:create_poll')

        for choice_text in valid_choices:
            Choice.objects.create(poll=poll, choice_text=choice_text)

        messages.success(request, f'Poll "{poll.title}" created successfully!')
        return redirect('dashboard:manage_polls')

    return render(request, 'dashboard/create_poll.html')


@login_required
@user_passes_test(is_admin)
def manage_polls(request):
    polls = Poll.objects.order_by('-created_at')
    return render(request, 'dashboard/manage_polls.html', {'polls': polls})


@login_required
@user_passes_test(is_admin)
def edit_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if request.method == 'POST':
        poll.title = request.POST.get('title')
        poll.description = request.POST.get('description')
        poll.show_results_before_end = request.POST.get('show_results_before_end') == 'on'
        poll.save()
        messages.success(request, 'Poll updated successfully!')
        return redirect('dashboard:manage_polls')

    return render(request, 'dashboard/edit_poll.html', {'poll': poll})


@login_required
@user_passes_test(is_admin)
def delete_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    poll.delete()
    messages.success(request, 'Poll deleted.')
    return redirect('dashboard:manage_polls')


@login_required
@user_passes_test(is_admin)
def toggle_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    poll.is_active = not poll.is_active
    poll.save()
    return redirect('dashboard:manage_polls')


@login_required
@user_passes_test(is_admin)
def poll_monitor(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    choices = poll.choices.all()
    total_votes = sum(c.vote_count for c in choices)

    for choice in choices:
        choice.percentage = round((choice.vote_count / total_votes) * 100, 1) if total_votes > 0 else 0

    votes = Vote.objects.filter(poll=poll).select_related('user', 'choice').order_by('-voted_at')

    return render(request, 'dashboard/poll_monitor.html', {
        'poll': poll,
        'choices': choices,
        'total_votes': total_votes,
        'votes': votes,
    })
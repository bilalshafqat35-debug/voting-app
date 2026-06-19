from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Poll, Choice, Vote


def poll_list(request):
    polls = Poll.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'polls/poll_list.html', {'polls': polls})


@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    already_voted = Vote.objects.filter(user=request.user, poll=poll).exists()
    return render(request, 'polls/poll_detail.html', {
        'poll': poll,
        'already_voted': already_voted,
    })


@login_required
def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    # Check: already voted?
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        messages.error(request, 'You have already voted on this poll.')
        return redirect('polls:results', poll_id=poll.id)

    # Check: poll time window
    now = timezone.now()
    if poll.start_time and now < poll.start_time:
        messages.error(request, 'Voting has not started yet.')
        return redirect('polls:poll_detail', poll_id=poll.id)
    if poll.end_time and now > poll.end_time:
        messages.error(request, 'Voting has ended for this poll.')
        return redirect('polls:results', poll_id=poll.id)

    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if not choice_id:
            messages.error(request, 'Please select a choice.')
            return redirect('polls:poll_detail', poll_id=poll.id)

        choice = get_object_or_404(Choice, id=choice_id, poll=poll)

        # Save the vote record
        Vote.objects.create(user=request.user, poll=poll, choice=choice)

        # Update vote count
        choice.vote_count += 1
        choice.save()

        messages.success(request, 'Your vote has been recorded!')
        return redirect('polls:results', poll_id=poll.id)

    return redirect('polls:poll_detail', poll_id=poll.id)


@login_required
def results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.show_results_before_end and poll.end_time:
        now = timezone.now()
        if now < poll.end_time:
            messages.info(request, 'Results will be visible after voting ends.')
            return redirect('polls:poll_detail', poll_id=poll.id)

    choices = poll.choices.all()
    total_votes = sum(c.vote_count for c in choices)

    # Calculate percentage for each choice
    for choice in choices:
        if total_votes > 0:
            choice.percentage = round((choice.vote_count / total_votes) * 100, 1)
        else:
            choice.percentage = 0

    return render(request, 'polls/results.html', {
        'poll': poll,
        'choices': choices,
        'total_votes': total_votes,
    })
from django.http import JsonResponse


@login_required
def poll_results_data(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    choices = poll.choices.all()
    total_votes = sum(c.vote_count for c in choices)

    data = []
    for choice in choices:
        percentage = round((choice.vote_count / total_votes) * 100, 1) if total_votes > 0 else 0
        data.append({
            'id': choice.id,
            'choice_text': choice.choice_text,
            'vote_count': choice.vote_count,
            'percentage': percentage,
        })

    return JsonResponse({
        'total_votes': total_votes,
        'choices': data,
    })
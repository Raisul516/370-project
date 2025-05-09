from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Historicalevents, Profile, Notification , HistoricalEventUpvote
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Q, Count
from .forms import HistoricalEventForm, EventRejectionForm


def home_view(request):
    recent_events = Historicalevents.objects.filter(status='approved').order_by('-created_at')[:6]
    categories = Historicalevents.objects.filter(status='approved').values_list('category', flat=True).distinct()
    todays_events = Historicalevents.objects.filter(
        Q(status='approved') & Q(eventdate=now().date())
    ).order_by('-importance')[:5]
    
    context = {
        'recent_events': recent_events,
        'categories': categories,
        'todays_events': todays_events,
    }
    return render(request, 'accounts/home.html', context)

def search_events(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    date = request.GET.get('date', '')
    importance = request.GET.get('importance', '')
    
    events = Historicalevents.objects.filter(status='approved')
    
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    if category:
        events = events.filter(category=category)
    
    if date:
        events = events.filter(eventdate=date)
    
    if importance:
        events = events.filter(importance=importance)
    
    events = events.order_by('-created_at')
    
    context = {
        'events': events,
        'query': query,
        'selected_category': category,
        'selected_date': date,
        'selected_importance': importance,
        'categories': Historicalevents.objects.values_list('category', flat=True).distinct(),
    }
    return render(request, 'accounts/search_results.html', context)

def event_detail_view(request, event_id):
    # Fetch the event with the given ID or return a 404 error if not found
    event = get_object_or_404(Historicalevents, id=event_id)
    return render(request, 'accounts/event_detail.html', {'event': event})

def category_events_view(request, category):
    # Fetch events based on the given category
    events = Historicalevents.objects.filter(status='approved', category=category)

    context = {
        'category': category,
        'events': events,
    }

    return render(request, 'accounts/category_events.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            # Handle profile information update
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            
            # Check if username is taken by another user
            if User.objects.exclude(id=request.user.id).filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('edit_profile')
            
            # Check if email is taken by another user
            if User.objects.exclude(id=request.user.id).filter(email=email).exists():
                messages.error(request, 'Email is already taken.')
                return redirect('edit_profile')
            
            # Update user information
            request.user.username = username
            request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            
            messages.success(request, 'Profile updated successfully!')
            
        elif form_type == 'password':
            # Handle password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Verify current password
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('edit_profile')
            
            # Check if new passwords match
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('edit_profile')
            
            # Update password
            request.user.set_password(new_password)
            request.user.save()
            
            messages.success(request, 'Password changed successfully! Please log in again.')
            return redirect('login')
    
    return render(request, 'accounts/edit_profile.html')

@login_required
def submit_event_view(request):
    if request.method == 'POST':
        form = HistoricalEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.submitted_by = request.user

            # Auto-approve for verified users and superusers
            if request.user.is_superuser or request.user.profile.is_verified:
                event.status = 'approved'
                event.points_awarded = 100
                request.user.profile.points += 100
                request.user.profile.save()
            else:
                event.status = 'pending'

            event.save()
            messages.success(request, 'Event submitted successfully!')
            return redirect('dashboard')
    else:
        form = HistoricalEventForm()

    return render(request, 'accounts/submit_event.html', {'form': form})

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        notifications.update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    return render(request, 'accounts/notifications.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, "passwords do not match")
            return redirect('register')
            #return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            messages.error(request, "username already exists")
            return redirect('register')
            #return render(request, 'accounts/register.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')    

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request,"registration successful.Please log in")
        return redirect('login')
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    user_events = Historicalevents.objects.filter(submitted_by=request.user).order_by('-created_at')
    approved_events_count = user_events.filter(status='approved').count()
    
    # Auto-verify user if they have 10 or more approved posts
    if approved_events_count >= 10 and not profile.is_verified:
        profile.is_verified = True
        profile.save()
    
    context = {
        'profile': profile,
        'user_events': user_events,
        'approved_events_count': approved_events_count,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def my_contributions_view(request):
    # Assuming you have a model `Historicalevents` to track user contributions
    user_events = Historicalevents.objects.filter(submitted_by=request.user)

    context = {
        'events': user_events,
    }
    return render(request, 'accounts/my_contributions.html', context)

@login_required
def dashboard_view(request):
    # Get events submitted by the logged-in user
    user_events = Historicalevents.objects.filter(submitted_by=request.user).order_by('-created_at')
    user_events.approved = user_events.filter(status='approved')
    user_events.pending = user_events.filter(status='pending')
    user_events.rejected = user_events.filter(status='rejected')

    
    
    # Fetch pending events for review (only for verified users or superusers)
    pending_events_for_review = []
    if request.user.is_superuser or request.user.profile.is_verified:
        pending_events_for_review = Historicalevents.objects.filter(status='pending').exclude(submitted_by=request.user)

    # Get all approved events for the search functionality
    all_events = Historicalevents.objects.filter(status='approved').order_by('-created_at')
    
    # Get top contributors (users with most approved events)
    top_contributors = User.objects.annotate(
        approved_events_count=Count('submitted_events', filter=Q(submitted_events__status='approved'))
    ).filter(approved_events_count__gt=0).order_by('-approved_events_count')[:5]
    
    # Get total users count
    total_users = User.objects.count()
    
    # Get categories for search filter
    categories = Historicalevents.objects.values_list('category', flat=True).distinct()
    
    # Get user's notifications - fixed to avoid slice error
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'user_events': user_events,
        'all_events': all_events,
        'top_contributors': top_contributors,
        'total_users': total_users,
        'categories': categories,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'pending_events_for_review': pending_events_for_review,  # Add pending events for review
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def approve_event(request, event_id):
    # Check if user is authorized (superuser or verified)
    if not (request.user.is_superuser or request.user.profile.is_verified):
        messages.error(request, "You are not authorized to approve events.")
        return redirect('dashboard')

    event = get_object_or_404(Historicalevents, id=event_id)
    
    # Don't allow users to approve their own events unless they're superusers
    if event.submitted_by == request.user and not request.user.is_superuser:
        messages.error(request, "You cannot approve your own events.")
        return redirect('dashboard')

    event.status = 'approved'
    event.reviewed_by = request.user
    event.points_awarded = 100
    event.save()

    # Update submitter's points and approved posts count
    submitter_profile = event.submitted_by.profile
    submitter_profile.points += event.points_awarded
    submitter_profile.approved_posts_count += 1
    submitter_profile.save()

    # Create notification for event approval
    Notification.objects.create(
        user=event.submitted_by,
        type='approval',
        message=f'Your event "{event.title}" has been approved! You earned {event.points_awarded} points.',
        related_event=event
    )

    # Create notification for points awarded
    Notification.objects.create(
        user=event.submitted_by,
        type='points',
        message=f'You earned {event.points_awarded} points for your approved event "{event.title}".',
        related_event=event
    )

    # Check if user is now eligible for verification
    if submitter_profile.approved_posts_count >= 5 and not submitter_profile.is_verified:
        submitter_profile.is_verified = True
        submitter_profile.save()
        
        # Create notification for verification
        Notification.objects.create(
            user=event.submitted_by,
            type='verification',
            message='Congratulations! Your account has been verified due to your consistent quality contributions.'
        )

    messages.success(request, f"Event '{event.title}' approved successfully.")
    return redirect('dashboard')

@login_required
def reject_event(request, event_id):
    # Check if user is authorized (superuser or verified)
    if not (request.user.is_superuser or request.user.profile.is_verified):
        messages.error(request, "You are not authorized to reject events.")
        return redirect('dashboard')

    event = get_object_or_404(Historicalevents, id=event_id)

    # Don't allow users to reject their own events unless they're superusers
    if event.submitted_by == request.user and not request.user.is_superuser:
        messages.error(request, "You cannot reject your own events.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EventRejectionForm(request.POST)
        if form.is_valid():
            event.status = 'rejected'
            event.rejection_reason = form.cleaned_data['reason']
            event.reviewed_by = request.user
            event.save()

            # Create notification for event rejection
            Notification.objects.create(
                user=event.submitted_by,
                type='rejection',
                message=f'Your event "{event.title}" was not approved. Reason: {event.rejection_reason}',
                related_event=event
            )

            messages.success(request, f"Event '{event.title}' rejected with reason: {event.rejection_reason}")
            return redirect('dashboard')
    else:
        form = EventRejectionForm()

    return render(request, 'accounts/reject_event.html', {'form': form, 'event': event})

@login_required
def toggle_upvote(request, event_id):
    event = get_object_or_404(Historicalevents, id=event_id)
    
    # Don't allow users to upvote their own events
    if event.submitted_by == request.user:
        messages.error(request, "You cannot upvote your own events.")
        return redirect('event_detail', event_id=event_id)
    
    event.toggle_upvote(request.user)
    return redirect('event_detail', event_id=event_id)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, "Notification marked as read.")
    return redirect('dashboard')
@login_required
def vote_event(request, event_id, vote_type):
    event = get_object_or_404(Historicalevents, id=event_id)

    if vote_type not in ['upvote', 'downvote']:
        messages.error(request, "Invalid vote type.")
        return redirect('event_detail', event_id=event.id)

    # Get the current user (the actual User instance)
    user = request.user

    # Check if the user has already voted on this event
    existing_vote = HistoricalEventUpvote.objects.filter(user=user, historicalevent=event).first()
    if existing_vote:
        messages.error(request, "You have already voted on this event.")
        return redirect('event_detail', event_id=event.id)

    # Create the vote entry
    HistoricalEventUpvote.objects.create(
        user=user,  # Use the User instance for the user who is voting
        historicalevent=event,  # The event being voted on
        vote_type=vote_type  # The vote type (upvote or downvote)
    )

    # Update the event's points based on the vote type
    if vote_type == 'upvote':
        event.points_awarded += 10
    elif vote_type == 'downvote':
        event.points_awarded -= 10

    event.save()

    messages.success(request, "Your vote has been recorded.")
    return redirect('event_detail', event_id=event.id)
@login_required
def event_detail_view(request, event_id):
    # Fetch the event object
    event = get_object_or_404(Historicalevents, id=event_id)

    # Calculate vote counts
    upvote_count = event.get_vote_count('upvote')
    downvote_count = event.get_vote_count('downvote')

    # Check the user's vote, if authenticated
    user_vote = None
    if request.user.is_authenticated:
        try:
            # Correcting this line: we want to query based on the User instance
            user_vote = event.votes.get(user=request.user).vote_type
        except HistoricalEventUpvote.DoesNotExist:
            user_vote = None

    # Pass the calculated data to the template
    context = {
        'event': event,
        'upvote_count': upvote_count,
        'downvote_count': downvote_count,
        'user_vote': user_vote,
    }
    return render(request, 'accounts/event_detail.html', context)
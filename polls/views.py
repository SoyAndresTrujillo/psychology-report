from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Polls 
from .forms import PollsForm


def home_view(request):
    """Home page with navigation to all sections.
    
    Technical Details:
    - Simple template rendering view
    - No database queries
    - Serves as entry point for the application
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered home.html template
    """
    return render(request, 'home.html')


def create_poll_view(request):
    """Create a new poll.
    
    Technical Details:
    - Handles POST requests for poll creation via PollsForm
    - Uses Django's form validation pipeline (clean methods)
    - Implements atomic operation: poll creation
    - Redirects to polls list on success with flash message
    
    Form Validation:
    - PollForm.clean_rate(): Ensures rate is between 0 and 5
    
    Database Operations:
    - Creates Poll instance via form.save()
    
    Args:
        request: HttpRequest object containing POST data or GET request
        
    Returns:
        HttpResponse: Rendered create form or redirect to accounts:list
    """
    if request.method == 'POST':
        form = PollsForm(request.POST)
        if form.is_valid():
            poll = form.save()
            
            messages.success(request, f'Poll "{poll.description}" created successfully!')
            return redirect('polls:list')
    else:
        form = PollsForm()
    
    return render(request, 'polls/create.html', {'form': form})


def list_polls_view(request):
    """List all polls with statistics.
    
    Technical Details:
    - Retrieves all Poll objects ordered by rates (descending)
    - No pagination implemented (consider for large datasets)
    
    Database Queries:
    - SELECT * FROM polls ORDER BY rate DESC
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered list template with polls and statistics
    """
    polls = Polls.objects.all().order_by('-rate')
    context = {
        'polls': polls,
        'total_count': polls.count(),
    }
    return render(request, 'polls/list.html', context)


def poll_detail_view(request, poll_id):
    """View detailed poll information.
    
    Technical Details:
    - Uses get_object_or_404 for safe object retrieval (raises Http404)
    
    Database Queries:
    - SELECT * FROM polls WHERE id = poll_id
    
    Args:
        request: HttpRequest object
        poll_id: Integer primary key of the Poll to retrieve
        
    Returns:
        HttpResponse: Rendered detail template with poll
        
    Raises:
        Http404: If poll with given ID does not exist
    """
    poll = get_object_or_404(Polls, id=poll_id)
    
    context = {
        'poll': poll,
    }
    return render(request, 'polls/detail.html', context)

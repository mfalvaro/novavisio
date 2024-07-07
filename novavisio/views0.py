from django.shortcuts import render
from django.http import HttpResponse


##-----------------------------GLOBALS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##--------------------FUNCTIONS AND CLASSES---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##    HOME PAGE **********************************************************************************************************************************************************************    HOME PAGE
def home(request):
    """View function for home page of site."""
  # Number of visits to this view, as counted in the session variable.
    num_visits = 0
    context = {
        'num_visits': num_visits,
    }
  # Render the HTML template index.html with the data in the context variable
    return render(request, 'home.html', context=context)

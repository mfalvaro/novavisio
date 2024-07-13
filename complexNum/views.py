from django.shortcuts import render
from django.http import HttpResponse


##-----------------------------GLOBALS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##--------------------FUNCTIONS AND CLASSES---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##    home_cNum PAGE **********************************************************************************************************************************************************************    HOME PAGE
def home_cNum(request):
    """View function for home page of site."""

    # Number of visits to this view, as counted in the session variable.
    num_visits = 0



    context = {
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'complexNum/home_cNum.html', context=context)



def topicos_cNum(request):
    """View function for home page of site."""

    # Number of visits to this view, as counted in the session variable.
    num_visits = 0



    context = {
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'complexNum/Estrutura_topicos.htm', context=context)

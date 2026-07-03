from django.shortcuts import render

def portfolio_home(request):
    return render(request, 'portfolio/portfolio.html')
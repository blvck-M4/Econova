from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
def members(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())
def connexion(request):
    if request.method == 'POST':
        print(request.POST)

    template = loader.get_template('connexion.html')
    return render(request, 'connexion.html')

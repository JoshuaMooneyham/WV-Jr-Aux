from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def aboutUs(request):
    return render(request, 'about.html')

def projectsPage(request):
    return render(request, 'projects.html')

def contactUs(request):
    return render(request, 'contactus.html')

def loginPage(request):
    return render(request, 'login.html')

def logoutUser(request):
    return render(request, 'logout.html')
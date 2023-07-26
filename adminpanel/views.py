from django.shortcuts import render

def testSite(request):
    return render(request, 'adminpanel/base.html')

"""
Mobile App Views for Repli
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import os


def mobile_index(request):
    """Mobile app landing/splash screen"""
    return render(request, 'mobile/index.html')


def mobile_onboarding(request):
    """Mobile app onboarding flow"""
    return render(request, 'mobile/onboarding.html')


def mobile_app(request):
    """Main mobile app interface"""
    return render(request, 'mobile/app.html')


def mobile_create(request):
    """Mobile content creation interface"""
    return render(request, 'mobile/create.html')


def mobile_library(request):
    """Mobile content library"""
    return render(request, 'mobile/library.html')


def mobile_profile(request):
    """Mobile user profile"""
    return render(request, 'mobile/profile.html')


def mobile_simulator(request):
    """Mobile simulator for testing"""
    # Read the HTML file and return it
    simulator_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mobile_simulator.html')
    try:
        with open(simulator_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Mobile simulator not found", status=404)


@csrf_exempt
def mobile_api(request):
    """Mobile API proxy for handling requests"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Handle mobile-specific API calls
            return JsonResponse({'status': 'success', 'data': data})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'})
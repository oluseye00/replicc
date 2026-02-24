"""
Frontend views for the Repli web interface
"""
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    """Landing page"""
    return render(request, "repli/index.html")


@login_required
def dashboard(request):
    """User dashboard"""
    # In a real implementation, you'd fetch user's actual data here
    context = {
        "user": request.user,
    }
    return render(request, "repli/dashboard.html", context)


@login_required
def create_content(request):
    """Content creation interface"""
    # Get content type from query params for pre-selection
    content_type = request.GET.get("type", "social")

    context = {
        "content_type": content_type,
        "user": request.user,
    }
    return render(request, "repli/create.html", context)


def login_view(request):
    """Login page"""
    return render(request, "repli/auth/login.html")


def register_view(request):
    """Registration page"""
    return render(request, "repli/auth/register.html")


def videos_view(request):
    """Video library management"""
    return render(request, "repli/videos.html")


def content_library_view(request):
    """Content library view"""
    return render(request, "repli/content_library.html")


def pricing_view(request):
    """Pricing page"""
    return render(request, "repli/pricing.html")


def help_view(request):
    """Help/support page"""
    return render(request, "repli/help.html")

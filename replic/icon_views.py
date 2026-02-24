"""
Dynamic icon generation for mobile PWA
"""
import re

from django.http import HttpResponse
from django.views.decorators.cache import cache_control


@cache_control(max_age=86400)  # Cache for 1 day
def mobile_icon(request, size):
    """Generate mobile app icons dynamically as SVG"""

    # Extract numeric size
    size_match = re.match(r"icon-(\d+)x(\d+)\.png", size)
    if size_match:
        width = size_match.group(1)
        height = size_match.group(2)
    else:
        width = height = "192"

    # Create SVG icon
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Background gradient -->
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.3"/>
        </filter>
    </defs>
    
    <!-- Background circle -->
    <circle cx="{int(width)//2}" cy="{int(height)//2}" r="{int(width)//2 - 10}" 
            fill="url(#grad)" filter="url(#shadow)"/>
    
    <!-- Magic wand icon -->
    <g transform="translate({int(width)//2}, {int(height)//2})">
        <!-- Wand handle -->
        <line x1="-25" y1="25" x2="-5" y2="5" 
              stroke="white" stroke-width="4" stroke-linecap="round"/>
        
        <!-- Wand tip -->
        <circle cx="-5" cy="5" r="3" fill="white"/>
        
        <!-- Magic sparkles -->
        <g fill="white">
            <circle cx="10" cy="-10" r="2"/>
            <circle cx="20" cy="-5" r="1.5"/>
            <circle cx="15" cy="15" r="1"/>
            <circle cx="25" cy="10" r="1.5"/>
            <circle cx="5" cy="20" r="1"/>
        </g>
        
        <!-- Star sparkle -->
        <g transform="translate(15, -15)" fill="white">
            <path d="M0,-8 L2,0 L8,0 L3,3 L5,8 L0,5 L-5,8 L-3,3 L-8,0 L-2,0 Z"/>
        </g>
    </g>
    
    <!-- App name at bottom -->
    <text x="{int(width)//2}" y="{int(height) - 15}" 
          font-family="Arial, sans-serif" font-size="14" font-weight="bold" 
          text-anchor="middle" fill="white">Repli</text>
</svg>"""

    return HttpResponse(svg_content, content_type="image/svg+xml")


@cache_control(max_age=86400)
def shortcut_icon(request, icon_type):
    """Generate shortcut icons"""

    if icon_type == "shortcut-create.png":
        icon_path = "M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M17,13H13V17H11V13H7V11H11V7H13V11H17V13Z"
        color = "#667eea"
    elif icon_type == "shortcut-library.png":
        icon_path = "M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M10,17L5,12L6.41,10.58L10,14.17L17.59,6.58L19,8L10,17Z"
        color = "#10b981"
    else:
        icon_path = "M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"
        color = "#6366f1"

    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="96" height="96" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="{icon_path}" fill="{color}"/>
</svg>"""

    return HttpResponse(svg_content, content_type="image/svg+xml")

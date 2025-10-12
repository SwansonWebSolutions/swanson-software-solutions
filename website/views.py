from django.shortcuts import render

# Create your views here.

def landing_page(request):
    """Landing page view"""
    return render(request, 'website/landing.html')

def company_page(request):
    """Company page view"""
    return render(request, 'website/company.html')

def contact_sales_page(request):
    """Contact Sales page view"""
    return render(request, 'website/contact_sales.html')

def client_approval_page(request):
    """Client Approval page view"""
    return render(request, 'website/client_approval.html')

def pricing_page(request):
    """Pricing page view"""
    return render(request, 'website/pricing.html')

def seo_page(request):
    """SEO page view"""
    return render(request, 'website/seo.html')

def solutions_page(request):
    """Solutions page view"""
    return render(request, 'website/solutions.html')


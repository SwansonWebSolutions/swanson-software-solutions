from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from .models import DoNotEmailRequest, DoNotCallRequest
# Create your views here.

def index(request):
    """Landing page view"""
    return render(request, 'website/index.html')

def company_page(request):
    """Company page view"""
    return render(request, 'website/company.html')

def services_page(request):
    """Services page view"""
    return render(request, 'website/services.html')

def clients_page(request):
    """Clients page view"""
    return render(request, 'website/clients.html')

def privacy_policy_page(request):
    """Privacy Policy page view"""
    return render(request, 'website/privacy_policy.html')

def terms_of_service_page(request):
    """Terms of Service page view"""
    return render(request, 'website/terms_of_service.html')

def insights_page(request):
    """Insights page view"""
    return render(request, 'website/insights.html')

def shopify_page(request):
    """Shopify Development page view"""
    return render(request, 'website/shopify.html')

def custom_web_dev_page(request):
    """Custom Website Development page view"""
    return render(request, 'website/custom_web_dev.html')

def mobile_app_dev_page(request):
    """Mobile App Development page view"""
    return render(request, 'website/mobile_app_dev.html')

def do_not_call(request):
    """Do Not Call page view"""
    return render(request, 'website/do_not_call.html')

def do_not_email(request):
    """Do Not Email page view"""
    return render(request, 'website/do_not_email.html')

def submit_do_not_call(request):
    """POST endpoint placeholder for Do Not Call submissions.
    Currently no processing; returns the same form page.
    """
    if request.method == 'GET' and request.GET.get('paid') == '1':
        # Bridge page will collect cached values from localStorage and post them here
        return render(request, 'website/checkout_bridge.html', {
            'kind': 'dnc',
            'post_url': reverse('website:submit-do-not-call')
        })
    if request.method == 'POST':
        # Persist after (assumed) payment
        full_name = request.POST.get('full_name', '')
        phone = request.POST.get('phone', '')
        notes = request.POST.get('notes', '')
        DoNotCallRequest.objects.create(
            full_name=full_name,
            phone=phone,
            notes=notes,
            paid_confirmed=True,
        )
        messages.success(request, 'Your Do Not Call request has been received.')
        return render(request, 'website/checkout_success.html')
    return render(request, 'website/do_not_call.html')

def submit_do_not_email(request):
    """POST endpoint placeholder for Do Not Email submissions.
    Currently no processing; returns the same form page.
    """
    if request.method == 'GET' and request.GET.get('paid') == '1':
        # Bridge page will collect cached values from localStorage and post them here
        return render(request, 'website/checkout_bridge.html', {
            'kind': 'dne',
            'post_url': reverse('website:submit-do-not-email')
        })
    if request.method == 'POST':
        # Persist after (assumed) payment
        obj = DoNotEmailRequest.objects.create(
            first_name=request.POST.get('first_name',''),
            last_name=request.POST.get('last_name',''),
            primary_email=request.POST.get('primary_email',''),
            secondary_email=request.POST.get('secondary_email') or None,
            address1=request.POST.get('address1',''),
            address2=request.POST.get('address2') or None,
            city=request.POST.get('city',''),
            region=request.POST.get('region',''),
            postal=request.POST.get('postal',''),
            country=request.POST.get('country','US'),
            notes=request.POST.get('notes') or None,
            paid_confirmed=True,
        )
        messages.success(request, 'Your Do Not Email request has been received.')
        return render(request, 'website/checkout_success.html')
    return render(request, 'website/do_not_email.html')


def do_not_contact_faq_page(request):
    """FAQ page for Do Not Call & Do Not Email services."""
    return render(request, 'website/do_not_contact_faq.html')


def contact_sales_page(request):
    """Contact Sales page view with optional prefilled inquiry via ?inquiry= query.

    Accepts one of the dropdown options:
    - Web Development
    - iOS App Development
    - Shopify
    - Wordpress
    - General Inquiry
    """
    # Normalize and whitelist inquiry prefill from query string
    allowed = {
        'web': 'Web Development',
        'app': 'iOS App Development',
        'shopify': 'Shopify',
        'wordpress': 'Wordpress',
        'general': 'General Inquiry',
    }
    inquiry_param = request.GET.get('inquiry', '')
    inquiry_prefill = allowed.get(inquiry_param.lower().strip(), '') if inquiry_param else ''

    if request.method == 'POST':
        # Parse form data from the request
        name = request.POST.get('name', 'No Name Provided')
        email = request.POST.get('email', 'No Email Provided')
        company = request.POST.get('company', 'No Company Provided')
        phone = request.POST.get('phone', 'No Phone Provided')
        message_body = request.POST.get('message', 'No Message Provided')
        inquiry_type = request.POST.get('inquiry_type', 'General Inquiry')

        # Email details (to you)
        subject = "New Contact Sales Inquiry"
        message = (
            f"You have received a new inquiry from the Contact Sales page.\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Company: {company}\n"
            f"Phone: {phone}\n"
            f"Inquiry Type: {inquiry_type}\n"
            f"Message: {message_body}"
        )
        from_email = "Swanson Technologies <daswanson22@gmail.com>"
        recipient_list = ["daswanson22@gmail.com"]

        # Send notification email to your team
        send_mail(subject, message, from_email, recipient_list)

        # --- Send confirmation email to the user ---
        confirmation_subject = "Thanks for contacting Swanson Software Solutions!"
        context = {
            "name": name,
            "company": company,
            "email": email,
        }
        text_content = render_to_string('emails/contact_confirmation.txt', context)
        html_content = render_to_string('emails/contact_confirmation.html', context)

        confirmation_email = EmailMultiAlternatives(
            confirmation_subject,
            text_content,
            from_email,
            [email],
        )
        confirmation_email.attach_alternative(html_content, "text/html")
        confirmation_email.send()

        messages.success(request, "Your message has been sent! We'll get back to you soon.")
        return render(request, 'website/contact_sales.html', { 'inquiry_prefill': inquiry_prefill })
    return render(request, 'website/contact_sales.html', { 'inquiry_prefill': inquiry_prefill })



from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from .models import DoNotEmailRequest, DoNotCallRequest
from .models import BrokerCompliance
from django.http import HttpResponseBadRequest, Http404
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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
        # Validate required fields
        full_name = (request.POST.get('full_name') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        notes = request.POST.get('notes', '')
        missing = []
        if not full_name:
            missing.append('Full Name')
        if not phone:
            missing.append('Phone')
        # Require agreement to terms/privacy
        ack = (request.POST.get('acknowledge') or '').strip().lower() in ('true','on','1','yes')
        if not ack:
            messages.error(request, 'You must agree to the Terms of Service and Privacy Policy.')
            return render(request, 'website/do_not_call.html')
        if missing:
            for m in missing:
                messages.error(request, f"{m} is required.")
            return render(request, 'website/do_not_call.html')

        # Persist after validation (assumed payment)
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
        # Validate required fields
        data = {k: (request.POST.get(k) or '').strip() for k in [
            'first_name','last_name','primary_email','address1','city','region','postal','country'
        ]}
        missing = [label for key,label in [
            ('first_name','First Name'),('last_name','Last Name'),('primary_email','Primary Email'),
            ('address1','Home Address'),('city','City'),('region','State/Region'),('postal','Postal Code'),('country','Country')
        ] if not data.get(key)]
        email_value = data.get('primary_email')
        if email_value:
            try:
                validate_email(email_value)
            except ValidationError:
                messages.error(request, 'Primary Email is not a valid email address.')
                return render(request, 'website/do_not_email.html')
        ack = (request.POST.get('acknowledge') or '').strip().lower() in ('true','on','1','yes')
        if not ack:
            messages.error(request, 'You must agree to the Terms of Service and Privacy Policy.')
            return render(request, 'website/do_not_email.html')
        if missing:
            for m in missing:
                messages.error(request, f"{m} is required.")
            return render(request, 'website/do_not_email.html')

        # Persist after validation (assumed payment)
        obj = DoNotEmailRequest.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            primary_email=email_value,
            secondary_email=request.POST.get('secondary_email') or None,
            address1=data['address1'],
            address2=request.POST.get('address2') or None,
            city=data['city'],
            region=data['region'],
            postal=data['postal'],
            country=data['country'] or 'US',
            notes=request.POST.get('notes') or None,
            paid_confirmed=True,
        )
        
        # Send follow up email to the user
        subject = "Your Stop My Spam Request Received"
        context = {
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "primary_email": obj.primary_email,
        }
        text_content = render_to_string('emails/do_not_email_confirmation.txt', context)
        html_content = render_to_string('emails/do_not_email_confirmation.html', context)
        from_email = "Stop My Spam <daswanson22@gmail.com>"
        confirmation_email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [obj.primary_email],
        )
        confirmation_email.attach_alternative(html_content, "text/html")
        confirmation_email.send()

        messages.success(request, 'Your Stop My Spam request has been received.')
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


def broker_compliance(request):
    """Display and accept broker compliance confirmations via tokenized link.

    GET: expects ?t=<token>; renders confirmation form if valid.
    POST: accepts token and marks the associated record as submitted.
    """
    token = request.GET.get('t') if request.method == 'GET' else request.POST.get('t')
    if not token:
        return HttpResponseBadRequest('Missing token.')
    try:
        compliance = BrokerCompliance.objects.select_related('broker').get(token=token)
    except BrokerCompliance.DoesNotExist:
        raise Http404('Invalid token.')

    if request.method == 'POST':
        compliance.submitted = True
        compliance.submitted_at = timezone.now()
        compliance.contact_name = request.POST.get('contact_name', '')
        compliance.contact_email = request.POST.get('contact_email', '')
        compliance.notes = request.POST.get('notes', '')
        compliance.save(update_fields=['submitted', 'submitted_at', 'contact_name', 'contact_email', 'notes', 'updated_at'])
        messages.success(request, 'Thank you. Your confirmation has been recorded.')
        return render(request, 'website/broker_compliance_success.html', {
            'broker': compliance.broker,
        })

    return render(request, 'website/broker_compliance.html', {
        'broker': compliance.broker,
        'token': compliance.token,
    })

import re
import re
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import DoNotEmailRequest, DoNotCallRequest, ConsumerBrokerStatus, Consumer, BrokerCompliance
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# Create your views here.


def _normalize_phone(raw: str) -> str | None:
    """Strip non-digits and enforce a 10-digit phone number."""
    digits = re.sub(r"\D", "", raw or "")
    return digits if len(digits) == 10 else None

def _ensure_consumer(email: str, first: str, last: str, phone: str, weekly_opt_in: bool) -> Consumer:
    """Create or update a Consumer (and auth user) for the given email."""
    User = get_user_model()
    user = User.objects.filter(email=email).first()
    if not user:
        # Use email as username; if username field differs, Django will handle the kwarg.
        user_defaults = {"email": email, "first_name": first, "last_name": last}
        user, _ = User.objects.get_or_create(username=email, defaults=user_defaults)
    consumer = Consumer.objects.filter(primary_email=email).first()
    if not consumer:
        consumer = Consumer.objects.create(
            user=user,
            first_name=first,
            last_name=last,
            primary_email=email,
            phone=phone,
            weekly_status_opt_in=weekly_opt_in,
        )
        consumer.initialize_broker_statuses(request_type=ConsumerBrokerStatus.RequestType.DELETE)
    else:
        updated = False
        for field, value in {
            "first_name": first,
            "last_name": last,
            "phone": phone,
            "weekly_status_opt_in": weekly_opt_in,
        }.items():
            if value and getattr(consumer, field) != value:
                setattr(consumer, field, value)
                updated = True
        if updated:
            consumer.save(
                update_fields=["first_name", "last_name", "phone", "weekly_status_opt_in", "updated_at"]
            )
    return consumer

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
        phone_raw = (request.POST.get('phone') or '').strip()
        notes = request.POST.get('notes', '')
        weekly_opt_in = (request.POST.get('weekly_status_opt_in') or '').strip().lower() in ('true','on','1','yes')
        missing = []
        if not full_name:
            missing.append('Full Name')
        phone = _normalize_phone(phone_raw)
        if not phone_raw:
            missing.append('Phone')
        elif not phone:
            messages.error(request, 'Phone must be exactly 10 digits (numbers only).')
            return render(request, 'website/do_not_call.html')
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
            weekly_status_opt_in=weekly_opt_in,
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
            'first_name','last_name','primary_email','primary_phone','address1','city','region','postal','country'
        ]}
        weekly_opt_in = (request.POST.get('weekly_status_opt_in') or '').strip().lower() in ('true','on','1','yes')
        missing = [label for key,label in [
            ('first_name','First Name'),('last_name','Last Name'),('primary_email','Primary Email'),
            ('primary_phone','Primary Phone'),
            ('address1','Home Address'),('city','City'),('region','State/Region'),('postal','Postal Code'),('country','Country')
        ] if not data.get(key)]
        email_value = data.get('primary_email')
        if email_value:
            try:
                validate_email(email_value)
            except ValidationError:
                messages.error(request, 'Primary Email is not a valid email address.')
                return render(request, 'website/do_not_email.html')
        primary_phone = _normalize_phone(data.get('primary_phone'))
        if data.get('primary_phone') and not primary_phone:
            messages.error(request, 'Primary Phone must be exactly 10 digits (numbers only).')
            return render(request, 'website/do_not_email.html')
        secondary_phone_raw = (request.POST.get('secondary_phone') or '').strip()
        secondary_phone = None
        if secondary_phone_raw:
            secondary_phone = _normalize_phone(secondary_phone_raw)
            if not secondary_phone:
                messages.error(request, 'Secondary Phone must be exactly 10 digits (numbers only).')
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
            primary_phone=primary_phone,
            secondary_phone=secondary_phone,
            address1=data['address1'],
            address2=request.POST.get('address2') or None,
            city=data['city'],
            region=data['region'],
            postal=data['postal'],
            country=data['country'] or 'US',
            notes=request.POST.get('notes') or None,
            paid_confirmed=True,
            weekly_status_opt_in=weekly_opt_in,
        )
        # Ensure auth user + consumer exist and are initialized after payment.
        _ensure_consumer(
            email=email_value,
            first=data['first_name'],
            last=data['last_name'],
            phone=primary_phone or "",
            weekly_opt_in=weekly_opt_in,
        )
        
        # Send follow up email to the user
        if weekly_opt_in:
            subject = "Your Stop My Spam Request Received"
            context = {
                "first_name": obj.first_name,
                "last_name": obj.last_name,
                "primary_email": obj.primary_email,
            }

            text_content = render_to_string('emails/do_not_email_confirmation.txt', context)
            html_content = render_to_string('emails/do_not_email_confirmation.html', context)
            from_email = f"Stop My Spam <{getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@swantech.org')}>"
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


def broker_compliance(request, tracking_token=None):
    """Display and accept broker confirmations tied to ConsumerBrokerStatus tokens."""

    if tracking_token:
        token = str(tracking_token)
    else:
        token = request.GET.get('t')
        if request.method == 'POST' and not token:
            token = request.POST.get('t')
    if not token:
        return HttpResponseBadRequest('Missing token.')

    # Tokens from ConsumerBrokerStatus are UUIDs; BrokerCompliance tokens are urlsafe strings.
    status_record = None
    compliance = None
    try:
        uuid.UUID(str(token))
        status_record = get_object_or_404(
            ConsumerBrokerStatus.objects.select_related('consumer', 'broker'),
            tracking_token=token,
        )
    except (ValueError, TypeError):
        status_record = None

    allowed_statuses = {
        ConsumerBrokerStatus.Status.COMPLETED,
        ConsumerBrokerStatus.Status.PROCESSING,
        ConsumerBrokerStatus.Status.REJECTED,
        ConsumerBrokerStatus.Status.NO_RESPONSE,
    }
    if status_record:
        preselected_status = (
            status_record.status if status_record.status in allowed_statuses else ""
        )
    else:
        preselected_status = ""
    status_choices = [
        (value, label)
        for value, label in ConsumerBrokerStatus.Status.choices
        if value in allowed_statuses
    ]

    if status_record is None:
        compliance = get_object_or_404(
            BrokerCompliance.objects.select_related("broker"),
            token=token,
        )
        if request.method == 'POST':
            response_status = request.POST.get('response_status')
            if response_status not in allowed_statuses:
                messages.error(request, 'Please choose a valid status response.')
            else:
                compliance.submitted = True
                compliance.submitted_at = timezone.now()
                compliance.notes = request.POST.get('notes', '')
                compliance.contact_name = request.POST.get('contact_name', '')
                compliance.contact_email = request.POST.get('contact_email', '')
                compliance.save(update_fields=["submitted", "submitted_at", "notes", "contact_name", "contact_email", "updated_at"])
                messages.success(request, 'Thank you. Your confirmation has been recorded.')
                return render(
                    request,
                    'website/broker_compliance_success.html',
                    {
                        'status_record': None,
                        'compliance': compliance,
                    },
                )
        return render(
            request,
            'website/broker_compliance.html',
            {
                'status_record': None,
                'compliance': compliance,
                'status_choices': status_choices,
                'token': token,
                'preselected_status': "",
            },
        )
    else:
        if request.method == 'POST':
            response_status = request.POST.get('response_status')
            if response_status not in allowed_statuses:
                messages.error(request, 'Please choose a valid status response.')
            else:
                status_record.apply_broker_response(
                    response_status,
                    notes=request.POST.get('notes', ''),
                    contact_name=request.POST.get('contact_name', ''),
                    contact_email=request.POST.get('contact_email', ''),
                )
                messages.success(request, 'Thank you. Your confirmation has been recorded.')
                return render(
                    request,
                    'website/broker_compliance_success.html',
                    {
                        'status_record': status_record,
                    },
                )

    return render(
        request,
        'website/broker_compliance.html',
        {
            'status_record': status_record,
            'compliance': None,
            'status_choices': status_choices,
            'token': token,
            'preselected_status': preselected_status,
        },
    )

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render
from django.contrib import messages
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


def contact_sales_page(request):
    """Contact Sales page view"""
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
        return render(request, 'website/contact_sales.html')

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

def custom_web_dev_page(request):
    """Custom Website Development page view"""
    return render(request, 'website/custom_web_dev.html')

def shopify_dev_page(request):
    """Shopify Development page view"""
    return render(request, 'website/shopify_dev.html')

def wordpress_dev_page(request):
    """WordPress Development page view"""
    return render(request, 'website/wordpress_dev.html')

def mobile_app_dev_page(request):
    """Mobile App Development page view"""
    return render(request, 'website/mobile_app_dev.html')

def ccpa_compliance_page(request):
    """CCPA & Do-Not-Call Registration page view"""
    return render(request, 'website/ccpa_compliance.html')


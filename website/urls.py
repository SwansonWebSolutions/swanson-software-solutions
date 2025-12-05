from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('company/', views.company_page, name='company'),
    path('clients/', views.clients_page, name='clients'),
    path('services/', views.services_page, name='services'),
    path('contact/', views.contact_sales_page, name='contact'),
    path('insights/', views.insights_page, name='insights'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter-subscribe'),
    path('manage-preferences/', views.manage_preferences, name='manage-preferences'),
    # New Stop My Spam routes (preserve existing URL names for compatibility)
    path('stop-my-spam/', views.do_not_email, name='do-not-email'),
    path('stop-my-spam/submit/', views.submit_do_not_email, name='submit-do-not-email'),
    # Redirect legacy routes to new slugs
    path('do-not-email-me/', RedirectView.as_view(url='/stop-my-spam/', permanent=True)),
    path('do-not-email-me/submit/', RedirectView.as_view(url='/stop-my-spam/submit/', permanent=True)),
    path('faq/', views.do_not_contact_faq_page, name='faq'),
    path('privacy/', views.privacy_policy_page, name='privacy'),
    path('terms/', views.terms_of_service_page, name='terms'),
    path('broker-compliance/<uuid:tracking_token>/', views.broker_compliance, name='broker-compliance-token'),
    path('broker-compliance/', views.broker_compliance, name='broker-compliance'),
    path(
        'locations/<slug:state_slug>/<slug:city_slug>/web-development/',
        views.location_web_development,
        name='location-web-development',
    ),
    path(
        'locations/<slug:state_slug>/<slug:city_slug>/ios-app-development/',
        views.location_ios_app,
        name='location-ios-app',
    ),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
]

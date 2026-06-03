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
    path('book-consultation/', views.book_consultation, name='book-consultation'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter-subscribe'),
    path('manage-preferences/', views.manage_preferences, name='manage-preferences'),
    path('faq/', views.do_not_contact_faq_page, name='faq'),
    path('privacy/', views.privacy_policy_page, name='privacy'),
    path('terms/', views.terms_of_service_page, name='terms'),
    path(
        'locations/<slug:state_slug>/<slug:city_slug>/ios-app-development/',
        views.location_ios_app,
        name='location-ios-app',
    ),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
]

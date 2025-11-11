from django.urls import path
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('company/', views.company_page, name='company'),
    path('clients/', views.clients_page, name='clients'),
    path('contact/', views.contact_sales_page, name='contact'),
    path('client-approval/', views.client_approval_page, name='client_approval'),
    path('insights/', views.insights_page, name='insights'),
    path('shopify/', views.shopify_page, name='shopify'),
    path('pricing/', views.pricing_page, name='pricing'),
    path('custom-website-development/', views.custom_web_dev_page, name='custom_website'),
    path('wordpress/', views.wordpress_dev_page, name='wordpress'),
    path('mobile-app-development/', views.mobile_app_dev_page, name='ios_apps'),
    path('do-not-call-me/', views.do_not_call, name='do-not-call'),
    path('do-not-email-me/', views.do_not_email, name='do-not-email'),
    path('seo/', views.seo_page, name='seo'),
    path('services/', views.services_page, name='services'),
    path('privacy/', views.privacy_policy_page, name='privacy'),
    path('terms/', views.terms_of_service_page, name='terms'),
    path('services/custom-website-development/', views.custom_web_dev_page, name='custom_web_dev'),
    path('services/shopify-development/', views.shopify_dev_page, name='shopify_dev'),
    path('services/wordpress-development/', views.wordpress_dev_page, name='wordpress_dev'),
    path('services/mobile-app-development/', views.mobile_app_dev_page, name='mobile_app_dev'),
    path('services/ccpa-compliance/', views.ccpa_compliance_page, name='ccpa_compliance'),
]

from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('company/', views.company_page, name='company'),
    path('contact-sales/', views.contact_sales_page, name='contact_sales'),
    path('client-approval/', views.client_approval_page, name='client_approval'),
    path('pricing/', views.pricing_page, name='pricing'),
    path('seo/', views.seo_page, name='seo'),
    path('solutions/', views.solutions_page, name='solutions'),
    path('services/custom-website-development/', views.custom_web_dev_page, name='custom_web_dev'),
    path('services/shopify-development/', views.shopify_dev_page, name='shopify_dev'),
    path('services/wordpress-development/', views.wordpress_dev_page, name='wordpress_dev'),
    path('services/mobile-app-development/', views.mobile_app_dev_page, name='mobile_app_dev'),
    path('services/ccpa-compliance/', views.ccpa_compliance_page, name='ccpa_compliance'),
]

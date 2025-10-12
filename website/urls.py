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
]

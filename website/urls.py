from django.urls import path
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('company/', views.company_page, name='company'),
    path('clients/', views.clients_page, name='clients'),
    path('contact/', views.contact_sales_page, name='contact'),
    path('insights/', views.insights_page, name='insights'),
    path('do-not-call-me/', views.do_not_call, name='do-not-call'),
    path('do-not-call-me/submit/', views.submit_do_not_call, name='submit-do-not-call'),
    path('do-not-email-me/', views.do_not_email, name='do-not-email'),
    path('do-not-email-me/submit/', views.submit_do_not_email, name='submit-do-not-email'),
    path('faq/', views.do_not_contact_faq_page, name='faq'),
    path('privacy/', views.privacy_policy_page, name='privacy'),
    path('terms/', views.terms_of_service_page, name='terms'),
]

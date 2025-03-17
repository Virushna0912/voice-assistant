from django.urls import path
from assistant import views


    
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_signup_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('index/', views.index, name='index'),  # Fixed URL pattern
    path('about/', views.about_view, name='about'),
    path('service/', views.service_view, name='service'),
    path('process_voice/', views.process_voice, name='process_voice'),
]
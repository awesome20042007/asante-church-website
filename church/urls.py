from django.urls import path

from . import views
from .views import robots_txt

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('leadership/', views.leadership, name='leadership'),
    path('ministries/', views.ministries, name='ministries'),
    path('services/', views.services, name='services'),
    path('events/', views.events, name='events'),
    path('sermons/', views.sermons, name='sermons'),
    path('gallery/', views.gallery, name='gallery'),
    path('give/', views.give, name='give'),
    path('contact/', views.contact, name='contact'),
        path('robots.txt', robots_txt, name='robots_txt'),
]
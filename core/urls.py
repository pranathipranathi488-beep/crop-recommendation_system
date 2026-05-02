from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('calendar', views.calendar, name='calendar'),
    path('schemes', views.schemes, name='schemes'),
    path('news', views.news, name='news'),
    path('about', views.about, name='about'),
    path('help', views.help_page, name='help'),
    path('signup', views.signup_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('recommend', views.recommend, name='recommend'),
    path('predict', views.predict, name='predict'),
    path('contact', views.contact, name='contact'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('farmer/register', views.register_farmer, name='register_farmer'),
    path('farmer/dashboard/<int:farmer_id>', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/update/<int:farmer_id>', views.update_farmer, name='update_farmer'),
    path('marketplace', views.marketplace, name='marketplace'),
]

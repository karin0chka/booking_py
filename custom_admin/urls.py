from django.urls import path
from . import views

urlpatterns = [
    # ... other URL patterns ...
    path('', views.dashboard_view, name='custom_admin'),
    path('login/', views.login_view,name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_allowance/', views.update_allowance, name='update_allowance'),
    path('create_allowance/', views.create_allowance, name='create_allowance'),
    path('new_admin_feedback/', views.new_admin_feedback, name='new_admin_feedback')
]
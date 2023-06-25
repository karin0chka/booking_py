from django.urls import path
from . import views

urlpatterns = [
    # ... other URL patterns ...
    path('', views.dashboard_view, name='custom_admin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_allowance/', views.update_allowance, name='update_allowance'),
    path('create_allowance/', views.create_allowance, name='create_allowance'),
    path('new_admin_feedback/', views.new_admin_feedback,
         name='new_admin_feedback'),
    path('return_csv_report/', views.return_ticket_csv_report, name='return_csv_report'),
    path('return_all_report/', views.return_all_report, name='return_all_report'),
]

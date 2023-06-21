from django.urls import path
from . import views


#snippet id defining the URL pattern 
#map specific URLs to corresponding views in app 'views.py'
urlpatterns=[
    path('', views.home, name='home'),
    path('ticket/<str:booking_id>/', views.booked_ticket ),
    path('feedback/<str:booking_id>/', views.feedback, name='feedback'),
    path('ticket/new/', views.newTicket ),
    path('discount/', views.discount )

]

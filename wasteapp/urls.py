from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name="dashboard"),

    path('producer/', views.producer_page, name="producer_page"),

    path('consumer/', views.consumer_page, name="consumer_page"),

    path('request/<int:id>/', views.request_waste, name="request"),

]
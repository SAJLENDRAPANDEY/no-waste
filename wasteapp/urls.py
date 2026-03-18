from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    # ── Public ──────────────────────────────
    path('',           views.landing,     name="landing"),
    path('dashboard/', views.dashboard,   name="dashboard"),
    path('login/',     views.login_view,  name="login"),       # ✅ custom login view
    path('signup/',    views.signup,      name="signup"),
    path('logout/',    LogoutView.as_view(next_page='login'), name='logout'),

    # ── Producer ────────────────────────────
    path('producer/',  views.producer_page,   name="producer_page"),
    path('add-waste/', views.add_waste,       name="add_waste"),
    path('approve/<int:id>/', views.approve_request, name="approve_request"),
    path('reject/<int:id>/',  views.reject_request,  name="reject_request"),

    # ── Consumer ────────────────────────────
    path('consumer/',         views.consumer_page,  name="consumer_page"),
    path('request/<int:id>/', views.request_waste,  name="request"),
    path('add-request/',      views.add_requirement, name="add_requirement"),

    # ── Common ──────────────────────────────
    path('profile/', views.profile, name='profile'),

    # path("smart-match/", views.smart_match_page, name="smart_match_page"),
    # path("api/smart-match/", views.smart_match_api, name="smart_match"),
    path('smart-match/', views.smart_match_page),
    path('api/smart-match/', views.smart_match_api),
    path('request/', views.request_page, name='request_page'), 
]

from django.urls import path

from . import views

urlpatterns = [
    path("poll/<str:id>", views.PollView.as_view(), name="poll"),
    path("login", views.LoginView.as_view(), name="login"),
    path("signup", views.SignUpView.as_view(), name="signup"),
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/delete/<str:id>", views.DashboardView.as_view(), name="dashboard"),
]

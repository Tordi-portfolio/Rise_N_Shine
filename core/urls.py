from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("areas/", views.areas, name="areas"),
    path("faq/", views.faq, name="faq"),
    path("quote/", views.quote, name="quote"),
    path("thank-you/", views.thank_you, name="thank_you"),

    # Staff area. Everything except the login page requires a staff account.
    path("staff/login/", views.StaffLoginView.as_view(), name="staff_login"),
    path("staff/logout/", LogoutView.as_view(), name="staff_logout"),
    path("staff/", views.dashboard, name="staff_dashboard"),
    path("staff/responses/", views.response_list, name="staff_responses"),
    path("staff/responses/export/", views.response_export, name="staff_export"),
    path("staff/responses/<int:pk>/", views.response_detail, name="staff_response_detail"),
    path("staff/responses/<int:pk>/delete/", views.response_delete, name="staff_response_delete"),
]

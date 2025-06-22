from django.urls import path
from . import views

app_name = "support"

urlpatterns = [
    path("faq/", views.faq, name="faq"),
    path("tutorial/", views.tutorial, name="tutorial"),
    path("chatbot/", views.chatbot, name="chatbot"),   # GEMS AI route
]

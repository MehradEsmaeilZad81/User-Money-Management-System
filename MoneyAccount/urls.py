from django.urls import path, include
from .views import GeneralSourceView

urlpatterns = [
    path('generalsources', GeneralSourceView.as_view()),
]